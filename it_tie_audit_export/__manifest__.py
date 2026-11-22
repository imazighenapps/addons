# -*- coding: utf-8 -*-
{
    "name": "It Tie Audit Export",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "summary": "Automate accounting controls, journal entries and financial reporting with full traceability.",
    "description": """
Export TIE Italie
==================
Export d'audit **TIE** depuis les écritures Odoo pour les contrôles en
Italie :

- **Mapping des registres fiscaux** : registre IVA ventes/achats,
  corrispettivi, journal général, registre cespiti → journaux Odoo
- Génération **par période** : fichier CSV structuré (en-tête TIE avec
  codice fiscale, colonnes normalisées, ligne de totaux TOT)
- **Contrôles de complétude** : journaux de la période non mappés à un
  registre fiscal (blocants, contournable explicitement)
- **Journal des dépôts** : historique des exports avec traçage du dépôt
  effectif (date, déposant, note)
- Fichier `TIE_<codicefiscale>_<AAAAMMJJ>_<AAAAMMJJ>.csv`
    """,
    "author": "ImazighenApps",
    "website": "https://apps.odoo.com/",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/tie_registry_views.xml",
        "views/tie_export_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
