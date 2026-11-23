# Pilotage des En-Cours par Poste (mrp_wip_queue_monitor)

Moniteur d'en-cours : quantité et temps de cycle devant chaque poste, détection des goulots, comparaison du lead time réel au théorique et alerte sur les dérives.

## Problème
Les files d'attente devant chaque poste s'allongent sans signal : les goulots ne sont visibles qu'à la fin du mois sur les retards.

## Fonctionnalités
- File par poste en quantité et jours
- Détection des goulots
- Lead time réel vs théorique
- Alertes de dérive de WIP
- Rapport hebdo par atelier

## Dépendances
- `mrp`, `mail`
