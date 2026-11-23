# Écarts de Change Réalisés (realized_fx_settlement)

Traitement automatique des écarts réalisés : calcul au taux du jour de règlement, écriture d'écart de change, option de saut d'écart et statistiques par devise.

## Problème
Les écarts de change réalisés à l'encaissement/paiement sont régularisés à la main, facture par facture.

## Fonctionnalités
- Calcul automatique à l'encaissement
- Écriture d'écart de change
- Saut d'écart sous seuil
- Statistiques de pertes/gains par devise
- Journal d'audit

## Dépendances
- `account`, `mail`
