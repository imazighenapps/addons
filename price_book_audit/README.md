# Audit du Livre de Prix (price_book_audit)

Audit automatique du référentiel tarifaire : règles d'anomalie (prix nul, négatif, écart au-delà d'un seuil, trous de période), liste priorisée et correction guidée.

## Problème
Les livres de prix s'encrassent : prix à zéro, prix négatifs, écarts énormes avec l'historique, doublons entre listes — découverts par les clients.

## Fonctionnalités
- Règles d'anomalies configurables
- Détection des prix nuls et négatifs
- Écarts contre l'historique
- Liste priorisée avec propriétaires
- Historique du score tarifaire

## Dépendances
- `sale`, `product`, `mail`
