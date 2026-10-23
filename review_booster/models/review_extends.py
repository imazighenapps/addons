# -*- coding: utf-8 -*-
from datetime import timedelta, date
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super().action_post()
        for move in self.filtered(
                lambda m: m.move_type == "out_invoice" and m.state == "posted"
                and m.commercial_partner_id.review_optin):
            campaigns = self.env["review.campaign"].search(
                [("trigger", "=", "invoice"),
                 ("company_id", "=", move.company_id.id),
                 ("active", "=", True)], order="delay_days asc, id asc")
            # One request per invoice. If several invoice campaigns match,
            # keep the most urgent one: contacting the customer twice for
            # the same invoice is a bug, not a feature.
            for camp in campaigns[:1]:
                exists = self.env["review.request"].search_count(
                    [("move_id", "=", move.id), ("campaign_id", "=", camp.id)])
                if not exists:
                    self.env["review.request"].create({
                        "campaign_id": camp.id,
                        "partner_id": move.commercial_partner_id.id,
                        "move_id": move.id,
                        "send_on": date.today() + timedelta(days=camp.delay_days),
                    })
        return res


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()
        for picking in self.filtered(lambda p: p.picking_type_id.code == "outgoing"):
            partner = picking.partner_id.commercial_partner_id
            if not partner or not partner.review_optin:
                continue
            campaigns = self.env["review.campaign"].search(
                [("trigger", "=", "delivery"),
                 ("company_id", "=", picking.company_id.id),
                 ("active", "=", True)])
            for camp in campaigns:
                exists = self.env["review.request"].search_count(
                    [("picking_id", "=", picking.id),
                     ("campaign_id", "=", camp.id)])
                if not exists:
                    self.env["review.request"].create({
                        "campaign_id": camp.id,
                        "partner_id": partner.id,
                        "picking_id": picking.id,
                        "send_on": date.today() + timedelta(days=camp.delay_days),
                    })
        return res
