# Sauvegardes & Restauration Testée (db_backup_scheduler)

Planificateur de sauvegardes avec rotation de rétention, contrôle d'intégrité, alerte d'échec et test de restauration périodique en bac à sable.

## Problème
Les sauvegardes d'instances Odoo sont faites « quand on y pense » et personne ne teste jamais que le fichier se restaure.

## Fonctionnalités
- Planification avec rotation de rétention
- Alerte d'échec et de silence
- Contrôle d'intégrité des dumps
- Test de restauration périodique
- Journal des exécutions

## Dépendances
- `base`, `mail`
