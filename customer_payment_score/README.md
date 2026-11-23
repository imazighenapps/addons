# Score de Risque Client (customer_payment_score)

Score de risque interne : retards historiques, incidents, ancienneté, taux d'encaissement → score, plafond suggéré et alerte de dégradation.

## Problème
Accorder un crédit se fait au ressenti ; l'historique de paiement réel du client n'est pas exploité.

## Fonctionnalités
- Score calculé sur l'historique réel
- Plafond suggéré
- Alerte de dégradation
- Comparaison inter-clients
- Journal de décision

## Dépendances
- `account`, `mail`
