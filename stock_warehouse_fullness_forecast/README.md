# Saturation de l'Entrepôt (stock_warehouse_fullness_forecast)

Prévision de saturation : projection de l'occupation (arrivages planifiés vs sorties prévues), alerte à J-x sur les zones et plan de surflux proposé.

## Problème
L'entrepôt déborde soudainement quand les commandes fournisseurs arrivent en masse : personne ne voit la saturation venir.

## Fonctionnalités
- Projection d'occupation par zone
- Alerte à J-x
- Plan de surflux proposé
- Comparaison entrepôts
- Historique des pics

## Dépendances
- `stock`, `purchase`, `sale`, `mail`
