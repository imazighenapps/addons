# Rapprochement Settlements Cartes (card_settlement_recon)

Import des settlements PSP : lignes de transactions, commissions, remboursements, rapprochement avec factures et écriture d'encaissement nette automatique.

## Problème
Les règlements Stripe/PayPal/PSP arrivent en lot avec commissions et remboursements ; les comptables rapprochent à la main.

## Fonctionnalités
- Import des fichiers de settlement PSP
- Rapprochement transactions/factures
- Commissions ventilées
- Écriture d'encaissement nette
- Réserve de remboursements

## Dépendances
- `account`, `mail`
