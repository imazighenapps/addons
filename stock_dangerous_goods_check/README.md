# Contrôle ADR avant Expédition (stock_dangerous_goods_check)

Contrôle ADR à l'expédition : classification par produit, calcul des quantités limitées/exemptées, checklist avant départ et documents ADR générés.

## Problème
Expédier des marchandises dangereuses sans vérifier classe, quantités limitées et documents expose à une immobilisation du camion.

## Fonctionnalités
- Classification ADR par produit
- Calcul quantités limitées
- Checklist avant départ
- Documents ADR générés
- Journal de conformité

## Dépendances
- `stock`, `sale`, `mail`
