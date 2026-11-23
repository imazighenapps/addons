# Gardien de Sauvegardes (backup_keeper)

Gestionnaire de sauvegardes : dump planifié, rotation, copie hors site (S3/SFTP) et test de restauration périodique avec preuve.

## Problème
Les sauvegardes Odoo sont promis sans être testés : le jour du sinistre, la restauration échoue.

## Fonctionnalités
- Dump planifié
- Rotation et rétention
- Copie hors site
- Test de restauration
- Preuve datée

## Dépendances
- `base`, `mail`
