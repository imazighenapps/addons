# Révisions de Plans chez les Fournisseurs (supplier_drawing_revision)

Contrôle de révision chez fournisseurs : chaque révision est transmise avec accusé, indexation des versions en vigueur par article et blocage de la commande tant que l'accusé manque.

## Problème
Envoyer un plan révisé à un fournisseur ne garantit rien : il peut produire encore six mois sur l'ancienne version, sans trace de qui a reçu quoi.

## Fonctionnalités
- Révision transmise avec accusé
- Index des versions par article
- Blocage tant que non accusé
- Diff visuelle des révisions
- Historique complet

## Dépendances
- `purchase`, `mail`
