# -*- coding: utf-8 -*-
{
    "name": "Saft Export Pack",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Reconcile accounts, monitor balances and audit every financial entry from one Odoo workspace.",
    "description": """
Export SAF-T Multi-Pays
========================
Génère le fichier d'audit **SAF-T** (Standard Audit File for Tax purposes,
spécification OECD) exigé par plusieurs pays (Portugal, Autriche, Luxembourg,
Norvège…) :

- **Profils par pays** : namespace XML, version de schéma, comptes/taxes
- **Mapping des comptes** : AccountType SAF-T par compte, ou fallback par
  groupe interne Odoo ; contrôle de complétude (mapping explicite exigible)
- **Mapping des taxes** : TaxTableEntry par taxe (code, taux, type)
- Génération **mensuelle ou annuelle** : Header, MasterFiles (comptes,
  clients, fournisseurs, table de taxes), GeneralLedgerEntries (toutes les
  écritures validées de la période)
- **Contrôles de complétude** : comptes/taxes non mappés, équilibre des
  totaux, avant génération du fichier
- **Journal des dépôts** : historique des exports avec fichiers archivés
- **Extensible** : ajouter un profil pour un nouveau pays sans développement
    """,
    "author": "ImazighenApps",
    "website": "https://apps.odoo.com/",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/saft_profile_views.xml",
        "views/saft_export_views.xml",
        "views/menus.xml",
    ],
    "application": True,
}
