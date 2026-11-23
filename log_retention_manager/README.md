# Rétention des Logs (log_retention_manager)

Politique de rétention par type de log : archivage compressé, expiration, extraction à la demande et journal de conformité.

## Problème
Les logs Odoo grossissent sans limite : disques saturés, recherche lente, rétention réglementaire non respectée.

## Fonctionnalités
- Rétention par type de log
- Archivage compressé
- Expiration planifiée
- Extraction à la demande
- Journal de conformité

## Dépendances
- `base`, `mail`
