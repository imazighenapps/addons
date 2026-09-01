# -*- coding: utf-8 -*-
from odoo import fields, models


class EduflowParent(models.Model):
    _name = 'eduflow.parent'
    _description = "Parent / Legal Guardian"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string="Full Name", required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string="Related Contact",
                                  help="Related Odoo contact (portal, invoicing, email).")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    address = fields.Char(string="Address")
    profession = fields.Char(string="Profession")
    student_rel_ids = fields.One2many('eduflow.student.parent.rel', 'parent_id',
                                       string="Enfants")
    student_ids = fields.Many2many('eduflow.student', string="Enfants (liste)",
                                    compute='_compute_student_ids')
    portal_access = fields.Boolean(string="Portal Access Enabled", default=False)

    def _compute_student_ids(self):
        for rec in self:
            rec.student_ids = rec.student_rel_ids.mapped('student_id')

    def action_grant_portal_access(self):
        """Create the related contact if necessary and mark portal access as enabled.
        L'envoi effectif de l'invitation portail se fait ensuite depuis la fiche contact
        (button Actions > Grant Portal Access), in accordance with Odoo standard.
        If a portal user already exists for this contact (case of re-granting
        access or different operation order), we directly synchronize
        the business group here rather than waiting for a new event on res.users."""
        group = self.env.ref('eduflow.group_eduflow_parent_portal', raise_if_not_found=False)
        for rec in self:
            if not rec.partner_id:
                rec.partner_id = self.env['res.partner'].create({
                    'name': rec.name,
                    'email': rec.email,
                    'phone': rec.phone,
                })
            rec.portal_access = True
            if group and rec.partner_id.user_ids:
                rec.partner_id.user_ids.sudo().write({'groups_id': [(4, group.id)]})
