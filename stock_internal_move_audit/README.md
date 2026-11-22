# Audit des Mouvements Internes (stock_internal_move_audit)

Contrôle des mouvements internes : motif obligatoire sur les transferts sans origine (réception, commande, OF), journal d'audit et rapport des mouvements inexpliqués.

## Problème
Des transferts internes se font sans motif ni justification : le stock bouge, personne ne sait pourquoi, et les audits s'en aperçoivent.

## Fonctionnalités
- Motif obligatoire configurable
- Journal d'audit tracé
- Rapport des mouvements inexpliqués
- Statistiques par type de motif
- Vieillissement des exceptions

## Dépendances
- `stock`, `mail`
