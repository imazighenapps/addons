# Docteur de la Base (db_doctor)

Analyse de santé de base : volumétrie par table, index manquants, fragmentation, suggestions d'action (reindex, vacuum, purge) et rapport.

## Problème
La base grossit sans contrôle : tables bloat, index manquants, registres orphelins ralentissent tout.

## Fonctionnalités
- Volumétrie par table
- Index manquants
- Suggestions d'action
- Historique de croissance
- Rapport PDF

## Dépendances
- `base`, `mail`
