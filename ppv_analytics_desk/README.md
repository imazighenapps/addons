# Analytique des Écarts de Prix d'Achat (ppv_analytics_desk)

Analytique PPV : décomposition des écarts de prix d'achat par fournisseur, produit, famille et période, avec drill-down jusqu'à la facture et rapport de contribution.

## Problème
Les alertes prix isolées s'accumulent sans synthèse : impossible de dire pourquoi le coût standard a dérivé (négociation, change, volume, fournisseur).

## Fonctionnalités
- Décomposition par dimension
- Drill-down jusqu'à la facture
- Contribution des principaux écarts
- Comparaison au coût standard
- Rapport mensuel

## Dépendances
- `purchase`, `account`, `mail`
