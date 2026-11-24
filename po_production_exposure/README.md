# Exposition Production des Retards Fournisseurs (po_production_exposure)

Exposition aval : chaque ligne en retard est rattachée aux ordres de fabrication et ventes dépendants, avec le jour de rupture projeté et les commandes impactées listées.

## Problème
Un retard fournisseur ne devient visible que le jour où un ordre de production s'arrête faute de matière.

## Fonctionnalités
- Liaison retard → ordres impactés
- Jour de rupture projeté
- Liste des OF et ventes exposés
- Communication d'alerte interne
- Historique des impacts

## Dépendances
- `purchase`, `mrp`, `mail`
