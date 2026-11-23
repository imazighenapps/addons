# Gardien de Quota API (api_rate_guard)

Quotas d'API : limites par route/utilisateur/clé, réponse 429 propre, journal des dépassements et dashboard.

## Problème
Les appels API externes (site, intégrations) peuvent saturer l'instance : aucun garde-fou natif.

## Fonctionnalités
- Limites par route
- Réponse 429 propre
- Journal des dépassements
- Dashboard
- Règles par clé

## Dépendances
- `base`, `mail`
