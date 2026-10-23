# -*- coding: utf-8 -*-
from odoo import fields, models


class RmaReason(models.Model):
    _name = "rma.reason"
    _description = "RMA Return Reason"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    rtype = fields.Selection(
        [("withdrawal", "Withdrawal 14d"), ("warranty", "Legal Warranty"),
         ("goodwill", "Commercial Goodwill")],
        default="withdrawal",
        required=True,
    )
    requires_photo = fields.Boolean()
    auto_approve = fields.Boolean()
    restocking_fee_pct = fields.Float(string="Restocking Fee (%)", default=0.0)
    charge_to_customer = fields.Boolean(string="Return Shipping Charged to Customer")
    website_visible = fields.Boolean(default=True)
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint("UNIQUE(code)", "Reason code must be unique.")


class RmaGrade(models.Model):
    _name = "rma.grade"
    _description = "RMA QC Grade"

    name = fields.Char(required=True)
    description = fields.Text()
    disposition = fields.Selection(
        [("restock", "Restock as New"), ("refurb", "Refurbish / Second Life"),
         ("scrap", "Scrap"), ("repair", "Send to Repair")],
        default="restock",
        required=True,
    )
    discount_pct = fields.Float(string="Second-Life Discount (%)", default=0.0)
    active = fields.Boolean(default=True)
