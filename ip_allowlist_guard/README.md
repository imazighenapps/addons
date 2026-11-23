# Liste Blanche d'IP (ip_allowlist_guard)

Restriction par IP/plages pour le backend et les routes sensibles, exceptions par groupe, journal des refus.

## Problème
Les accès administrateur sont ouverts à Internet entier : surface d'attaque inutile.

## Fonctionnalités
- Règles par route et plage IP
- Exceptions par groupe
- Journal des refus
- Mode 'audit' sans blocage
- Rapport d'usage

## Dépendances
- `base`, `mail`
