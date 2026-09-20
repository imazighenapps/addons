from odoo import _


DEFAULT_RULES = [
    ('purchase.order', 'Purchase Vendor Confirmation Overdue', "[('state', 'in', ['sent', 'purchase']), ('date_planned', '<', 'today')]", 'delay', 'high', 'date_planned'),
    ('purchase.order', 'Purchase Delivery Overdue', "[('state', '=', 'purchase'), ('date_planned', '<', 'today-1d')]", 'delay', 'high', 'date_planned'),
    ('purchase.order', 'High Value Purchase Delay', "[('state', '=', 'purchase'), ('date_planned', '<', 'today'), ('amount_total', '>=', 10000)]", 'business_risk', 'high', 'date_planned'),
    ('purchase.order', 'RFQ Awaiting Vendor Response', "[('state', '=', 'sent'), ('date_order', '<', 'today-3d')]", 'stagnation', 'medium', 'date_order'),
    ('sale.order', 'Sales Delivery Commitment At Risk', "[('state', '=', 'sale'), ('commitment_date', '<', 'today')]", 'deadline_risk', 'high', 'commitment_date'),
    ('sale.order', 'Overdue Sales Delivery', "[('state', '=', 'sale'), ('commitment_date', '<', 'today-1d')]", 'delay', 'high', 'commitment_date'),
    ('sale.order', 'High Value Sales Order At Risk', "[('state', '=', 'sale'), ('commitment_date', '<', 'today'), ('amount_total', '>=', 10000)]", 'business_risk', 'critical', 'commitment_date'),
    ('sale.order', 'Quotation Stagnation', "[('state', 'in', ['draft', 'sent']), ('date_order', '<', 'today-7d')]", 'stagnation', 'medium', 'date_order'),
    ('stock.picking', 'Inventory Transfer Delay', "[('state', 'in', ['waiting', 'confirmed', 'assigned']), ('scheduled_date', '<', 'today')]", 'delay', 'high', 'scheduled_date'),
    ('stock.picking', 'Inventory Transfer Critical Delay', "[('state', 'in', ['waiting', 'confirmed']), ('scheduled_date', '<', 'today-3d')]", 'deadline_risk', 'critical', 'scheduled_date'),
    ('stock.picking', 'Receipt Overdue', "[('picking_type_code', '=', 'incoming'), ('state', 'not in', ['done', 'cancel']), ('scheduled_date', '<', 'today')]", 'delay', 'high', 'scheduled_date'),
    ('stock.move', 'Stock Move Waiting Too Long', "[('state', 'in', ['waiting', 'confirmed']), ('date', '<', 'today-2d')]", 'dependency', 'high', 'date'),
    ('mrp.production', 'Manufacturing Order Delay', "[('state', 'in', ['confirmed', 'progress']), ('date_start', '<', 'today')]", 'delay', 'high', 'date_start'),
    ('mrp.production', 'Manufacturing Order Critical Delay', "[('state', 'in', ['confirmed', 'progress']), ('date_start', '<', 'today-2d')]", 'deadline_risk', 'critical', 'date_start'),
    ('mrp.production', 'Manufacturing Component Risk', "[('state', 'in', ['confirmed', 'progress']), ('reservation_state', 'in', ['waiting', 'partially_available'])]", 'dependency', 'high', 'date_start'),
    ('account.move', 'Overdue Customer Invoice', "[('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('payment_state', '!=', 'paid'), ('invoice_date_due', '<', 'today')]", 'business_risk', 'high', 'invoice_date_due'),
    ('account.move', 'High Value Overdue Invoice', "[('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('payment_state', '!=', 'paid'), ('invoice_date_due', '<', 'today'), ('amount_residual', '>=', 10000)]", 'business_risk', 'critical', 'invoice_date_due'),
    ('crm.lead', 'Opportunity Stagnation', "[('type', '=', 'opportunity'), ('active', '=', True), ('probability', '<', 100), ('write_date', '<', 'now-7d')]", 'stagnation', 'medium', 'write_date'),
    ('crm.lead', 'High Value Opportunity Stagnation', "[('type', '=', 'opportunity'), ('active', '=', True), ('probability', '<', 100), ('expected_revenue', '>=', 10000), ('write_date', '<', 'now-3d')]", 'business_risk', 'high', 'write_date'),
    ('crm.lead', 'Lead Without Recent Follow-up', "[('type', '=', 'lead'), ('active', '=', True), ('write_date', '<', 'now-7d')]", 'missing_action', 'medium', 'write_date'),
]


def sync_default_rules(env):
    Rule = env['smart.operations.rule']
    IrModel = env['ir.model']
    for index, (model_name, name, domain, issue_type, severity, date_field) in enumerate(DEFAULT_RULES, start=10):
        model = IrModel.search([('model', '=', model_name)], limit=1)
        if not model or Rule.search([('name', '=', name)], limit=1):
            continue
        Rule.create({
            'name': _(name),
            'sequence': index,
            'model_id': model.id,
            'domain': domain,
            'rule_issue_type': issue_type,
            'severity': severity,
            'date_field': date_field,
            'action_create_activity': True,
            'activity_due_hours': 24.0,
            'risk_weight': 5.0,
        })


def post_init_hook(env):
    sync_default_rules(env)
