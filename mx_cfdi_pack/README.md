# Mexique CFDI 4.0 (mx_cfdi_pack)

Connecteur CFDI : timbrage PAC, compléments de paiement, annulation avec motifs SAT et réception des CFDI fournisseurs.

## Problème
Le Mexique impose le CFDI 4.0 avec compléments de paiement et gestion du statut SAT.

## Fonctionnalités
- Timbrage CFDI 4.0 via PAC
- Complément de paiement
- Annulation avec motifs
- Consultation statut SAT

## Dépendances
- `account`, `mail`

## Notes QA
Génération/export/validation et journal de conformité testables localement. Les transmissions API/certificats gouvernementaux externes ne sont pas effectuées sur la VM QA.
