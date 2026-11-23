# Détection d'Anomalies du Grand Livre (ledger_anomaly_scan)

Scanner heuristique du grand livre : scores d'anomalie par écriture, motifs configurables, revue par lots et journal d'investigation.

## Problème
Les écritures anormales (montants ronds inhabituels, écritures weekend, paires inversées, comptes rares) ne sont détectées qu'à l'audit.

## Fonctionnalités
- Heuristiques configurables
- Score d'anomalie par écriture
- Revue par lots avec décisions
- Journal d'investigation
- Rapport mensuel

## Dépendances
- `account`, `mail`
