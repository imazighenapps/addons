# -*- coding: utf-8 -*-
{
    "name": "It Sdi Einvoice",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Reconcile accounts, monitor balances and audit every financial entry from one Odoo workspace.",
    "description": """
e-Invoicing Italie SdI
======================
Connecteur SdI pour les factures vers l'Italie :

- Génération du XML **FatturaPA** (codice destinatario, PEC, données fiscales)
- Suivi des statuts de transmission (prête, envoyée, NS/MC/MZ, refusée)
- Ré-émission guidée après refus et historique des tentatives
- Journal de conformité et contrôles de complétude avant génération
    """,
    "author": "ImazighenApps",
    "website": "https://apps.odoo.com/",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/sdi_document_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
