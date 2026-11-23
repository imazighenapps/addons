# Rattrapage des Manquants de Picking (stock_short_pick_recovery)

Boucle de rattrapage : détection des écarts de quantité au picking, recherche des stocks alternatifs, complétion avant expédition ou justification, analyse des causes.

## Problème
Un short pick (ligne préparée en moins) s'explique mal : la commande part incomplète sans boucle de re-complétion ni analyse.

## Fonctionnalités
- Détection des écarts de quantité
- Recherche de stock alternatif
- Complétion avant expédition
- Justification obligatoire
- Analyse des causes récurrentes

## Dépendances
- `stock`, `sale`, `mail`
