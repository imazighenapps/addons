# Taux Figé à la Devis (quote_fx_lock)

Figage du taux de change à la devis : taux enregistré à la validation, appliqué à la facturation, alerte si la facture s'écarte du taux promis.

## Problème
Un devis en devise se facture plus tard à un autre taux : la marge promie fond entre l'offre et la facture.

## Fonctionnalités
- Taux enregistré à la validation
- Application à la facturation
- Alerte d'écart de taux
- Historique des taux promis
- Impact marge du glissement de taux

## Dépendances
- `sale`, `account`, `mail`
