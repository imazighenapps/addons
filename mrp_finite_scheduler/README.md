# Ordonnanceur à Capacité Finie (mrp_finite_scheduler)

Ordonnanceur qui calcule la charge par poste de charge, décale automatiquement les opérations vers le premier créneau disponible et propose des dates d'engagement réalistes.

## Problème
Odoo place les ordres de fabrication par date de besoin sans vérifier la capacité réelle des postes de charge : les ateliers découvrent des semaines surchargées au dernier moment.

## Fonctionnalités
- Charge par poste de charge et par semaine
- Décalage automatique des opérations
- Ordonnancement avant/arrière configurable
- Dates d'engagement proposées aux commerciaux
- Alerte sur les semaines surchargées

## Dépendances
- `mrp`, `mail`
