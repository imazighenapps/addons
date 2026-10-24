# -*- coding: utf-8 -*-
import base64
import csv
import io
import secrets
from xml.sax.saxutils import escape

from odoo import api, fields, models, _
from odoo.exceptions import UserError

GOOGLE_FIELDS = [
    "id", "title", "description", "link", "image_link", "availability",
    "price", "brand", "condition", "identifier_exists", "quantity",
]
META_FIELDS = [
    "id", "title", "description", "availability", "condition", "price",
    "link", "image_link", "brand",
]


class FeedChannel(models.Model):
    _name = "feed.channel"
    _description = "Product Feed"
    _inherit = ["mail.thread"]
    _order = "sequence, name"

    name = fields.Char(required=True, tracking=True)
    sequence = fields.Integer(default=10)
    backend = fields.Selection(
        [("google", "Google Merchant"), ("meta", "Meta Catalogue")],
        default="google", required=True, tracking=True)
    format = fields.Selection(
        [("xml", "XML (RSS 2.0)"), ("csv", "CSV")],
        default="xml", required=True, tracking=True)
    token = fields.Char(
        default=lambda self: secrets.token_urlsafe(18), required=True,
        copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    base_url = fields.Char(
        string="Website URL", default="https://www.example.com",
        help="Prefix used to build the product link.")
    active = fields.Boolean(default=True)
    min_price = fields.Monetary(
        currency_field="currency_id",
        help="Products cheaper than this are skipped. Zero disables the filter.")
    include_oos = fields.Boolean(
        string="Include Out of Stock", default=True)
    content = fields.Text(string="Last Generated Feed", readonly=True)
    mimetype = fields.Char(readonly=True, default="application/xml")
    last_generation = fields.Datetime(readonly=True)
    product_count = fields.Integer(readonly=True)
    error_count = fields.Integer(readonly=True)
    attachment_id = fields.Many2one("ir.attachment", string="Last File",
                                    readonly=True)
    log_ids = fields.One2many("feed.log", "channel_id", string="Validation")

    def _website_base(self):
        self.ensure_one()
        base = (self.base_url or "").rstrip("/")
        if not base:
            base = (self.company_id.website or "") \
                if "website" in self.company_id._fields else ""
        return base.rstrip("/")

    def _templates(self):
        domain = [
            ("sale_ok", "=", True),
            ("company_id", "in", [False, self.company_id.id]),
        ]
        if not self.include_oos:
            domain.append(("qty_available", ">", 0))
        return self.env["product.template"].search(domain, order="name")

    def _log(self, template, level, message, field_name=None):
        self.env["feed.log"].create({
            "channel_id": self.id,
            "product_id": template.product_variant_id.id,
            "product_name": template.display_name,
            "level": level,
            "field_name": field_name,
            "message": message,
        })

    def _check_product(self, template):
        errors = 0
        if not template.name:
            self._log(template, "error", _("The product has no title."), "title")
            errors += 1
        if not template.list_price:
            self._log(template, "error", _("The product has no price."), "price")
            errors += 1
        if not (template.default_code or template.barcode):
            self._log(template, "error",
                      _("The product has no SKU or barcode."), "id")
            errors += 1
        if not template.image_1920:
            self._log(template, "warning",
                      _("The product has no image."), "image_link")
        if not template.description_sale:
            self._log(template, "warning",
                      _("The product has no sales description."),
                      "description")
        return errors

    def _row(self, template):
        base = self._website_base()
        variant = template.product_variant_id
        price = template.list_price
        return {
            "id": template.default_code or template.barcode or str(variant.id),
            "title": template.name or "",
            "description": template.description_sale or template.name or "",
            "link": "%s/shop/%s" % (base, variant.id),
            "image_link": "%s/web/image/product.template/%s/image_1920"
                          % (base, template.id),
            "availability": "in stock" if template.qty_available > 0
                            else "out of stock",
            "price": "%.2f %s" % (price, self.currency_id.name),
            "brand": template.brand_id.name if "brand_id" in template._fields
                     and template.brand_id else self.company_id.name,
            "condition": "new",
            "identifier_exists": "yes" if (template.default_code or
                                           template.barcode) else "no",
            "quantity": int(template.qty_available),
        }

    def _feed_fields(self):
        return META_FIELDS if self.backend == "meta" else GOOGLE_FIELDS

    def _build_xml(self, templates):
        self.ensure_one()
        items = []
        for template in templates:
            row = self._row(template)
            cells = "".join(
                "<g:%s>%s</g:%s>" % (key, escape(str(row.get(key, ""))), key)
                for key in self._feed_fields())
            items.append("<item>%s</item>" % cells)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">'
            "<channel><title>%s</title><link>%s</link><description>%s</description>%s"
            "</channel></rss>" % (
                escape(self.name), escape(self._website_base()),
                escape(self.name), "".join(items)))

    def _build_csv(self, templates):
        self.ensure_one()
        buffer = io.StringIO()
        fields = self._feed_fields()
        writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for template in templates:
            writer.writerow(self._row(template))
        return buffer.getvalue()

    def action_generate(self):
        for channel in self:
            channel.log_ids.unlink()
            templates = channel._templates()
            errors = 0
            kept = self.env["product.template"]
            for template in templates:
                if channel.min_price and template.list_price < channel.min_price:
                    continue
                errors += channel._check_product(template)
                kept |= template
            content = channel._build_xml(kept) if channel.format == "xml" \
                else channel._build_csv(kept)
            mimetype = "application/xml" if channel.format == "xml" \
                else "text/csv"
            if channel.attachment_id:
                channel.attachment_id.unlink()
            filename = "%s.%s" % (
                channel.name.replace(" ", "-").lower() or "feed",
                "xml" if channel.format == "xml" else "csv")
            attachment = self.env["ir.attachment"].create({
                "name": filename,
                "raw": base64.b64encode(content.encode("utf-8")),
                "mimetype": mimetype,
                "res_model": "feed.channel",
                "res_id": channel.id,
            })
            channel.write({
                "content": content,
                "mimetype": mimetype,
                "attachment_id": attachment.id,
                "last_generation": fields.Datetime.now(),
                "product_count": len(kept),
                "error_count": errors,
            })
            channel.message_post(body=_(
                "%(count)s products exported, %(errors)s errors.",
                count=len(kept), errors=errors))
        return True

    def action_download(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/feed/%s" % self.token,
            "target": "self",
        }

    @api.model
    def _cron_generate(self):
        channels = self.search([("active", "=", True)])
        for channel in channels:
            channel.action_generate()
        return True


class FeedLog(models.Model):
    _name = "feed.log"
    _description = "Feed Validation Line"
    _order = "level, product_name"

    channel_id = fields.Many2one(
        "feed.channel", required=True, ondelete="cascade", index=True)
    product_id = fields.Many2one("product.product", string="Product")
    product_name = fields.Char()
    level = fields.Selection(
        [("error", "Error"), ("warning", "Warning")], required=True)
    field_name = fields.Char(string="Field")
    message = fields.Char(required=True)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    feed_error_count = fields.Integer(compute="_compute_feed_error_count")

    def _compute_feed_error_count(self):
        Log = self.env["feed.log"]
        for template in self:
            template.feed_error_count = Log.search_count([
                ("product_id", "=", template.product_variant_id.id),
                ("level", "=", "error"),
            ])
