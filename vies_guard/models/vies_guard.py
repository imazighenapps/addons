# -*- coding: utf-8 -*-
import json
import re
import urllib.parse
import urllib.request
from datetime import timedelta

from odoo import api, fields, models, _

EU_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE",
}
VIES_URL = "https://ec.europa.eu/taxation_customs/vies/rest-api/ms/%s/vat/%s"
VIES_TIMEOUT = 10


def normalize_vat(vat):
    return re.sub(r"[^0-9A-Za-z]", "", vat or "").upper()


def vies_query(vat):
    """Call the official VIES REST API and return its JSON answer."""
    code = normalize_vat(vat)
    country, number = code[:2], code[2:]
    if country not in EU_COUNTRIES or not number:
        raise ValueError("Not a European VAT number: %s" % (vat or ""))
    url = VIES_URL % (country, urllib.parse.quote(number))
    request = urllib.request.Request(
        url, headers={"Accept": "application/json",
                      "User-Agent": "Odoo VIESGuard"})
    with urllib.request.urlopen(request, timeout=VIES_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


class ResCompany(models.Model):
    _inherit = "res.company"

    vies_auto_check = fields.Boolean(
        string="Automatic VIES Check", default=True,
        help="Check the VAT number when a partner is created or changed.")
    vies_recheck_days = fields.Integer(
        string="Re-check After (days)", default=30,
        help="Re-check VAT numbers older than this. Zero disables it.")


class ResPartner(models.Model):
    _inherit = "res.partner"

    vies_state = fields.Selection(
        [("not_checked", "Not Checked"), ("valid", "Valid"),
         ("invalid", "Invalid"), ("unavailable", "Service Unavailable")],
        string="VIES Status", default="not_checked", copy=False,
        readonly=True, index=True)
    vies_checked_on = fields.Datetime(
        string="Checked On", readonly=True, copy=False)
    vies_trader_name = fields.Char(
        string="Trader Name (VIES)", readonly=True, copy=False)
    vies_trader_address = fields.Text(
        string="Trader Address (VIES)", readonly=True, copy=False)
    vies_message = fields.Char(
        string="VIES Message", readonly=True, copy=False)
    vies_is_eu = fields.Boolean(
        string="EU VAT", compute="_compute_vies_is_eu")
    vies_check_ids = fields.One2many(
        "vies.check", "partner_id", string="VAT Checks")
    vies_check_count = fields.Integer(compute="_compute_vies_check_count")

    @api.depends("vat", "country_id")
    def _compute_vies_is_eu(self):
        for partner in self:
            country = (partner.country_id.code or "").upper()
            prefix = normalize_vat(partner.vat)[:2]
            partner.vies_is_eu = country in EU_COUNTRIES or prefix in EU_COUNTRIES

    @api.depends("vies_check_ids")
    def _compute_vies_check_count(self):
        for partner in self:
            partner.vies_check_count = len(partner.vies_check_ids)

    @api.model
    def _vies_query(self, vat):
        return vies_query(vat)

    def _run_vies_check(self, source="manual"):
        for partner in self:
            code = normalize_vat(partner.vat)
            if not code or code[:2] not in EU_COUNTRIES:
                continue
            vals = {
                "vies_checked_on": fields.Datetime.now(),
                "vies_trader_name": False,
                "vies_trader_address": False,
            }
            try:
                data = partner._vies_query(code)
                valid = bool(data.get("isValid"))
                message = data.get("userError") or (
                    "Valid" if valid else "Invalid")
                vals.update({
                    "vies_state": "valid" if valid else "invalid",
                    "vies_message": message,
                    "vies_trader_name": data.get("name") or False,
                    "vies_trader_address": data.get("address") or False,
                })
            except Exception as error:  # network, timeout, bad answer
                vals.update({
                    "vies_state": "unavailable",
                    "vies_message": str(error)[:250],
                })
            partner.write(vals)
            self.env["vies.check"].create({
                "partner_id": partner.id,
                "vat": code,
                "state": vals["vies_state"],
                "message": vals.get("vies_message"),
                "source": source,
                "trader_name": vals.get("vies_trader_name"),
                "company_id": (partner.company_id or self.env.company).id,
            })
        return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("vat"):
                vals["vat"] = normalize_vat(vals["vat"])
        partners = super().create(vals_list)
        if not self.env.context.get("vies_no_auto"):
            for partner in partners.filtered("vat"):
                company = partner.company_id or self.env.company
                if company.vies_auto_check:
                    partner._run_vies_check("auto")
        return partners

    def write(self, vals):
        if vals.get("vat"):
            vals = dict(vals, vat=normalize_vat(vals["vat"]))
        result = super().write(vals)
        if "vat" in vals and not self.env.context.get("vies_no_auto"):
            for partner in self.filtered("vat"):
                company = partner.company_id or self.env.company
                if company.vies_auto_check:
                    partner._run_vies_check("auto")
        return result

    def action_vies_check(self):
        self.ensure_one()
        if not normalize_vat(self.vat):
            raise ValueError("Set a VAT number before checking it.")
        self._run_vies_check("manual")
        return True

    def action_view_vies_checks(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "VAT Checks",
            "res_model": "vies.check",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
        }

    @api.model
    def _cron_recheck(self):
        today = fields.Datetime.now()
        for company in self.env["res.company"].search([]):
            if not company.vies_auto_check or not company.vies_recheck_days:
                continue
            limit = today - timedelta(days=company.vies_recheck_days)
            partners = self.search([
                ("vat", "!=", False),
                ("company_id", "in", [False, company.id]),
                "|", ("vies_checked_on", "=", False),
                ("vies_checked_on", "<", limit),
            ])
            partners._run_vies_check("cron")
        return True


class ViesCheck(models.Model):
    _name = "vies.check"
    _description = "VIES VAT Check"
    _order = "check_date desc, id desc"

    name = fields.Char(default="/", required=True)
    partner_id = fields.Many2one(
        "res.partner", string="Partner", required=True,
        ondelete="cascade", index=True)
    vat = fields.Char(string="VAT Number", required=True)
    state = fields.Selection(
        [("valid", "Valid"), ("invalid", "Invalid"),
         ("unavailable", "Unavailable")],
        required=True, index=True)
    message = fields.Char()
    trader_name = fields.Char(string="Trader Name")
    source = fields.Selection(
        [("manual", "Manual"), ("auto", "Automatic"),
         ("batch", "Batch"), ("cron", "Scheduler")],
        default="manual", required=True)
    check_date = fields.Datetime(
        default=fields.Datetime.now, required=True)
    user_id = fields.Many2one(
        "res.users", string="Checked By",
        default=lambda self: self.env.user, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "vies.check") or "/"
        return super().create(vals_list)


class ViesBatchWizard(models.TransientModel):
    _name = "vies.batch.wizard"
    _description = "Batch VIES Check"

    partner_ids = fields.Many2many(
        "res.partner", string="Partners",
        help="Leave empty to check every partner with a VAT number.")
    only_unchecked = fields.Boolean(
        string="Only Unchecked or Unavailable", default=True)
    only_contacts = fields.Boolean(
        string="Only Customers and Suppliers", default=True)
    checked_count = fields.Integer(readonly=True)
    valid_count = fields.Integer(readonly=True)
    invalid_count = fields.Integer(readonly=True)
    unavailable_count = fields.Integer(readonly=True)

    def action_run(self):
        self.ensure_one()
        if self.partner_ids:
            domain = [("id", "in", self.partner_ids.ids), ("vat", "!=", False)]
        else:
            domain = [("vat", "!=", False)]
            if self.only_contacts:
                domain += ["|", ("customer_rank", ">", 0),
                           ("supplier_rank", ">", 0)]
            if self.only_unchecked:
                domain += [("vies_state", "in",
                            ["not_checked", "unavailable"])]
        partners = self.env["res.partner"].search(domain)
        partners._run_vies_check("batch")
        valid = len(partners.filtered(lambda p: p.vies_state == "valid"))
        invalid = len(partners.filtered(lambda p: p.vies_state == "invalid"))
        unavailable = len(
            partners.filtered(lambda p: p.vies_state == "unavailable"))
        self.write({
            "checked_count": len(partners),
            "valid_count": valid,
            "invalid_count": invalid,
            "unavailable_count": unavailable,
        })
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "VIES check finished",
                "message": "%(total)s checked: %(valid)s valid, "
                           "%(invalid)s invalid, %(unavailable)s unavailable."
                           % {"total": len(partners), "valid": valid,
                              "invalid": invalid,
                              "unavailable": unavailable},
                "type": "warning" if invalid else "success",
                "sticky": False,
            },
        }
