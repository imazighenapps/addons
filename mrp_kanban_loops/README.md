# Boucles Kanban Internes (mrp_kanban_loops)

Boucles Kanban entre étapes : cartes de réapprovisionnement, dimensionnement du tampon calculé sur la consommation, alerte quand le stock tampon dérive.

## Problème
Le réapprovisionnement des postes de travail se déclenche trop tard ou trop tôt : les tampons intermédiaires ne sont ni dimensionnés ni pilotés.

## Fonctionnalités
- Cartes Kanban par boucle
- Dimensionnement du tampon calculé
- Déclenchement de MOs par carte
- Alerte de dérive du tampon
- Statistiques de consommation

## Dépendances
- `mrp`, `stock`, `mail`
