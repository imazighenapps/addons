# Pénalités Facturées aux Fournisseurs (vendor_chargeback_desk)

Refacturation de pénalités fournisseurs : barème par manquement, détection sur les réceptions et factures, note de débit générée et suivi du recouvrement.

## Problème
Les manquements fournisseurs (livraison en retard, emballage non conforme, documents manquants) ne sont jamais facturés en retour : les règles existent mais ne s'appliquent pas.

## Fonctionnalités
- Barème de pénalités par manquement
- Détection sur réceptions et factures
- Note de débit générée
- Contestation fournisseur tracée
- Suivi du recouvrement

## Dépendances
- `purchase`, `account`, `stock`, `mail`
