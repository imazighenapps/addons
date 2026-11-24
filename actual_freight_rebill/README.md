# Refacturation du Fret Réel (actual_freight_rebill)

Refacturation du fret réel : coût transport réel rattaché à la livraison, écart versus estimé affiché, refacturation tracée sur la facture et tolérance configurable.

## Problème
Le port estimé au devis diffère du coût réel constaté : le delta est absorbé ou refacturé oralement, sans trace ni cohérence.

## Fonctionnalités
- Coût transport réel par livraison
- Écart versus estimé affiché
- Refacturation tracée
- Tolérance configurable
- Statistique des écarts absorbés

## Dépendances
- `sale`, `stock`, `account`, `mail`
