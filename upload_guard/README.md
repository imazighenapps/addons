# Gardien des Uploads (upload_guard)

Contrôle des uploads : extensions autorisées, taille max par contexte, vérification de signature de fichier et quarantaine.

## Problème
Les uploads (portail, pièces) acceptent tout : fichiers exécutables, tailles abusives, types inattendus.

## Fonctionnalités
- Extensions autorisées
- Taille max par contexte
- Vérification de signature
- Quarantaine
- Journal

## Dépendances
- `base`, `mail`
