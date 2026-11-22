# États Financiers Community (financial_reports_community)

Moteur d'états financiers pour Odoo 20 Community : compte de résultat, bilan,
trésorerie, balance et états personnalisés, avec comparaison de périodes et export
PDF/CSV.

## Fonctionnalités
- Définitions d'états paramétrables (lignes, sous-totaux, signes, hiérarchie)
- Sources de comptes : groupes comptables, comptes explicites ou préfixes
- Agrégation sur écritures comptables postées (`account.move.line`)
- Comparaison entre deux périodes
- Export PDF (QWeb) et CSV
- Multi-société (règle d'entreprise)

## Dépendances
- `account`

## Installation
1. Copier le module dans le chemin d'addons Odoo 20.
2. Mettre à jour la liste des applications.
3. Installer « États Financiers Community ».

## Utilisation
Menu **Comptabilité → États financiers (Community)** : créer un état, définir ses
lignes (titres, lignes de comptes, sous-totaux), puis cliquer sur **Exécuter** pour
choisir la période et afficher / exporter le résultat.

## Sécurité
- Comptables (`account.group_account_user`) : lecture et exécution.
- Responsables comptables (`account.group_account_manager`) : configuration complète.
- Règle multi-société sur les définitions d'états.

## Internationalisation
7 langues : en_US, fr_FR, ar_001 (RTL à vérifier en environnement), es_ES, de_DE, pt_BR, zh_CN.
Voir `reports/financial_reports_community_translation_report.md`.

## Licence
LGPL-3
