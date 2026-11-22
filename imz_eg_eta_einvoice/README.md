# Égypte e-Invoice ETA (eg_eta_einvoice)

Connecteur ETA : soumission JSON, statuts, codes produits/services ETA et réconciliation des rejets.

## Problème
L'Égypte impose la plateforme ETA pour les émissions B2B.

## Fonctionnalités
- Soumission JSON ETA
- Codes produits/services ETA
- Statuts et rejets
- Journal de conformité

## Dépendances
- `account`, `mail`

## Notes QA
Génération/export/validation et journal de conformité testables localement. Les transmissions API/certificats gouvernementaux externes ne sont pas effectuées sur la VM QA.
