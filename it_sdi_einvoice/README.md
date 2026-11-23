# e-Invoicing Italie SdI (it_sdi_einvoice)

Génération FatturaPA et suivi des statuts SdI pour les factures vers l'Italie.

## Fonctionnalités
- Génération XML **FatturaPA** (FPR12/FPA12, codice destinatario/PEC, données émetteur/destinataire/lignes)
- Suivi des statuts : brouillon → prête → envoyée → délivrée/acceptée/refusée
- Ré-émission après refus, journal des statuts, identifiant SdI
- Un document par facture (contrainte d'unicité), contrôles (destinataire 7 caractères)

## Dépendances
- `account`, `mail`

## Tests
3 tests : génération/structure XML, flux de statuts et refus, contrainte codice destinatario.
