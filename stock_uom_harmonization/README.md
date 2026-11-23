# Harmonisation des Unités (stock_uom_harmonization)

Assistant d'harmonisation : détection des incohérences d'unités par produit, proposition de correction en masse, contrôle d'impact sur les documents en cours et journal.

## Problème
Les unités de mesure du catalogue sont incohérentes (kg/l, caisse/pièce) : les calculs de coût et de marge dérivent.

## Fonctionnalités
- Détection des incohérences d'unités
- Correction en masse
- Contrôle d'impact avant application
- Journal des changements
- Rapport avant/après

## Dépendances
- `stock`, `product`, `mail`
