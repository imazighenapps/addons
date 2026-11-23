# Politique d'Authentification (auth_policy_enforcer)

Application d'une politique : longueur et complexité de mots de passe, durée de session par groupe, 2FA obligatoire par profil, rappels de rotation.

## Problème
Mots de passe faibles, sessions trop longues et 2FA optionnelle : la politique réelle dépend de chaque utilisateur.

## Fonctionnalités
- Complexité de mots de passe
- Durée de session par groupe
- 2FA obligatoire par profil
- Rotation planifiée
- Rapport de conformité

## Dépendances
- `base`, `auth_totp`, `mail`
