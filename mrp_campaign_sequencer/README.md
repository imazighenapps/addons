# Séquenceur de Campagnes par Ligne (mrp_campaign_sequencer)

Séquenceur qui regroupe les MOs par famille ou caractéristique commune et propose un ordre de lancement minimisant les réglages, avec un temps de changement économisé chiffré.

## Problème
Produire des références dans un ordre aléatoire multiplie les changements de gamme ; l'ordre de lancement n'est jamais optimisé par famille produit.

## Fonctionnalités
- Regroupement par famille ou attribut
- Ordre de lancement proposé
- Gain de temps de changement estimé
- Priorités client respectées
- Jeu de MOs appliqué en un clic

## Dépendances
- `mrp`, `mail`
