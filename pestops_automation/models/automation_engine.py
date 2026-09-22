from datetime import timedelta

from odoo import api, fields, models, _


class PestAutomationEngine(models.AbstractModel):
    _name = 'pest.automation.engine'
    _description = 'PestOps Automation Engine'

    def _activity_type(self):
        return self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)

    def _ir_model_id(self, model_name):
        return self.env['ir.model']._get_id(model_name)

    def _log_exists(self, key):
        return bool(self.env['pest.automation.log'].search_count([('key', '=', key)]))

    def _create_activity(self, model_name, record, user, summary, note, deadline=None):
        if not record or not user:
            return False
        activity_type = self._activity_type()
        if not activity_type:
            return False
        Activity = self.env['mail.activity'].sudo()
        domain = [
            ('res_model', '=', model_name),
            ('res_id', '=', record.id),
            ('activity_type_id', '=', activity_type.id),
            ('summary', '=', summary),
            ('user_id', '=', user.id),
        ]
        if Activity.search_count(domain):
            return False
        Activity.create({
            'activity_type_id': activity_type.id,
            'res_model_id': self._ir_model_id(model_name),
            'res_id': record.id,
            'user_id': user.id,
            'summary': summary,
            'note': note,
            'date_deadline': deadline or fields.Date.context_today(self),
        })
        return True

    def _send_customer_mail(self, partner, subject, body_html):
        if not partner or not partner.email:
            return False
        mail = self.env['mail.mail'].sudo().create({
            'subject': subject,
            'body_html': body_html,
            'email_to': partner.email,
            'auto_delete': True,
        })
        mail.send()
        return True

    def _run_company(self, config):
        now = fields.Datetime.now()
        today = fields.Date.context_today(self)
        Log = self.env['pest.automation.log'].sudo()

        Visit = self.env['pest.visit'].with_company(config.company_id)
        reminder_limit = now + timedelta(hours=config.visit_reminder_hours)
        upcoming = Visit.search([
            ('company_id', '=', config.company_id.id),
            ('state', '=', 'scheduled'),
            ('scheduled_start', '>=', now),
            ('scheduled_start', '<=', reminder_limit),
            ('technician_id', '!=', False),
        ])
        for visit in upcoming:
            key = 'visit_reminder:%s:%s' % (visit.id, fields.Datetime.to_string(visit.scheduled_start))
            if self._log_exists(key):
                continue
            activity = self._create_activity(
                'pest.visit',
                visit,
                visit.technician_id,
                _('Upcoming PestOps Visit'),
                _('Visit %s is scheduled for %s at %s.') % (
                    visit.name,
                    visit.site_id.display_name,
                    fields.Datetime.context_timestamp(self, visit.scheduled_start).strftime('%Y-%m-%d %H:%M'),
                ),
                deadline=visit.scheduled_start.date(),
            )
            email_sent = False
            customer = visit.site_id.partner_id.commercial_partner_id
            if config.customer_notifications and config.customer_visit_reminders:
                email_sent = self._send_customer_mail(
                    customer,
                    _('PestOps visit reminder - %s') % visit.name,
                    _('Your PestOps visit <strong>%s</strong> is scheduled for <strong>%s</strong>.') % (
                        visit.name,
                        fields.Datetime.context_timestamp(self, visit.scheduled_start).strftime('%Y-%m-%d %H:%M'),
                    ),
                )
            Log.create({
                'name': _('Upcoming visit - %s') % visit.name,
                'key': key,
                'event_type': 'visit_reminder',
                'company_id': config.company_id.id,
                'user_id': visit.technician_id.id,
                'partner_id': customer.id,
                'res_model': 'pest.visit',
                'res_id': visit.id,
                'record_display_name': visit.display_name,
                'email_sent': email_sent,
                'activity_created': activity,
                'note': _('Automated upcoming visit reminder.'),
            })

        if config.overdue_visit_enabled:
            overdue = Visit.search([
                ('company_id', '=', config.company_id.id),
                ('state', '=', 'scheduled'),
                ('scheduled_start', '<', now),
                ('technician_id', '!=', False),
            ], limit=500)
            for visit in overdue:
                key = 'visit_overdue:%s:%s' % (visit.id, fields.Datetime.to_string(visit.scheduled_start))
                if self._log_exists(key):
                    continue
                user = visit.technician_id or config.escalation_user_id
                activity = self._create_activity(
                    'pest.visit', visit, user,
                    _('Overdue PestOps Visit'),
                    _('Visit %s was scheduled for %s and is still not started.') % (
                        visit.name,
                        fields.Datetime.context_timestamp(self, visit.scheduled_start).strftime('%Y-%m-%d %H:%M'),
                    ),
                    deadline=today,
                )
                Log.create({
                    'name': _('Overdue visit - %s') % visit.name,
                    'key': key,
                    'event_type': 'visit_overdue',
                    'company_id': config.company_id.id,
                    'user_id': user.id,
                    'partner_id': visit.site_id.partner_id.commercial_partner_id.id,
                    'res_model': 'pest.visit',
                    'res_id': visit.id,
                    'record_display_name': visit.display_name,
                    'activity_created': activity,
                    'note': _('Automated overdue visit escalation.'),
                })

        Contract = self.env['pest.contract'].with_company(config.company_id)
        renewal_limit = today + timedelta(days=config.contract_renewal_days)
        contracts = Contract.search([
            ('company_id', '=', config.company_id.id),
            ('state', '=', 'confirmed'),
            ('end_date', '!=', False),
            ('end_date', '>=', today),
            ('end_date', '<=', renewal_limit),
        ])
        for contract in contracts:
            key = 'contract_renewal:%s:%s' % (contract.id, contract.end_date)
            if self._log_exists(key):
                continue
            user = contract.responsible_id or config.escalation_user_id
            activity = self._create_activity(
                'pest.contract', contract, user,
                _('Contract Renewal Due'),
                _('Contract %s expires on %s. Prepare the renewal action.') % (
                    contract.display_name, contract.end_date,
                ),
                deadline=contract.end_date,
            )
            email_sent = False
            customer = contract.partner_id.commercial_partner_id
            if config.customer_notifications and config.customer_contract_renewals:
                email_sent = self._send_customer_mail(
                    customer,
                    _('PestOps contract renewal - %s') % contract.display_name,
                    _('Your PestOps contract <strong>%s</strong> reaches its end date on <strong>%s</strong>.') % (
                        contract.display_name, contract.end_date,
                    ),
                )
            Log.create({
                'name': _('Contract renewal - %s') % contract.display_name,
                'key': key,
                'event_type': 'contract_renewal',
                'company_id': config.company_id.id,
                'user_id': user.id,
                'partner_id': customer.id,
                'res_model': 'pest.contract',
                'res_id': contract.id,
                'record_display_name': contract.display_name,
                'email_sent': email_sent,
                'activity_created': activity,
                'note': _('Automated contract renewal reminder.'),
            })

        Anomaly = self.env['pest.anomaly'].with_company(config.company_id)
        anomaly_limit = today - timedelta(days=config.overdue_anomaly_grace_days)
        anomalies = Anomaly.search([
            ('site_id.company_id', '=', config.company_id.id),
            ('state', 'in', ('open', 'in_progress')),
            ('due_date', '!=', False),
            ('due_date', '<', anomaly_limit),
        ])
        for anomaly in anomalies:
            key = 'anomaly_overdue:%s:%s' % (anomaly.id, anomaly.due_date)
            if self._log_exists(key):
                continue
            user = anomaly.assigned_user_id or anomaly.technician_id or config.escalation_user_id
            activity = self._create_activity(
                'pest.anomaly', anomaly, user,
                _('Overdue PestOps Anomaly'),
                _('Anomaly %s is overdue since %s. Severity: %s.') % (
                    anomaly.display_name, anomaly.due_date, dict(anomaly._fields['severity'].selection).get(anomaly.severity, anomaly.severity),
                ),
                deadline=today,
            )
            Log.create({
                'name': _('Overdue anomaly - %s') % anomaly.display_name,
                'key': key,
                'event_type': 'anomaly_overdue',
                'company_id': config.company_id.id,
                'user_id': user.id,
                'partner_id': anomaly.site_id.partner_id.commercial_partner_id.id if anomaly.site_id else False,
                'res_model': 'pest.anomaly',
                'res_id': anomaly.id,
                'record_display_name': anomaly.display_name,
                'activity_created': activity,
                'note': _('Automated overdue anomaly escalation.'),
            })

        if config.stock_alert_enabled and 'pest.stock.threshold' in self.env:
            thresholds = self.env['pest.stock.threshold'].with_company(config.company_id).search([
                ('active', '=', True),
                ('status', 'in', ('low', 'out')),
            ])
            for threshold in thresholds:
                if not threshold.alert_open:
                    continue
                key = 'stock_alert:%s:%s' % (threshold.id, threshold.last_alert_at or fields.Datetime.now())
                if Log.search_count([('res_model', '=', 'pest.stock.threshold'), ('res_id', '=', threshold.id), ('event_type', '=', 'stock_alert'), ('email_sent', '=', False), ('key', 'like', 'stock_alert:%s:' % threshold.id)]):
                    continue
                activity = self._create_activity(
                    'pest.stock.threshold', threshold,
                    threshold.responsible_user_id or config.escalation_user_id,
                    _('PestOps Stock Alert'),
                    _('Product %s is at status %s. Current quantity: %s.') % (
                        threshold.product_id.display_name,
                        dict(threshold._fields['status'].selection).get(threshold.status, threshold.status),
                        threshold.current_qty,
                    ),
                    deadline=today,
                )
                Log.create({
                    'name': _('Stock alert - %s') % threshold.product_id.display_name,
                    'key': key,
                    'event_type': 'stock_alert',
                    'company_id': config.company_id.id,
                    'user_id': (threshold.responsible_user_id or config.escalation_user_id).id,
                    'res_model': 'pest.stock.threshold',
                    'res_id': threshold.id,
                    'record_display_name': threshold.display_name,
                    'activity_created': activity,
                    'note': _('Automated stock alert escalation.'),
                })

        self._process_customer_events(config)

    def _process_customer_events(self, config):
        Log = self.env['pest.automation.log'].sudo()
        cutoff = fields.Datetime.now() - timedelta(days=2)
        if 'pest.service.request' in self.env and config.customer_notifications and config.customer_service_requests:
            requests = self.env['pest.service.request'].with_company(config.company_id).search([
                ('company_id', '=', config.company_id.id),
                ('create_date', '>=', cutoff),
            ])
            for request in requests:
                key = 'service_request:%s' % request.id
                if Log.search_count([('key', '=', key)]):
                    continue
                email_sent = self._send_customer_mail(
                    request.partner_id.commercial_partner_id,
                    _('PestOps service request received - %s') % request.name,
                    _('We received your PestOps service request <strong>%s</strong>.') % request.name,
                )
                activity = self._create_activity(
                    'pest.service.request', request,
                    config.service_request_responsible_id,
                    _('New PestOps Service Request'),
                    _('Customer submitted request %s: %s') % (request.name, request.description or ''),
                )
                Log.create({
                    'name': _('Service request - %s') % request.name,
                    'key': key,
                    'event_type': 'service_request',
                    'company_id': config.company_id.id,
                    'user_id': config.service_request_responsible_id.id,
                    'partner_id': request.partner_id.commercial_partner_id.id,
                    'res_model': 'pest.service.request',
                    'res_id': request.id,
                    'record_display_name': request.display_name,
                    'email_sent': email_sent,
                    'activity_created': activity,
                    'note': _('Automated customer request notification.'),
                })

        if 'pest.portal.document' in self.env and config.customer_notifications and config.customer_portal_documents:
            documents = self.env['pest.portal.document'].with_company(config.company_id).search([
                ('company_id', '=', config.company_id.id),
                ('published', '=', True),
                ('published_at', '>=', cutoff),
            ])
            for document in documents:
                key = 'portal_document:%s' % document.id
                if Log.search_count([('key', '=', key)]):
                    continue
                email_sent = self._send_customer_mail(
                    document.partner_id.commercial_partner_id,
                    _('PestOps document available - %s') % document.name,
                    _('A new PestOps document <strong>%s</strong> is now available in your customer portal.') % document.name,
                )
                Log.create({
                    'name': _('Portal document - %s') % document.name,
                    'key': key,
                    'event_type': 'portal_document',
                    'company_id': config.company_id.id,
                    'partner_id': document.partner_id.commercial_partner_id.id,
                    'res_model': 'pest.portal.document',
                    'res_id': document.id,
                    'record_display_name': document.display_name,
                    'email_sent': email_sent,
                    'note': _('Automated published-document customer notification.'),
                })

    @api.model
    def cron_run(self):
        Config = self.env['pest.automation.config'].sudo()
        for config in Config.search([('active', '=', True)]):
            self.with_company(config.company_id)._run_company(config)
        return True
