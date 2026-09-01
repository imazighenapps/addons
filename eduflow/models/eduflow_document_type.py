# -*- coding: utf-8 -*-
from odoo import fields, models


class EduflowDocumentType(models.Model):
    """F3.3 -- reference list of document types that can be required for an
    admission file, optionally scoped to a level (e.g. birth certificate,
    previous report card, medical certificate)."""
    _name = 'eduflow.document.type'
    _description = "Admission Document Type"
    _order = 'name'

    name = fields.Char(string="Document Type", required=True)
    level_id = fields.Many2one('eduflow.level', string="Level",
                                help="Leave empty if required for all levels.")
    required = fields.Boolean(string="Required by Default", default=True)
    company_id = fields.Many2one('res.company', string="Institution",
                                  default=lambda self: self.env.company)
