import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ContractSendWizard(models.TransientModel):
    _name = 'contract.send.wizard'
    _description = "Contract Send Wizard"

    contract_id = fields.Many2one(
        'contract.contract',
        string='Contract',
        required=True,
        readonly=True,
    )
    partner_email = fields.Char(string='Recipient Email')
    cc_email = fields.Char(string='Copy (CC)', help='Addresses separated by commas')
    subject = fields.Char(string='Subject')
    body = fields.Html(string='Message')
    attach_pdf = fields.Boolean(string='Attach Contract PDF', default=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        contract_id = self.env.context.get('default_contract_id')
        if contract_id:
            contract = self.env['contract.contract'].browse(contract_id)
            res['partner_email'] = contract.partner_id.email or ''

            template = self.env.ref(
                'smart_contract_lifecycle.mail_template_contract_send',
                raise_if_not_found=False,
            )
            if template:
                rendered = template._render_field(
                    'subject', [contract.id], compute_lang=True,
                )
                res['subject'] = rendered.get(contract.id) or (
                    _('Contract %s — %s') % (contract.name, contract.title)
                )
                rendered_body = template._render_field(
                    'body_html', [contract.id], compute_lang=True,
                )
                res['body'] = rendered_body.get(contract.id) or ''
            else:
                res['subject'] = _('Contract %s — %s') % (contract.name, contract.title)
                res['body'] = _('''
<p>Hello,</p>
<p>Please find attached the contract <strong>%s</strong>.</p>
<p>Kindly return this signed document to us as soon as possible.</p>
<p>Best regards,<br/><strong>%s</strong></p>
                ''') % (contract.title, contract.user_id.name or '')
        return res

    def action_send(self):
        self.ensure_one()
        contract = self.contract_id

        if not self.partner_email:
            raise UserError(_("The recipient's email address is required."))

        attachment_ids = []

        if self.attach_pdf:
            report = self.env.ref('smart_contract_lifecycle.action_report_contract')
            pdf_content, report_format = report._render_qweb_pdf([contract.id])
            attachment = self.env['ir.attachment'].create({
                'name': 'Contract_%s.pdf' % contract.name,
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'res_model': 'contract.contract',
                'res_id': contract.id,
                'mimetype': 'application/pdf',
            })
            attachment_ids.append(attachment.id)

        mail_values = {
            'email_to': self.partner_email,
            'email_cc': self.cc_email or '',
            'subject': self.subject,
            'body_html': self.body,
            'attachment_ids': [(4, att_id) for att_id in attachment_ids],
            'model': 'contract.contract',
            'res_id': contract.id,
            'auto_delete': True,
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()

        contract.message_post(
            body=_('Contract sent by <strong>%s</strong> to %s on %s.') % (
                self.env.user.name,
                self.partner_email,
                fields.Date.today(),
            ),
            message_type='comment',
            subtype_xmlid='mail.mt_note',
        )
        return {'type': 'ir.actions.act_window_close'}
