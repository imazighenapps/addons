# Export GoBD Allemagne (de_gobd_export)

Génère un export **GoBD (GDPdU)** pour les audits fiscaux allemands.

## Fonctionnalités

- **Index XML** (`index.xml`) décrivant les tables/champs (format GDPdU / variable length, UTF-8, séparateur `;`)
- **Données comptables** : écritures validées de la période exportées en `journal_entries.csv` (11 colonnes : pièce, date, journal, compte, libellés, partenaire, débit, crédit, devise)
- **Archive ZIP** téléchargeable regroupant index + données
- **Protocole de remise** daté et **journal des exports** (historique, fichier archivé, totaux débit/crédit, nombre d'écritures/lignes)
- Sélection par période, société et journaux ; contrôles de cohérence (période, absence d'écritures)

## Utilisation

Comptabilité → Rapports → **Export GoBD Allemagne** : créer un export, choisir la période/journaux, cliquer **Générer l'export GoBD**, puis télécharger l'archive.

## Dépendances

- `account`, `mail`

## Tests

3 tests fonctionnels : génération ZIP + structure index/données + protocole, erreur période vide, contrainte d'ordre des dates.
