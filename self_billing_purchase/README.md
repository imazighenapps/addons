# Autofacturation Fournisseurs (self_billing_purchase)

Génération d'autofactures depuis les réceptions validées : conditions d'éligibilité par fournisseur, contrôle des écarts, envoi au fournisseur et traitement de ses corrections.

## Problème
Établir l'autofacturation (self-billing) depuis les réceptions est hors Odoo : les PME la préparent à la main et se disputent avec les fournisseurs sur les écarts.

## Fonctionnalités
- Autofacture générée des réceptions
- Conditions par fournisseur
- Contrôle et décision sur écarts
- Registre des corrections fournisseur
- Journal d'audit

## Dépendances
- `purchase`, `stock`, `account`, `mail`
