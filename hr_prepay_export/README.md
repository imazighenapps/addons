# Pré-Paie pour Prestataire (hr_prepay_export)

Export de pré-paie structuré : collecte des absences, heures validées, primes et éléments variables dans un fichier normalisé, avec contrôle de cohérence avant envoi.

## Problème
Les PME en Community paient un cabinet de paie : elles lui envoient des éléments variables en fichiers improvisés qui génèrent des allers-retours d'erreurs.

## Fonctionnalités
- Fichier structuré normalisé
- Collecte automatique des éléments
- Contrôle de cohérence avant envoi
- Historique des envois
- Retour du cabinet tracé

## Dépendances
- `hr`, `hr_holidays`, `hr_attendance`, `mail`
