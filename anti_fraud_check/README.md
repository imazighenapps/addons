# Contrôle Anti-Fraude à la Commande (anti_fraud_check)

Score anti-fraude à la commande : règles de risque (ancienneté, mode de paiement, urgence, incohérences d'adresse), revue manuelle obligatoire au-dessus du seuil et journal des décisions.

## Problème
Nouveau client, première commande, montant élevé, paiement atypique : les fraudes se voient après livraison et le préjudice est fait.

## Fonctionnalités
- Règles de risque configurables
- Score à la commande
- Revue manuelle au-dessus du seuil
- Journal des décisions
- Statistique des fraudes évitées

## Dépendances
- `sale`, `payment`, `mail`
