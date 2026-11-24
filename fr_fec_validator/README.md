# Validateur FEC (fr_fec_validator)

Contre-expertise d'un fichier **FEC** avant transmission au Liasse Fiscal :
**25+ contrôles réglementaires** sur n'importe quel fichier FEC exporté.

## Contrôles exécutés

| Famille | Contrôles |
|---|---|
| Structure | séparateur détecté, 18 colonnes, noms d'en-tête exacts et ordre réglementaire, colonnes non réglementaires, comptage de colonnes par ligne |
| Champs | présence des 11 champs obligatoires, longueurs max réglementaires (BOI-FECPAT) |
| Dates | AAAAMMJJ calendaire (EcritureDate, PieceDate, DateLet, ValidDate), ValidDate ≥ EcritureDate, DateLet si EcritureLet |
| Montants | numériques à la virgule, non négatifs, pas de ligne à montant nul (avertissement), pas de débit/crédit simultanés (avertissement) |
| Balance | total débit = total crédit (écart toléré 0,05) |
| Séquence | EcritureNum croissant par journal, unicité (journal, date, numéro) |
| Cohérence | CompNumMvt unique par pièce (avertissement) |

## Résultat

- Rapport d'anomalies **pointé sur les écritures** : n° de ligne du fichier,
  champ concerné, type, sévérité, message explicite, référence de pièce avec
  bouton **Ouvrir l'écriture**.
- Statuts : `Conforme` (0 erreur) / `Anomalies`.
- **Historique des validations** conservé (modèle stocké + chatter).

## Utilisation

Comptabilité → Rapports → **Validateur FEC** : créer un contrôle, charger le
fichier, cliquer **Analyser le fichier**, corriger les erreurs, re-valider.

## Dépendances

- `account`

## Tests

6 tests fonctionnels : fichier conforme, écart de balance, longueurs et
dates, numériques et séquence, pointage sur l'écriture, champs d'en-tête
manquants.
