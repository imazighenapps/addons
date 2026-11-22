# -*- coding: utf-8 -*-
{
    "name": "De Xrechnung Einvoice",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Automate accounting controls, journal entries and financial reporting with full traceability.",
    "description": """
e-Invoicing XRechnung DE
========================
- Génération XML **XRechnung** (structure CIUS conforme, données facture/acheteur/vendeur/lignes)
- Contrôles de complétude avant génération (champs obligatoires)
- Statuts d'acceptation et journal de conformité
- Fichier XML téléchargeable et archivé
    """,
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/xrechnung_document_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
