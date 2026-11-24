# Export FEC France (imz_fr_fec_export)

Générateur de **FEC** (Fichier des Écritures Comptables) conforme à l'article
**A47 A-1 du LPF** pour les contrôles fiscaux en France.

## Fonctionnalités

- Export FEC **18 champs obligatoires** (format BOI-FECPAT) + 3 colonnes de
  devise optionnelles (Monteuro, Montantdevise, Idevise)
- Sélection par **période** et **journaux** (vide = tous)
- **Totaux de contrôle** affichés avant téléchargement : nombre
  d'enregistrements, nombre d'écritures, total débit, total crédit
- Numérotation **chronologique par journal** (`EcritureNum` / `CompNumMvt`)
- **Lettrage** exporté (`EcritureLet`, `DateLet`)
- Auxiliaire des tiers (`CompAuxNum` / `CompAuxLib`) pour receivable/payable
- Fichier `SIRENFECYYYYMMDD` (SIREN extrait du numéro de TVA)
- Séparateur **tabulation** ou **pipe**, encodage **ANSI (cp1252)** ou UTF-8
- Rejouable à tout moment, filtrage multi-sociétés

## Utilisation

Comptabilité → Rapports → **Export FEC France** : choisir la période, les
options de format, cliquer **Générer le FEC**, vérifier les totaux de
contrôle puis **Télécharger le fichier FEC**.

## Dépendances

- `account`, `l10n_fr`

## Tests

6 tests fonctionnels (`odoo/tests`) : structure d'en-tête, équilibre débit/
crédit, formats de champs, auxiliaire et séparateur pipe, erreur sur période
vide, contrainte d'ordre des dates.
