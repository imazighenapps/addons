# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LabelTemplate(models.Model):
    _name = "label.template"
    _description = "Label Template"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        help="Short code used to identify the template.")
    label_type = fields.Selection(
        [("product", "Product"), ("lot", "Lot"), ("location", "Location")],
        default="product", required=True, tracking=True,
        help="Type of label produced by this template.")
    width_mm = fields.Integer(
        string="Width (mm)", default=50, required=True,
        help="Label width in millimeters.")
    height_mm = fields.Integer(
        string="Height (mm)", default=30, required=True,
        help="Label height in millimeters.")
    content = fields.Text(
        help="Description of the fields and layout printed on the label.")
    job_ids = fields.One2many("label.job", "template_id", string="Print Jobs")
    job_count = fields.Integer(
        string="Print Jobs", compute="_compute_job_count", store=True,
        help="Number of print jobs using this template.")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("job_ids")
    def _compute_job_count(self):
        for record in self:
            record.job_count = len(record.job_ids)

    @api.constrains("width_mm", "height_mm")
    def _check_dimensions(self):
        for record in self:
            if record.width_mm <= 0 or record.height_mm <= 0:
                raise ValidationError(_(
                    "Label dimensions of %s must be greater than zero.",
                    record.name))
