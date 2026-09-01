# -*- coding: utf-8 -*-
from odoo import fields, models


class EduflowAdmissionDocumentLine(models.Model):
    """F3.3 -- one line per required document type on an admission file,
    tracking whether it has been received and its supporting attachment."""
    _name = 'eduflow.admission.document.line'
    _description = "Admission Document Tracking Line"
    _order = 'document_type_id'

    admission_id = fields.Many2one('eduflow.admission', string="Admission",
                                    required=True, ondelete='cascade')
    document_type_id = fields.Many2one('eduflow.document.type', string="Document Type",
                                        required=True)
    required = fields.Boolean(string="Required", default=True)
    received = fields.Boolean(string="Received", default=False)
    attachment_id = fields.Many2one('ir.attachment', string="Attached File")
    note = fields.Char(string="Note")

    _sql_constraints = [
        ('admission_doctype_uniq', 'unique(admission_id, document_type_id)',
         "This document type is already tracked on this admission file."),
    ]
