# SEPA Paiements Out (sepa_credit_transfer)

Génération de lots de virements SEPA (pain.001.001.03) depuis les paiements sortants Odoo, avec contrôles IBAN/BIC, identifiants uniques, historique des fichiers et import des rejets (pain.002).

## Dépendances
- `account`, `mail`

## Fonctionnalités
- Session de paiement multi-factures (sélection de paiements)
- Validation IBAN/BIC avant génération
- MsgId/PmtInfId uniques, fichier XML téléchargeable
- Import pain.002 (marquage rejets + journalisation)
- Suivi d'état (brouillon, généré, transmis, rejeté)

## Utilisation
Menu **Comptabilité → Virements SEPA → Lots de virements (pain.001)**. Configurer l'IBAN/BIC sur le journal bancaire et sur les comptes bancaires bénéficiaires.

## Internationalisation
7 langues : en_US, fr_FR, ar_001, es_ES, de_DE, pt_BR, zh_CN.

## Licence
LGPL-3
