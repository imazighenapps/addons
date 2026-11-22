# Consolidation des Besoins par Fournisseur (order_consolidation_desk)

File de consolidation : besoins en attente regroupés par fournisseur et fenêtre, déclenchement quand un seuil économique est atteint, avec gain de transport affiché.

## Problème
Les commandes partent produit par produit au fil de l'eau : frais de port cumulés, minimums de facturation atteints à contre-coeur.

## Fonctionnalités
- File des besoins par fournisseur
- Regroupement par fenêtre de commande
- Seuil de déclenchement configuré
- Gain de frais affiché
- Conversion en commandes en un clic

## Dépendances
- `purchase`, `stock`, `mail`
