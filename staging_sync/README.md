# Synchronisation Staging (staging_sync)

Copie prod→staging : sélection des tables, anonymisation automatique des données personnelles, cohérence des relations et journal.

## Problème
Tester sur des données réelles sans les anonymiser expose les clients ; créer des données fictives ne révèle pas les vrais bugs.

## Fonctionnalités
- Sélection des tables
- Anonymisation auto
- Cohérence des relations
- Journal des copies
- Gabarits

## Dépendances
- `base`, `mail`
