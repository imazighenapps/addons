# e-Invoicing Portugal SAF-T Fact (pt_saft_einvoice)

Pack PT : ATCUD, QR code obligatoire, export SAF-T mensuel et rapprochements de conformité.

## Problème
Le Portugal combine SAF-T comptable mensuel et transmission ATCUD/QR sur les factures.

## Fonctionnalités
- ATCUD sur documents
- QR code PT conforme
- Export SAF-T mensuel
- Journal de conformité

## Dépendances
- `account`, `mail`

## Notes QA
Génération/export/validation et journal de conformité testables localement. Les transmissions API/certificats gouvernementaux externes ne sont pas effectuées sur la VM QA.
