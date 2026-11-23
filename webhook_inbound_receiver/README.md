# Récepteur de Webhooks Entrants (webhook_inbound_receiver)

Récepteur générique : endpoints configurables, validation de signature, file de traitement, rejeu des échecs et mapping vers modèles Odoo.

## Problème
Recevoir un webhook externe exige un contrôleur dédié par source, avec validation et rejeu manuels.

## Fonctionnalités
- Endpoints configurables
- Validation de signature
- File de traitement asynchrone
- Rejeu des échecs
- Mapping vers modèles

## Dépendances
- `base`, `mail`
