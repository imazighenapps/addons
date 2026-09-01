# -*- coding: utf-8 -*-
from odoo import fields, models


class EduflowFeeType(models.Model):
    _name = 'eduflow.fee.type'
    _description = "Fee Type scolaire"
    _order = 'name'

    name = fields.Char(string="Label", required=True, help="E.g. Registration, Tuition, Transport")
    amount = fields.Monetary(string="Default Amount", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    level_id = fields.Many2one('eduflow.level', string="Level")
    year_id = fields.Many2one('eduflow.academic.year', string="Academic Year")
    student_type = fields.Selection([
        ('all', 'All Students'),
        ('new', 'New Students'),
        ('renewal', 'Re-enrollments'),
    ], string="Student Type", default='all')
    company_id = fields.Many2one('res.company', string="Institution",
                                  default=lambda self: self.env.company)

    # F1.1 -- accounting configuration used when generating a customer
    # invoice from a fee of this type (eduflow.fee.action_create_invoice).
    account_id = fields.Many2one(
        'account.account', string="Revenue Account",
        domain="[('deprecated', '=', False)]",
        help="Income account used on the invoice line. If left empty, the "
             "product/company default income account is used.")
    journal_id = fields.Many2one(
        'account.journal', string="Sales Journal",
        domain="[('type', '=', 'sale')]",
        help="Journal used to post invoices generated from this fee type. "
             "If left empty, the company's default sales journal is used.")
    tax_ids = fields.Many2many(
        'account.tax', string="Taxes",
        domain="[('type_tax_use', '=', 'sale')]",
        help="Taxes applied on the invoice line generated for this fee type.")
