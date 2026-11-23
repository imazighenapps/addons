# Estimation de Port sur Devis (quote_shipping_estimate)

Estimateur de frais de port à la devis : calcul depuis poids, volume, zone et tarif appliqué, ligne de transport ajoutée automatiquement et seuil de franco respecté.

## Problème
Le devis ne montre aucun frais de transport : le client découvre le port sur la facture et la marge fond.

## Fonctionnalités
- Calcul du port depuis poids et zone
- Tarif appliqué configurable
- Ligne de transport automatique
- Gestion du seuil de franco
- Comparaison estimation / coût réel

## Dépendances
- `sale`, `stock`, `product`, `mail`
