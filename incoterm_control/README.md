# Contrôle des Incoterms par Commande (incoterm_control)

Incoterm imposé par commande : contrôles de cohérence à la facturation (frais attendus côté acheteur ou vendeur), alerte sur les frais inattendus et rapport des dérives.

## Problème
L'incoterm choisi détermine qui paie quoi (fret, assurance, douane), mais n'est jamais vérifié à la facturation : les coûts arrivent du mauvais côté.

## Fonctionnalités
- Incoterm obligatoire par commande
- Règles de frais attendus
- Alerte sur frais inattendus
- Rapport des dérives par fournisseur
- Historique des choix

## Dépendances
- `purchase`, `account`, `mail`
