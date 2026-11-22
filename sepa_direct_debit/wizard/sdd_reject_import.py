# -*- coding: utf-8 -*-
import base64
from xml.etree import ElementTree as ET
from odoo import fields, models
from odoo.exceptions import UserError


class SddRejectImport(models.TransientModel):
    _name = "sdd.reject.import"
    _description = "Import des rejets SDD (pain.002)"

    batch_id = fields.Many2one("sdd.batch", string="Lot SDD", required=True)
    file_data = fields.Binary(string="Fichier pain.002", required=True)
    file_name = fields.Char(string="Nom du fichier")

    def action_import(self):
        self.ensure_one()
        try:
            raw = bytes(self.file_data or b"")
            content = raw if raw[:1] == b"<" or raw.startswith(b"\xef\xbb\xbf") else base64.b64decode(raw)
            root = ET.fromstring(content)
        except Exception as e:
            raise UserError("Fichier pain.002 invalide : %s" % e)
        texts = []
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag in ("StsRsnInf", "TxSts", "OrgnlEndToEndId") and (elem.text or list(elem)):
                if elem.text and elem.text.strip():
                    texts.append("%s: %s" % (tag, elem.text.strip()))
            for child in elem:
                ctag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if ctag in ("Cd", "Prtry", "AddtlInf") and child.text:
                    texts.append("%s: %s" % (ctag, child.text.strip()))
        info = "\n".join(texts[:200]) if texts else "Rejet importé (aucun détail lisible)."
        self.batch_id.write({"state": "rejected", "reject_info": info})
        self.batch_id.message_post(body="Rejets pain.002 importés :\n%s" % info[:2000])
        return {"type": "ir.actions.act_window_close"}
