# Numérotation des Lots par Règles (quality_lot_numbering_rules)

Générateur de numéros de lot : règles par famille (préfixe, date de production, ligne, séquence), attribution automatique à la production et contrôle d'unicité.

## Problème
Les numéros de lot sont saisis à la main selon des conventions par produit : incohérences, doublons et impossible de faire l'IA sans convention.

## Fonctionnalités
- Règles par famille de produits
- Variables (date, ligne, équipe, séquence)
- Attribution automatique à la MO
- Contrôle d'unicité multi-sites
- Historique des règles

## Dépendances
- `mrp`, `stock`, `mail`
