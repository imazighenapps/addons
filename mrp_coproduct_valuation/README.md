# Co-Produits et Sous-Produits (mrp_coproduct_valuation)

Gestion des co-produits : partage du coût de la MO entre produits principaux et secondaires selon des clés (poids, valeur), valorisation des sous-produits vendus ou rebus.

## Problème
Les co-produits (décolletages, sciures revendues, sous-produits) n'ont pas de coût ni de revenu dans la MO : le coût réel du produit principal est faussé.

## Fonctionnalités
- Clés de répartition du coût par MO
- Valorisation automatique des sous-produits
- Écritures de réception des co-produits
- Rendement co-produits suivi
- Rapport de coût net par produit principal

## Dépendances
- `mrp`, `stock`, `account`, `mail`
