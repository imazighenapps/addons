# Délivrances Partielles (pharma_partial_dispense)

Délivrance partielle tracée : solde restant par ordonnance, relance automatique quand le produit revient en stock, clôture à la délivrance complète.

## Problème
Les délivrances partielles (rupture, prescription à fractionner) sont notées sur papier et le solde à délivrer se perd.

## Fonctionnalités
- Solde restant par ordonnance
- Relance au retour du produit en stock
- Historique des fractions délivrées
- Clôture explicite de l'ordonnance
- Statistiques de ruptures

## Dépendances
- `sale`, `stock`, `mail`
