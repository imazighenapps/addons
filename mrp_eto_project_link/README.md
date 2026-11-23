# Fabrication à la Commande Projet (mrp_eto_project_link)

Liaison commande → projet → MOs : tous les coûts (matière, heures, sous-traitance) rattachés au lot projet, rentabilité par commande et alerte de dérive.

## Problème
Sur les commandes sur mesure, les MOs, achats et heures de conception ne sont reliés ni à la commande ni au projet : la rentabilité unitaire est inconnue.

## Fonctionnalités
- Création automatique du projet par commande
- Rattachement des MOs et achats
- Coût consolidé par commande
- Marge projetée vs réalisée
- Alerte de dérive en cours de fabrication

## Dépendances
- `mrp`, `project`, `sale`, `purchase`, `mail`
