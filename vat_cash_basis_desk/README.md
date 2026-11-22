# TVA Encaissement vs Débits (vat_cash_basis_desk)

Moteur de TVA sur encaissements : bascule automatique par facture (régime du client), journal TVA à l'encaissement, état des TVA dues/non dues et régularisation des impayés.

## Problème
Sous le régime encaissement (FR, BE,…) la TVA devient due au paiement : la bascule entre base et encaissement est gérée à la main.

## Fonctionnalités
- Bascule automatique par régime
- Journal TVA à l'encaissement
- Régularisation des impayés
- État de conformité annuel
- Paramétrage par pays

## Dépendances
- `account`, `mail`
