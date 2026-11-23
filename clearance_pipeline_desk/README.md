# Pipeline de Dédouanement (clearance_pipeline_desk)

Pipeline de dédouanement : chaque importation suivie par étapes (dépôt, acceptation, mainlevée), échéances et relances au courtier, lien direct aux réceptions bloquées.

## Problème
Le dédouanement est une boîte noire : la déclaration part au courtier, le statut ne revient jamais, l'entrepôt attend sans information.

## Fonctionnalités
- Étapes par dossier de douane
- Relances au courtier tracées
- Lien aux réceptions en attente
- Ancienneté des dossiers
- Historique des délais par bureau

## Dépendances
- `stock`, `purchase`, `mail`
