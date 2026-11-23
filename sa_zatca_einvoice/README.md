# ZATCA Arabie Saoudite (sa_zatca_einvoice)

Connecteur ZATCA : génération XML, signature cryptographique, transmission API, statuts et re-clearance.

## Problème
La ZATCA saoudienne impose la Phase 2 (intégration en temps réel avec QR, UUID, hash chaîné).

## Fonctionnalités
- Génération XML ZATCA Phase 2
- Signature + hash chaîné
- API clearence et reporting
- Statuts et anomalies

## Dépendances
- `account`, `mail`

## Notes QA
Génération/export/validation et journal de conformité testables localement. Les transmissions API/certificats gouvernementaux externes ne sont pas effectuées sur la VM QA.
