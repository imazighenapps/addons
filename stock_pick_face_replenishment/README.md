# Réappro des Faces de Picking (stock_pick_face_replenishment)

Réapprovisionnement interne des emplacements de préparation : min/max par face, génération de transferts bulk→picking, alerte avant rupture de face et suivi de l'attente.

## Problème
Les faces de picking se vident en pleine journée : les préparateurs partent chercher en réserve, perdant du temps, ou pire, livrent des quantités fausses.

## Fonctionnalités
- Min/max par emplacement de picking
- Transferts internes générés
- Alerte avant rupture de face
- Priorisation des réappro
- Mesure du temps d'attente

## Dépendances
- `stock`, `mail`
