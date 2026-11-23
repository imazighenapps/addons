# Chiffrement de Champs Sensibles (field_crypto)

Chiffrement applicatif de champs désignés : stockage chiffré, déchiffrement à la volée pour les groupes autorisés et journal des accès.

## Problème
IBAN, données médicales ou salariales sont en clair dans la base : un dump ou un accès excessif les expose.

## Fonctionnalités
- Champs désignés chiffrés
- Groupes autorisés
- Journal des accès
- Rotation de clés
- Export protégé

## Dépendances
- `base`, `mail`
