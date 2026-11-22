# Export TIE Italie (it_tie_audit_export)

Export d'audit **TIE** depuis les écritures Odoo pour les contrôles en
Italie, avec mapping des registres fiscaux et journal des dépôts.

## Fonctionnalités

- **Mapping des registres fiscaux** (`tie.registry.map`, un par registre et
  société) : registre IVA ventes, registre IVA achats, corrispettivi,
  journal général, registre des amortissements → journaux Odoo
- **Génération par période** : CSV structuré point-virgule, UTF-8
  - Ligne 1 : `TIE;<codice_fiscale>;<dal>;<al>;<version>`
  - Ligne 2 : 12 colonnes normalisées (RegistroFiscale, CodiceJournal,
    Data, NumeroDocumento, CodiceConto, DescrizioneConto, Parte D/A,
    Importo, ParteId, PartnerCodiceFiscale, PartnerRagioneSociale,
    Descrizione)
  - Dernière ligne : `TOT;<nb>;<totdebito>;<totcredito>`
- **Contrôles de complétude** : tout journal de la période doit être mappé
  à un registre fiscal (blocant) ; contournement explicite avec registre
  `NON_MAPPATO` et avertissement tracé
- **Journal des dépôts** : statut `Brouillon → Généré → Déposé` avec date
  de dépôt, utilisateur et chatter ; historique complet des exports
- Fichier `TIE_<codicefiscale>_<AAAAMMJJ>_<AAAAMMJJ>.csv`, montants à la
  virgule (usage italien)

## Utilisation

1. Comptabilité → Configuration → **Registres fiscaux TIE** : mapper les
   journaux Odoo aux registres fiscaux italiens
2. Comptabilité → Rapports → **Export TIE Italie** : créer l'export
   (période, journaux), contrôler la complétude, générer, puis **Tracer le
   dépôt** après transmission

## Dépendances

- `account`

## Tests

7 tests fonctionnels : blocage sans mapping, génération avec mapping
(structure, colonnes, totaux), contournement NON_MAPPATO, rapport de
complétude, journal des dépôts, unicité du registre par société, contrainte
de dates.
