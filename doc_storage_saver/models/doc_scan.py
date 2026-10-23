# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DocScan(models.Model):
    _name = "doc.storage.scan"
    _description = "Storage Scan"
    _inherit = ["mail.thread"]
    _order = "create_date desc"

    name = fields.Char(default="/", copy=False, readonly=True)
    date = fields.Datetime(default=fields.Datetime.now)
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")], default="draft", tracking=True)
    min_size_kb = fields.Integer(string="Min File Size (KB)", default=0)
    duplicate_ids = fields.One2many("doc.storage.duplicate", "scan_id")
    orphan_ids = fields.One2many("doc.storage.orphan", "scan_id")
    total_files = fields.Integer(readonly=True)
    total_bytes = fields.Integer(readonly=True)
    wasted_bytes = fields.Integer(string="Wasted (duplicates)", readonly=True)
    orphan_bytes = fields.Integer(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("doc.storage.scan") or "/"
        return super().create(vals_list)

    def action_run(self):
        for scan in self.sudo():
            env = scan.env
            scan.duplicate_ids.unlink()
            scan.orphan_ids.unlink()
            domain = []
            if scan.min_size_kb:
                domain.append(("file_size", ">=", scan.min_size_kb * 1024))
            atts = env["ir.attachment"].search(
                [("type", "=", "binary")] + domain)
            scan.total_files = len(atts)
            scan.total_bytes = sum(atts.mapped("file_size") or [0])
            groups = {}
            for att in atts:
                if att.checksum:
                    groups.setdefault(att.checksum, []).append(att.id)
            wasted = 0
            for checksum, ids in groups.items():
                if len(ids) < 2:
                    continue
                recs = env["ir.attachment"].browse(ids)
                size = recs[0].file_size or 0
                wasted += size * (len(ids) - 1)
                env["doc.storage.duplicate"].create({
                    "scan_id": scan.id,
                    "checksum": checksum,
                    "file_size": size,
                    "count": len(ids),
                    "wasted_bytes": size * (len(ids) - 1),
                    "attachment_ids": [(6, 0, ids)],
                })
            scan.wasted_bytes = wasted
            orphan_bytes = 0
            for att in atts:
                if att.res_model and att.res_id:
                    model = env.get(att.res_model)
                    if model is None or not model.browse(att.res_id).exists():
                        env["doc.storage.orphan"].create({
                            "scan_id": scan.id,
                            "attachment_id": att.id,
                            "file_name": att.name,
                            "file_size": att.file_size or 0,
                            "reason": _("Linked record is gone."),
                        })
                        orphan_bytes += att.file_size or 0
            scan.orphan_bytes = orphan_bytes
            scan.state = "done"
            scan.message_post(body=_(
                "Scan done: %d files, %s wasted on duplicates, %s orphaned.") % (
                    scan.total_files, scan.wasted_bytes, scan.orphan_bytes))
        return True

    @api.model
    def _cron_weekly_scan(self):
        scan = self.create({})
        scan.action_run()
        return True


class DocDuplicate(models.Model):
    _name = "doc.storage.duplicate"
    _description = "Duplicate File Group"

    scan_id = fields.Many2one("doc.storage.scan", required=True, ondelete="cascade")
    checksum = fields.Char(readonly=True)
    file_size = fields.Integer(readonly=True)
    count = fields.Integer(readonly=True)
    wasted_bytes = fields.Integer(readonly=True)
    attachment_ids = fields.Many2many("ir.attachment", string="Files")
    state = fields.Selection(
        [("new", "To Review"), ("kept", "Cleaned"), ("ignored", "Ignored")],
        default="new",
    )

    def _is_safe_to_delete(self, attachment):
        """A file is safe to delete only if it is not linked to a live record."""
        attachment = attachment.sudo()
        if attachment.res_model and attachment.res_id:
            model = self.env.get(attachment.res_model)
            if model is not None and model.browse(attachment.res_id).exists():
                return False
        return True

    def action_clean_keep_newest(self):
        for group in self:
            atts = group.sudo().attachment_ids.sorted("create_date", reverse=True)
            if len(atts) < 2:
                continue
            skipped = 0
            for att in atts[1:]:
                if self._is_safe_to_delete(att):
                    att.unlink()
                else:
                    skipped += 1
            group.state = "kept"
        return True

    def action_ignore(self):
        self.write({"state": "ignored"})


class DocOrphan(models.Model):
    _name = "doc.storage.orphan"
    _description = "Orphan Attachment"

    scan_id = fields.Many2one("doc.storage.scan", required=True, ondelete="cascade")
    attachment_id = fields.Many2one("ir.attachment", ondelete="set null")
    file_name = fields.Char(string="File Name", readonly=True)
    file_size = fields.Integer(readonly=True)
    reason = fields.Char(readonly=True)
    state = fields.Selection(
        [("new", "To Review"), ("deleted", "Deleted"), ("ignored", "Ignored")],
        default="new",
    )

    def action_delete(self):
        for rec in self.sudo():
            if rec.attachment_id:
                rec.attachment_id.unlink()
            rec.state = "deleted"

    def action_ignore(self):
        self.write({"state": "ignored"})
