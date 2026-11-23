# Coffre de Credentials (credential_vault)

Coffre chiffré des credentials par connexion : accès journalisé, rotation planifiée, recherche des secrets exposés dans les paramètres.

## Problème
Les identifiants des services externes (SMTP, passerelles) sont stockés en clair dans les paramètres système.

## Fonctionnalités
- Stockage chiffré par connexion
- Accès journalisés
- Rotation planifiée
- Détection de secrets en clair
- Rapport d'exposition

## Dépendances
- `base`, `mail`
