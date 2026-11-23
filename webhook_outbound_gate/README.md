# Webhooks Sortants (webhook_outbound_gate)

Passerelle de webhooks sortants : déclencheurs par modèle et événement, payload paramétré, signature HMAC, retries avec backoff et journal de livraison.

## Problème
Envoyer un webhook à chaque événement Odoo exige du code : pas d'outil générique avec retries et signatures.

## Fonctionnalités
- Déclencheurs par modèle/événement
- Payload paramétrable
- Signature HMAC
- Retries avec backoff
- Journal de livraison consultable

## Dépendances
- `base`, `mail`
