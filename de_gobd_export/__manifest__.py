# -*- coding: utf-8 -*-
{
    "name": "De Gobd Export",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Give finance teams a focused Odoo app for reconciliation, analysis and compliant reporting.",
    "description": """
Export GoBD Allemagne
=====================
Génère un export **GoBD (GDPdU)** pour les audits fiscaux allemands :

- Structure de tables/index conforme : `index.xml` décrivant les tables et champs
- Export des écritures comptables en fichier de données (CSV/variable length)
- Protocole de remise daté et journal des exports (historique, fichiers archivés)
- Sélection par période, société et journaux, contrôles de cohérence

Les fichiers sont regroupés dans une archive ZIP téléchargeable et conservée
dans le journal des exports.
    """,
    "author": "ImazighenApps",
    "website": "https://apps.odoo.com/",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/gobd_export_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}