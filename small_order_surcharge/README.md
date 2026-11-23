# Frais de Petit Lot (small_order_surcharge)

Supplément de traitement automatique sous un seuil : frais ajouté à la ligne, affiché clairement au client, supprimé au-delà du seuil et statistique des recettes de supplément.

## Problème
Le montant minimum de commande bloque le client au lieu de l'orienter : beaucoup de petites commandes rentables finissent refusées ou négociées oralement.

## Fonctionnalités
- Seuil de lot minimum par client
- Frais de traitement automatique
- Affichage clair au client
- Suppression au-delà du seuil
- Recettes de supplément par mois

## Dépendances
- `sale`, `account`, `mail`
