# Rapprochement Bancaire Assisté (bank_reconcile_assist)

Assistant d'auto-rapprochement bancaire pour Odoo 20 Community.

## Fonctionnalités
- Règles d'auto-matching configurables (libellé, référence, partenaire, journal)
- Tolérances de montant (fixe ou pourcentage)
- Propositions de lettrage classées par score
- Application en un clic des correspondances sélectionnées
- Rapport d'avancement mensuel par journal

## Dépendances
- `account`

## Utilisation
Menu **Comptabilité → Rapprochement assisté → Assistant de rapprochement** :
choisir le journal et la période, calculer les propositions, sélectionner puis appliquer.
Configurer les règles dans **Règles de rapprochement** (responsables comptables).

## Sécurité
- Comptables : exécution et lecture des règles.
- Responsables comptables : gestion des règles.
- Règle multi-société.

## Internationalisation
7 langues : en_US, fr_FR, ar_001 (RTL), es_ES, de_DE, pt_BR, zh_CN.

## Licence
LGPL-3
