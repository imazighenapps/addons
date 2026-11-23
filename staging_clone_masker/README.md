# Copie d'Environnement Masquée (staging_clone_masker)

Copie d'environnement avec masquage des données personnelles par champ (noms, emails, adresses, montants optionnels), prête au test.

## Problème
Cloner la prod vers un environnement de test expose des données personnelles réelles aux développeurs.

## Fonctionnalités
- Masquage par champ paramétrable
- Jeux de données factices cohérents
- Contrôle avant remise
- Journal de copie
- Réutilisation des masques

## Dépendances
- `base`, `mail`
