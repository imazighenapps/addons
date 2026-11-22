# Export SAF-T Multi-Pays (saft_export_pack)

Générateur **SAF-T** (Standard Audit File for Tax purposes, spécification
OECD) paramétrable pour les pays qui l'exigent : **Portugal, Autriche,
Luxembourg, Norvège** et tout pays à venir par simple configuration.

## Fonctionnalités

- **Profils par pays** (`saft.country.profile`) : namespace XML, version de
  schéma, base comptable fiscale ; un profil par pays et société (contrainte
  d'unicité)
- **Mapping des comptes** (`saft.account.map`) : `AccountType` SAF-T par
  compte (20 valeurs de l'énumération OECD) ; fallback automatique par
  groupe interne Odoo (`income` → `SalesRevenue`, etc.) ; option « mapping
  explicite exigé »
- **Mapping des taxes** (`saft.tax.map`) : code, type (VAT/Other) et taux
  attendus par l'administration
- Génération : **Header** (SIREN/VAT, adresse, exercice), **MasterFiles**
  (comptes avec soldes d'ouverture/clôture, clients, fournisseurs, table de
  taxes), **GeneralLedgerEntries** (toutes les écritures validées de la
  période, totaux débit/crédit)
- **Contrôles de complétude** avant génération : comptes et taxes utilisés
  sans mapping, exigence de mapping explicite, écritures trouvées
- **Journal des dépôts** : historique des exports (fichiers archivés,
  totaux, dates de génération), séquence `SAFT/YYYY/####`

## Utilisation

1. Comptabilité → Configuration → **Profils pays SAF-T** : créer le profil
   du pays, configurer les mappings comptes/taxes
2. Comptabilité → Rapports → **Export SAF-T** : créer un export (période,
   profil), cliquer **Contrôles de complétude** puis **Générer le fichier
   SAF-T**
3. Télécharger le XML depuis l'enregistrement (journal des dépôts conservé)

## Dépendances

- `account`

## Tests

8 tests fonctionnels : structure XML et namespace, totaux, fallback et
mapping explicite des comptes, contrôles de complétude, table de taxes,
fichier clients, erreur période vide, contraintes (dates, unicité mapping).
