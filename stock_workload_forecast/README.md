# Charge de Travail Prévue (stock_workload_forecast)

Prévision de charge : projection des lignes à préparer (commandes confirmées, vagues à libérer) par jour et par zone, comparaison aux effectifs planifiés et alerte de sous-capacité.

## Problème
Le volume de lignes à préparer du lendemain arrive au jour le jour : ni planification d'effectifs ni lissage possible.

## Fonctionnalités
- Projection des lignes par jour/zone
- Comparaison aux effectifs
- Alerte de sous-capacité
- Historique de précision
- Aide au lissage

## Dépendances
- `stock`, `sale`, `mail`
