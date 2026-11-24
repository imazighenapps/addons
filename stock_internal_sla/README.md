# SLA Interne de Sortie (stock_internal_sla)

SLA de sortie : cible horaire par entrepôt/jour, mesure du délai picking→expédition, alertes sur les commandes qui traînent et historique hebdomadaire.

## Problème
Le temps qui sépare le picking validé de l'expédition réelle n'est mesuré nulle part : les retards internes restent invisibles.

## Fonctionnalités
- Cibles de délai par entrepôt
- Alerte sur les dépassements
- Historique hebdomadaire
- Analyse par créneau horaire
- Comparaison entrepôts

## Dépendances
- `stock`, `sale`, `mail`
