# Arrondi Psychologique des Prix (charm_price_rounding)

Formatage automatique des prix de vente selon des règles d'arrondi charmant (9,90 / x,95 / seuil rond) par famille, avec garde-fou de marge minimale.

## Problème
Les prix calculés donnent des montants techniques (137,42) qui rendent les offres peu lisibles et défavorables psychologiquement.

## Fonctionnalités
- Règles d'arrondi par famille
- Application au calcul des prix
- Garde-fou de marge minimale
- Aperçu avant application
- Historique des arrondis

## Dépendances
- `sale`, `product`, `mail`
