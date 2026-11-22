# COGS à la Facturation (cogs_invoice_engine)

Moteur COGS facturation : coût rattaché à la facture (COGS reconnu à la facturation), écritures alternatives, marge par facture exacte.

## Problème
Dans Community, le coût des ventes est posté à la livraison : la marge par facture au moment de la comptabilisation est faussée.

## Fonctionnalités
- COGS reconnu à la facturation
- Écritures alternatives
- Marge par facture exacte
- Rapport de cohérence stock
- Option de bascule

## Dépendances
- `account`, `stock`, `sale`, `mail`
