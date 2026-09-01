# EduFlow — Guide utilisateur

Ce guide couvre les fonctionnalités livrées suite à l'analyse du cahier des
charges (lots F0 à F5). Il complète le README technique.

## 1. Installation

1. Copier `eduflow/` (et, si le module RH est utilisé, `eduflow_hr_bridge/`)
   dans le dossier `addons` de l'instance Odoo 18.
2. Activer le mode développeur, mettre à jour la liste des applications.
3. Installer **EduFlow - School Management**. Aucune dépendance à `hr`
   n'est nécessaire (F0.1) : si le module Employés est installé, le pont
   `eduflow_hr_bridge` s'installe automatiquement et ajoute le lien
   `Employee Record` sur la fiche enseignant.
4. Dans **Réglages générale > EduFlow**, configurer :
   - la synchronisation comptable des paiements (F1.2),
   - le blocage d'acceptation d'admission sur dossiers incomplets (F3.3),
   - les paliers de relance des frais (F1.3),
   - la mention légale des bulletins.

## 2. Guide par profil

### Administrateur (`group_eduflow_admin`)
Accès complet, y compris la configuration (années scolaires, niveaux,
types de frais et leur paramétrage comptable, types de documents
d'admission, paramètres EduFlow).

### Direction (`group_eduflow_direction`)
- **Tableau de bord** : KPI en direct (effectifs, absentéisme, moyenne
  générale, finances) et **Historique des indicateurs** (F2.6) pour suivre
  leur évolution dans le temps (graphique).
- Accès en lecture à l'essentiel des modules pédagogiques et financiers,
  droit de dévalider un examen si nécessaire.

### Administration scolaire (`group_eduflow_administration`)
- Gestion des admissions : la vue **Kanban** (F2.3) permet de faire glisser
  les dossiers d'une étape à l'autre (Nouvelle demande → Étude → Entretien
  → Acceptée/Refusée). L'onglet **Documents requis** (F3.3) liste les
  pièces à fournir ; le dossier ne peut être accepté tant qu'elles ne sont
  pas cochées "Reçu" si l'option a été activée dans les Paramètres.
- Gestion des inscriptions, classes, emploi du temps (vue **Calendrier**,
  F2.4).

### Enseignant (`group_eduflow_teacher`)
- Menu **Pédagogie > Faire l'appel** (F2.1) : choisir sa classe et la date,
  la liste des élèves inscrits est pré-remplie en "Présent", il suffit de
  corriger les absences puis de valider en un clic.
- Sur une fiche **Examen**, le bouton **Générer la grille de notes** (F2.2)
  crée une ligne de note à zéro pour chaque élève de la classe ; il suffit
  de compléter la colonne "Note". Une fois l'examen **Validé**, les notes
  sont verrouillées pour les enseignants (message d'erreur explicite) —
  seules la Direction/Administration/Admin peuvent encore les corriger.
- **Portail > Mon espace enseignant** (F3.2) : emploi du temps de la
  semaine et accès rapide à ses classes depuis le portail web.

### Comptable (`group_eduflow_accountant`)
- **Finance > Types de frais** : paramétrer le compte de revenu, le
  journal de vente et les taxes à appliquer par type de frais (F1.1).
- Sur une fiche **Frais / Échéance**, bouton **Créer la facture** :
  génère une facture client Odoo standard pour le tuteur financier de
  l'élève. Un frais déjà facturé ne peut pas l'être une seconde fois.
- Lors de la confirmation d'un **Paiement**, si le frais est facturé et
  que la synchronisation comptable est activée, un `account.payment` est
  automatiquement créé et lettré avec la facture (F1.2). L'annulation du
  paiement annule et délettre l'écriture comptable correspondante.
- Le paiement en ligne (F1.4) réutilise le bouton **"Pay Now"** standard
  des factures Odoo : depuis le portail parent, le lien **Pay Online**
  d'un frais facturé ouvre directement la page portail de la facture.
  Tout règlement effectué là (ou via tout autre mode de paiement
  comptable) remonte automatiquement dans EduFlow comme paiement
  confirmé, sans double-saisie.
- Relances automatiques (F1.3) : une tâche planifiée quotidienne envoie
  un rappel aux tuteurs financiers aux échéances configurées (par défaut
  J-7 / J0 / J+7), sans jamais doubler un rappel déjà envoyé.

### Parent (portail, `group_eduflow_parent_portal`)
- **Mes enfants** : fiche par enfant avec infos, emploi du temps,
  présences, bulletins publiés et suivi des frais/paiements, incluant le
  bouton **Pay Online** dès qu'une facture est disponible.

## 3. Multi-société (F4.1)

Tous les modèles transactionnels (élève, enseignant, classe, inscription,
matière, examen, note, présence, frais, paiement, admission, programme,
bulletin, type de frais) sont désormais soumis à une règle de séparation
par société : un utilisateur ne voit et ne modifie que les données des
sociétés auxquelles il a accès.

## 4. Limites connues / axes d'amélioration

- **F1.4** a été volontairement simplifié : plutôt qu'un tunnel de
  paiement dédié, EduFlow s'appuie sur le flux "Payer maintenant" natif
  des factures Odoo (nécessite un fournisseur de paiement configuré dans
  **Paramètres > Paiements**).
- **i18n (F4.4)** : un fichier `i18n/eduflow.pot` complet a été généré,
  ainsi qu'un `i18n/fr.po` couvrant les libellés les plus visibles (menus,
  statuts, boutons). Une relecture/complément par un traducteur natif est
  recommandée avant mise en production pour les libellés de champs les
  plus spécifiques.
- Les tests automatisés (`tests/`) couvrent les scénarios critiques des
  lots F0-F4 mais n'ont pas pu être exécutés dans cet environnement
  (absence d'instance Odoo 18 démarrée) ; ils sont écrits selon les
  conventions déjà en place dans le module (`tests/common.py`) et prêts à
  être lancés via `--test-enable --test-tags eduflow`.
