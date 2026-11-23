# Traqueur de Requêtes Lentes (slow_query_watch)

Collecte des requêtes lentes : seuils configurables, agrégation par modèle/action, top N+1 et rapport d'optimisation.

## Problème
Les pages lentes sont signalées par les utilisateurs sans cause identifiée : SQL coûteux et N+1 inaperçus.

## Fonctionnalités
- Seuils configurables
- Agrégation par action
- Détection N+1
- Top des requêtes
- Rapport d'optimisation

## Dépendances
- `base`, `mail`
