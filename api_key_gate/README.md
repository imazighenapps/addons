# Clés API & Quotas (api_key_gate)

Gestion de clés API par consommateur : périmètres (modèles/actions), quotas de débit, statistiques d'usage et révocation datée.

## Problème
Les accès API sont donnés via comptes utilisateurs complets : périmètre flou, usage non audité, aucune limite.

## Fonctionnalités
- Clés par consommateur avec périmètres
- Quotas de débit
- Statistiques d'usage
- Révocation datée
- Journal des refus

## Dépendances
- `base`, `mail`
