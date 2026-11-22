# Réception à l'Aveugle (stock_blind_receiving)

Comptage à l'aveugle à la réception : la quantité du BL est masquée jusqu'au comptage effectif, puis révélée ; les écarts exigent un motif et alimentent un fichier fournisseur.

## Problème
À la réception, les équipes valident la quantité attendue sans compter : les écarts de livraison fournisseurs passent inaperçus et se découvrent des semaines plus tard en comptage.

## Fonctionnalités
- Quantité attendue masquée au comptage
- Révélation de l'écart après comptage
- Motif obligatoire sur les écarts
- Statistiques d'écarts par fournisseur

## Dépendances
- `stock`, `purchase`, `mail`
