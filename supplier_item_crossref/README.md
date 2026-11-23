# Correspondance des Références Fournisseurs (supplier_item_crossref)

Registre de correspondance : référence du fournisseur ↔ article interne par produit et fournisseur, recherche par référence fournisseur à la saisie et aide au matching des factures.

## Problème
Chaque fournisseur nomme le même produit autrement : les saisies se trompent, les factures ne matchent pas, les litiges se multiplient.

## Fonctionnalités
- Mapping par produit et fournisseur
- Recherche par référence externe
- Aide au matching de factures
- Import de la table de correspondance
- Rapport des produits non mappés

## Dépendances
- `purchase`, `product`, `mail`
