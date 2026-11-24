# Livraison Multi-Adresses (multi_drop_delivery)

Une seule commande, plusieurs adresses de livraison : répartition des lignes par destination, bons de livraison séparés et frais de port par arrêt.

## Problème
Une commande client doit être livrée sur plusieurs adresses : elle est saisie N fois, ce qui fausse les remises et la vision du dossier.

## Fonctionnalités
- Répartition des lignes par adresse
- Bons de livraison séparés
- Frais de port par arrêt
- Vision unique du dossier
- Contrôle des lignes non affectées

## Dépendances
- `sale`, `stock`, `mail`
