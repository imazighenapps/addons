# Brésil NF-e/NFS-e (br_nfe_pack)

Connecteur NF-e/NFS-e : génération, envoi SEFAZ, protocoles, denegations et lettres de correction.

## Problème
Les émissions brésiliennes NF-e/NFS-e exigent des XML d'états spécifiques avec protocoles d'autorisation.

## Fonctionnalités
- Génération XML NF-e
- SEFAZ + protocole d'autorisation
- Lettre de correction (CC-e)
- Gestion des denegations

## Dépendances
- `account`, `mail`

## Notes QA
Génération/export/validation et journal de conformité testables localement. Les transmissions API/certificats gouvernementaux externes ne sont pas effectuées sur la VM QA.
