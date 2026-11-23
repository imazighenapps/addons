# Échange EDI Fournisseurs (supplier_edi_desk)

Échange de fichiers EDI normalisés (ORDERS, DESADV, INVOIC) : génération des commandes, ingestion des avis et factures avec matching contrôlé et file des anomalies.

## Problème
Avec les fournisseurs équipés, tout se retape à la main : commandes recopiées, avis d'expédition ignorés, factures resaisies.

## Fonctionnalités
- Génération ORDERS
- Ingestion DESADV et INVOIC
- Matching contrôlé
- File des anomalies expliquées
- Journal des échanges

## Dépendances
- `purchase`, `account`, `stock`, `mail`
