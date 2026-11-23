# Temps de Transfert Inter-Postes (mrp_move_time_tracking)

Enregistrement du temps de transfert entre opérations avec motif (attente, contrôle, transport), calcul du temps hors-production et identification des routes les plus lentes.

## Problème
Le temps de déplacement des pièces entre postes (attente, transfert, contrôle) est invisible et fausse les délais d'atelier.

## Fonctionnalités
- Saisie du transfert à la fin d'opération
- Motifs de temps non productif
- Temps inter-opérations par route
- Classement des routes les plus lentes
- Rapport par semaine et par poste

## Dépendances
- `mrp`, `mail`
