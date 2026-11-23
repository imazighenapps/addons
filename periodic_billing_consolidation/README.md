# Facturation Consolidée Périodique (periodic_billing_consolidation)

Consolidation périodique : cumul des livraisons de la période du client en une facture détaillée par BL, avec prorata des remises et contrôle du total.

## Problème
Facturer chaque BL à part multiplie les documents et les frais pour les clients récurrents : ils demandent une facture mensuelle consolidée, montée à la main.

## Fonctionnalités
- Consolidation des livraisons de la période
- Détail par BL dans la facture
- Prorata des remises
- Contrôle du total consolidé
- Calendrier de facturation par client

## Dépendances
- `sale`, `account`, `stock`, `mail`
