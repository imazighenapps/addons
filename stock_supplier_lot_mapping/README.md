# Correspondance des Lots Fournisseurs (stock_supplier_lot_mapping)

Cartographie des lots : association automatique lot fournisseur ↔ lot interne à la réception, recherche bidirectionnelle et fiche de traçabilité fournisseur.

## Problème
Le lot imprimé par le fournisseur et le lot interne ne parlent pas le même langage : impossible de remonter d'un lot client vers le lot et le BL fournisseur.

## Fonctionnalités
- Association lot fournisseur/interne
- Recherche bidirectionnelle
- Fiche de traçabilité
- Export vers audits
- Alerte de lot sans lien

## Dépendances
- `stock`, `purchase`, `mail`
