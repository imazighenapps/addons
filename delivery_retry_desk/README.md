# Échecs de Livraison et Reprogrammation (delivery_retry_desk)

Desk d'échecs : motif structuré de l'échec, re-programmation tracée avec créneau confirmé, coût de la seconde tentative imputé et taux de réussite au premier passage suivi.

## Problème
Les premières tentatives échouées (absent, adresse, accès) coûtent double transport et irritation, sans que le coût soit mesuré ni la cause suivie.

## Fonctionnalités
- Motif structuré d'échec
- Re-programmation tracée
- Coût de la re-tentative
- Taux de réussite au premier passage
- Actions de prévention

## Dépendances
- `sale`, `stock`, `mail`
