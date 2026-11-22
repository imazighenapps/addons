# Numéro de Commande Client Obligatoire (customer_po_required)

Numéro de commande client obligatoire : champ exigé selon le client, format validé, répété sur BL et facture, et liste des ventes expédiées sans référence.

## Problème
Sans numéro de commande client sur le BL et la facture, le client bloque le paiement et la trésorerie attend des semaines.

## Fonctionnalités
- Champ exigé selon le client
- Validation de format
- Répétition sur BL et facture
- Liste des ventes sans référence
- Statistique des retards de règlement liés

## Dépendances
- `sale`, `account`, `mail`
