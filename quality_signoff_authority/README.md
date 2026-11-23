# Habilitations de Signature Qualité (quality_signoff_authority)

Matrice d'autorité de signature : par type de décision (libération, FAI, waiver, disposition) et par personne, blocage des signatures hors habilitation et journal des décisions.

## Problème
N'importe quel contrôleur signe n'importe quel type de validation : pas de matrice de qui peut libérer quoi, ni de preuve pour les audits.

## Fonctionnalités
- Matrice décision x habilité
- Blocage des signatures hors champ
- Délégation temporaire tracée
- Journal des signatures
- Rapport d'autorité pour audits

## Dépendances
- `quality`, `mail`
