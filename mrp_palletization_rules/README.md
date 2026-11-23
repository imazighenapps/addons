# Règles de Palettisation (mrp_palletization_rules)

Règles de palettisation par produit : configuration des unités par carton, cartons par couche, couches par palette, calcul automatique du nombre de palettes sur les commandes.

## Problème
Calculer le nombre de palettes d'une commande (pièces par carton, cartons par couche, couches par palette) se fait à la main : erreurs de dimensionnement et de transport.

## Fonctionnalités
- Configuration par produit (carton, couche, palette)
- Calcul automatique sur commandes
- Poids et volume totaux
- Formatage du plan de palette
- Export du plan pour la chargeuse

## Dépendances
- `mrp`, `stock`, `sale`, `mail`
