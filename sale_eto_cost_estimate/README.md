# Estimation de Coût ETO à la Commande (sale_eto_cost_estimate)

Estimateur ETO : assemblage du coût estimé depuis les références de la commande, heures de gammes estimées, achats prévus, marge cible et prix proposé cohérent.

## Problème
Sur les produits à la commande, le devis exige un coût estimé (matière + heures + achats) que les commerciaux font calculer à la main par la production.

## Fonctionnalités
- Coût estimé par ligne de commande
- Heures et achats prévisionnels
- Marge cible et prix plancher
- Comparaison estimation vs réalisé à la fin
- Historique des estimations

## Dépendances
- `sale`, `mrp`, `purchase`, `mail`
