# File de Facturation Fin de Mois (delivered_uninvoiced_queue)

File de facturation : liste des livrables prêts à facturer avec ancienneté, propriétaire et motif de non-facturation, objectif de vidage en fin de mois.

## Problème
Des commandes livrées restent non facturées : personne ne voit la file, le CA du mois s'évapore et le client reçoit sa facture un mois après livraison.

## Fonctionnalités
- Liste des livrables à facturer
- Ancienneté et propriétaire
- Motif de non-facturation
- Objectif de vidage mensuel
- CA non facturé affiché

## Dépendances
- `sale`, `account`, `stock`, `mail`
