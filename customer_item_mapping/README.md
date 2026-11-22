# Références Articles du Client (customer_item_mapping)

Table de correspondance référence client ↔ référence interne : mappage par client, résolution automatique sur devis, BL et factures, alerte sur références inconnues.

## Problème
Le client commande avec ses propres références (son code article) : l'équipe recherche à la main la correspondance et les erreurs de référence s'invitent dans les BL.

## Fonctionnalités
- Table de correspondance par client
- Résolution automatique sur les documents
- Alerte sur référence inconnue
- Import des listes client
- Historique des erreurs évitées

## Dépendances
- `sale`, `stock`, `account`, `mail`
