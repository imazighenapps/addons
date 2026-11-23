# Règles de Sourcing Inter-Dépôts (sourcing_rule_desk)

Matrice de sourcing : règles de désignation du dépôt servant chaque zone/commande (stock, coût de transport, équilibrage), appliquées à la livraison avec traçabilité de la règle choisie.

## Problème
Odoo sert les commandes depuis le dépôt le plus proche sans stratégie : le mauvais entrepôt se vide, l'autre s'engorge et le transport coûte plus cher.

## Fonctionnalités
- Règles par zone et priorité
- Application à la livraison
- Traçabilité de la règle choisie
- Équilibrage des déclencheurs
- Analyse du sourcing réalisé

## Dépendances
- `stock`, `sale`, `mail`
