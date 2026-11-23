# Contrôle de Complétude des Opportunités (opportunity_gate_fields)

Barrière de complétude : champs obligatoires conditionnels par étape, blocage du passage d'étape tant que les données manquent et score de fiabilité des données CRM.

## Problème
Les opportunités avancent avec des champs clés vides (montant, date cible, décideur) : la prévision et le pilotage restent faux.

## Fonctionnalités
- Champs obligatoires conditionnels par étape
- Blocage du passage d'étape
- Score de complétude par opportunité
- Rapport de fiabilité des données
- Exemption justifiée

## Dépendances
- `crm`, `mail`
