# Plan de Transport Quotidien (dispatch_board_desk)

Tableau de dispatch : expéditions du jour affectées à véhicule et chauffeur avec contrôle de charge, régimes d'exception (retard, refus), et statut de départ en temps réel.

## Problème
L'affectation des expéditions aux véhicules et chauffeurs se fait au tableau blanc : conflits invisibles jusqu'au matin de départ.

## Fonctionnalités
- Vue du jour par véhicule et chauffeur
- Contrôle de charge à l'affectation
- Statuts et exceptions en direct
- Réaffectation en un glisser
- Journal des décisions

## Dépendances
- `stock`, `sale`, `mail`
