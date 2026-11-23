# Fenêtres de Maintenance dans le Planning (mrp_maintenance_windows)

Projection des fenêtres de maintenance planifiée dans le planning de charge : les opérations ne sont plus posées sur un poste en arrêt planifié, avec report proposé.

## Problème
La maintenance planifiée tombe sur des MOs déjà en cours : les arrêts surprennent l'atelier et cassent le planning.

## Fonctionnalités
- Calendrier d'indisponibilité par machine
- Exclusion des créneaux au calcul de charge
- Report proposé des opérations touchées
- Coordination maintenance/production tracée
- Alerte si conflit non résolu

## Dépendances
- `mrp`, `maintenance`, `mail`
