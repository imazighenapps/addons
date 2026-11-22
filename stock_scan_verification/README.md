# Contrôle de Scan au Picking (stock_scan_verification)

Scan obligatoire au picking : validation par scan du produit (ou emplacement) avant confirmation, tolérances configurables, blocage des lignes non vérifiées et journal des écarts.

## Problème
Sur Odoo Community, le préparateur peut valider des lignes sans scanner : les erreurs de produit partent chez le client.

## Fonctionnalités
- Scan obligatoire par ligne
- Blocage des validations non scannées
- Tolérances et exceptions
- Journal des écarts de scan
- Statistiques d'erreurs évitées

## Dépendances
- `stock`, `mail`
