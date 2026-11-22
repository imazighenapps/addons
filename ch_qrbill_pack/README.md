# QR-bill Suisse (ch_qrbill_pack)

Génération de QR-bill (payload structuré) pour factures, références de paiement et journal.

## Fonctionnalités
- Génération du fichier/XML de conformité
- Workflow de statuts (brouillon → prête → envoyée → acceptée/refusée)
- Journal des statuts, identifiant externe, archivage du fichier

## Dépendances
- `account`, `mail`

## Tests
- Génération du document et transitions de statut.
