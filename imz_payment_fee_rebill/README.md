# Refacturation des Frais de Paiement (payment_fee_rebill)

Refacturation des frais de paiement : coût réel du mode utilisé calculé, ajout tracé à la facture selon les conditions du client et statistique des frais refacturés ou absorbés.

## Problème
Les frais de carte ou de virement international sont supportés par le vendeur sans être refacturés : une marge silencieuse part chez le PSP.

## Fonctionnalités
- Coût réel par mode de paiement
- Ajout tracé sur la facture
- Conditions par client
- Statistique frais refacturés ou absorbés
- Journal des surcharges

## Dépendances
- `sale`, `account`, `mail`
