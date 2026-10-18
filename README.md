# Hygie Sanitaire

Plateforme numérique de gestion d'un service de lavage automobile mobile destiné aux résidences d'Abidjan (Côte d'Ivoire).

**Statut : développement actif du backend.** L'analyse et la modélisation (MERISE + UML) sont terminées. Le backend Django est actuellementc onstruit application par application.

Dernière mise à jour du README : dimanche 18 octobre 2026 (voir le [journal des étapes](#14-journal-des-étapes)).

---

## Table des matières

1. [Présentation](#1-présentation)
2. [Surfaces de la plateforme](#2-surfaces-de-la-plateforme)
3. [Stack technique](#3-stack-technique)
4. [Structure du dépôt](#4-structure-du-dépôt)
5. [Architecture du backend](#5-architecture-du-backend)
6. [Rôles, comptes et authentification](#6-rôles-comptes-et-authentification)
7. [Modèle de données et règles de gestion](#7-modèle-de-données-et-règles-de-gestion)
8. [Diagrammes](#8-diagrammes)
9. [Décisions d'architecture](#9-décisions-darchitecture)
10. [Installation et lancement](#10-installation-et-lancement)
11. [Points d'accès de l'API](#11-points-daccès-de-lapi)
12. [Avancement et feuille de route](#12-avancement-et-feuille-de-route)
13. [Points ouverts](#13-points-ouverts)
14. [Journal des étapes](#14-journal-des-étapes)
15. [Conventions de travail](#15-conventions-de-travail)
16. [Auteur et licence](#16-auteur-et-licence)

---

## 1. Présentation

Hygie Sanitaire propose le lavage de véhicules directement au domicile des clients, dans des résidences (compounds). De petites équipes d'agents interviennent pendant les heures creuses :

| Créneau | Horaires |
|---|---|
| Matin | 4h à 6h30 |
| Soir | 20h à 00h |

La plateforme permet aux clients de réserver ou de s'abonner, aux agents de recevoir et d'exécuter des missions, et à l'équipe de gestion de piloter l'activité (zones, tarifs, paiements, statistiques).

Les comptes Administrateur peuvent recevoir des droits restreints. Cette conception vise une éventuelle commercialisation de la solution à d'autres sociétés de lavage.

---

## 2. Surfaces de la plateforme

| Surface | Technologie | Utilisateurs | État |
|---|---|---|---|
| Application mobile (iOS et Android) | Flutter | Clients et Agents | Non commencée |
| Back-office web | Next.js | Chefs d'équipe et Administrateurs | Non commencé |
| Site vitrine public | Next.js (projet partagé avec le back-office) | Public | Non commencé |

Les trois surfaces s'appuient sur la même API, fournie par le backend Django.

Reporté à une phase ultérieure :

- le paiement par mobile money (Wave, Orange Money, MTN Money) : en attendant, les statuts de paiement sont gérés manuellement depuis le back-office ;
- l'intégration Odoo.

---

## 3. Stack technique

### Backend

| Composant | Version / détail |
|---|---|
| Python | 3.13.7 |
| Django | 5.2 LTS (5.2.17 dans `requirements.txt`) |
| Django REST Framework | 3.18.0 |
| Authentification | djangorestframework-simplejwt 5.5.1 (contrainte `>=5.5.1` volontaire : elle corrige la faille PYSEC-2026-1305, liée à la désactivation des comptes agents) |
| Documentation d'API | drf-spectacular 0.30.0 |
| Configuration | django-environ 0.14.0 |
| Base de données | PostgreSQL 16, pilote psycopg 3.3.5 (`psycopg[binary]`) |
| CORS | django-cors-headers 4.9.0 |
| Images | Pillow 12.3.0 |

Réglages Django : langue `fr`, fuseau horaire `Africa/Abidjan`, clés primaires `BigAutoField`.

### Web (back-office et site vitrine)

Next.js 16, Tailwind CSS v4, shadcn/ui, Motion, TanStack Query, Recharts. Les jetons JWT seront stockés dans des cookies `httpOnly`.

### Mobile

Flutter, ciblant iOS et Android.

---

## 4. Structure du dépôt

Dépôt : [github.com/n1n3t33n/Hygie](https://github.com/n1n3t33n/Hygie). Branche principale : `main`.

Le dépôt contient l'ensemble du back-end du projet. Une fois le backend terminé, des branches dédiées seront créées, notamment pour le frontend, le mobile et le web.

```text
Hygie/
├── code/
│   └── hygie_backend/              # Projet Django (racine : manage.py, .env)
│       ├── manage.py
│       ├── requirements.txt
│       ├── .env.example
│       ├── apps/
│       │   ├── comptes/
│       │   ├── reservations/
│       │   ├── paiements/
│       │   ├── missions/
│       │   └── evaluations/
│       └── hygie_backend/          # Paquet de configuration
│           ├── urls.py
│           ├── asgi.py
│           ├── wsgi.py
│           └── settings/           # base.py, development.py, production.py
└── diagrammes/                     # Sources draw.io (.drawio) et exports (.svg, .png)
```

---

## 5. Architecture du backend

Le backend est organisé en cinq applications Django, une par domaine métier, regroupées dans `apps/` :

| App | Rôle | Dépend de |
|---|---|---|
| `comptes` | Utilisateurs, profils (Client, Agent, Administrateur), zones, authentification, permissions | aucune |
| `reservations` | Véhicules, abonnements, réservations | `comptes` |
| `paiements` | Paiements et tarifs (modèle `Tarif`) | `reservations` |
| `missions` | Missions des agents | `comptes`, `reservations` |
| `evaluations` | Évaluations des missions | `missions` |

Ces dépendances proviennent du diagramme de packages UML. Elles déterminent l'ordre de développement : on commence par l'app dont les dépendances sont déjà terminées.

### Convention fondamentale

Aucune logique métier dans les views. Tout calcul ou règle de gestion (par exemple « créneau libre » ou « date limite d'annulation ») va dans un dossier `services/`, pas dans les views ni directement dans les serializers.

### Migrations

Les cinq apps sont migrées. Les migrations de `missions` et `evaluations` sont scindées en deux passes chacune. Ce comportement est attendu : il vient des clés étrangères croisées entre apps.

---

## 6. Rôles, comptes et authentification

### Rôles

Quatre rôles fonctionnels : `client`, `agent`, `chef_equipe`, `administrateur`.

- `Utilisateur` étend `AbstractUser` sans champ supplémentaire (`AUTH_USER_MODEL = comptes.Utilisateur`).
- `Client`, `Agent` et `Administrateur` sont des profils reliés à `Utilisateur` par une relation un-à-un.
- Le chef d'équipe n'est pas un profil séparé : c'est une variante de `Agent` (choix `agent_laveur` / `chef_equipe`).
- `get_role()` applique la priorité `administrateur > agent > client` et renvoie `None` pour un utilisateur sans profil.
- Un utilisateur n'a qu'un seul profil. Cette exclusivité est vérifiée dans chaque serializer de création.

### Création des comptes

| Profil | Création |
|---|---|
| Client | Inscription publique (nom, prénom, téléphone, zone, point d'eau disponible) |
| Agent | Par un administrateur habilité |
| Administrateur | Par un administrateur disposant de la permission dédiée |

L'ajout d'un véhicule est une étape distincte, après l'inscription.

### Authentification JWT

| Paramètre | Valeur |
|---|---|
| Durée du jeton d'accès | 60 minutes(en developpement) |
| Durée du jeton de rafraîchissement | 30 jours(en developpement) |
| Rotation des jetons de rafraîchissement | Oui |
| Liste noire après rotation | Oui |
| Mise à jour de `last_login` | Oui |

Claims personnalisées implémentées : `username`, `email`, `is_staff`, `is_superuser`. La claim `role` (`client`, `agent`, `chef_equipe`, `administrateur`) est prévue, calculée à partir des profils à la génération du jeton ; son implémentation n'est pas confirmée à ce jour. Les claims `id_zone`, `id_agent` et `id_client` ont été abandonnées (redondantes avec `user_id`).

Par défaut, toute vue de l'API exige un utilisateur authentifié (`IsAuthenticated`).

### Permissions à deux niveaux

1. Le rôle, déterminé par `get_role()`.
2. La capacité, via les Groups et Permissions natifs de Django.

`is_superuser` donne un accès sans restriction (compte d'amorçage du concepteur, créé automatiquement). La permission personnalisée `comptes.creer_administrateur` contrôle la création d'autres administrateurs. Elle n'est jamais attribuée par défaut, uniquement via un groupe.

Groupes d'administrateur créés et vérifiés en base :

- « Administrateur - Gérer les zones »
- « Administrateur - Gérer les utilisateurs »
- « Administrateur - Consulter les statistiques »

Groupe à créer : « Administrateur - Gérer les tarifs ».

---

## 7. Modèle de données et règles de gestion

### Entités principales

| Entité | App | Description |
|---|---|---|
| `Zone` | comptes | Zone de service. Types : `compound_ferme`, `quartier_ouvert` |
| `Client`, `Agent`, `Administrateur` | comptes | Profils liés à `Utilisateur` |
| `Vehicule` | reservations | Immatriculation, type (`citadine`, `berline`, `suv_4x4`, `utilitaire`), lié à un Client |
| `Abonnement` | reservations | Fréquence (`hebdomadaire`, `bimensuelle`, `mensuelle`), date de début et de fin, lié à un Client |
| `Reservation` | reservations | Date, créneau (matin / soir), statut, lié à un Véhicule (0..1) et à un Abonnement (0..1) |
| `Tarif` | paiements | Tarification |

### Règles de gestion des réservations

| Règle | Contenu |
|---|---|
| RG3 | Gestion des créneaux |
| RG4 | Annulation possible jusqu'à la veille |
| RG5 | Le véhicule est optionnel sur une réservation |
| RG6 | Un créneau n'est pas partageable |

### Cycle de vie d'une réservation

`en_attente` puis `confirmee` puis `terminee`, ou `annulee` à tout moment avant la veille.

Les états d'une mission sont dérivés des horodatages (pas de champ de statut littéral).

---

## 8. Diagrammes

Les sources éditables (`.drawio`) et les exports (`.svg`, `.png`) se trouvent dans le dossier [`diagrammes/`](https://github.com/n1n3t33n/Hygie/tree/main/diagrammes).

### 8.1 Diagramme de cas d'utilisation

![Diagramme de cas d'utilisation](diagrammes/Cas%20d'utilisation%20Hygie.drawio.svg)

### 8.2 Diagramme de classes

![Diagramme de classes](diagrammes/Classe%20Hygie.drawio.svg)

### 8.3 Diagramme d'activité

![Diagramme d'activité : parcours](diagrammes/Hygie%20Activit%C3%A9%20Parcours.drawio.svg)

### 8.4 Diagrammes de séquence

**P1. Inscription**

![Séquence : inscription](diagrammes/Hygie%20S%C3%A9quence%20Inscription.drawio.svg)

**P2. Réservation**

![Séquence : réservation](diagrammes/Hygie%20S%C3%A9quence%20R%C3%A9servation.drawio.svg)

**P3. Abonnement**

![Séquence : abonnement](diagrammes/Hygie%20S%C3%A9quence%20Abonnement.drawio.svg)

**P4. Paiement**

![Séquence : paiement](diagrammes/Hygie%20S%C3%A9quence%20Paiement.drawio.svg)

**P5. Planification et exécution**

![Séquence : planification et exécution](diagrammes/Hygie%20S%C3%A9quence%20Planification/Ex%C3%A9cution.drawio.svg)

**P6. Évaluation et signalement**

Disponible dans le dossier [`Hygie Séquence évaluation`](https://github.com/n1n3t33n/Hygie/tree/main/diagrammes/Hygie%20S%C3%A9quence%20%C3%A9valuation).

**P7. Administration et pilotage**

![Séquence : administration et pilotage](diagrammes/Hygie%20S%C3%A9quence%20Administration/Pilotage.drawio.svg)

### 8.5 Diagramme de déploiement

![Diagramme de déploiement](diagrammes/Hygie%20D%C3%A9ploiement.drawio.svg)

### 8.6 Autres diagrammes disponibles

- Merise : [MCD](diagrammes/MCD%20Hygie.drawio.svg), [MCT](diagrammes/MCT%20Hygie.drawio.svg), [MLD](diagrammes/MLD.drawio.svg)
- États : [réservation](diagrammes/Hygie%20Etats%20Reservation.drawio.svg), [mission](diagrammes/Hygie%20Etats%20Mission.drawio.svg)
- UML : [communication](diagrammes/Hygie%20Communication.drawio.svg), [composants](diagrammes/Hygie%20Composants.drawio.svg), [packages](diagrammes/Hygie%20Packages.drawio.svg)

---

## 9. Décisions d'architecture

| Décision | Justification |
|---|---|
| `Administrateur` est un profil dédié (un-à-un avec `Utilisateur`) | Même schéma que `Client` et `Agent` ; extension du modèle MERISE documenté |
| Claim `role` calculée, non stockée | Évite un champ redondant dans la base |
| Capacités des administrateurs via Groups/Permissions Django | Mécanisme natif, aucun nouveau modèle nécessaire |
| Relation SOUSCRIT corrigée de n,n à 1,n | Chaque abonnement appartient à un seul client |
| Clé étrangère `Client` directe sur `Reservation` | Écart assumé par rapport au MCD v3, où le lien passait indirectement par Véhicule ou Abonnement, tous deux optionnels |
| Exclusivité des profils par validation dans les serializers | Choisie plutôt qu'une contrainte multi-tables complexe en base |
| Logique métier dans `services/` | Voir [architecture du backend](#5-architecture-du-backend) |

---

## 10. Installation et lancement

### Prérequis

- Python 3.13.7
- PostgreSQL 16
- Git

### Étapes (backend)

```bash
# 1. Cloner le dépôt et se placer à la racine du projet Django
git clone https://github.com/n1n3t33n/Hygie.git
cd Hygie/code/hygie_backend

# 2. Créer et activer un environnement virtuel
python -m venv venv
# Windows (PowerShell) :
venv\Scripts\Activate.ps1
# Linux / macOS :
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer le fichier d'environnement à partir du modèle
# Windows (PowerShell) :
Copy-Item .env.example .env
# Linux / macOS :
cp .env.example .env

# 5. Créer la base PostgreSQL (nom attendu par défaut : hygie_db), puis
#    renseigner USER et PASSWORD dans DATABASE_URL (fichier .env)

# 6. Appliquer les migrations
python manage.py migrate

# 7. Lancer le serveur de développement
python manage.py runserver

# 8. Lancer les tests
python manage.py test
```

Le fichier `manage.py` utilise par défaut les réglages `hygie_backend.settings.development` (PostgreSQL local via `DATABASE_URL`, `DEBUG=True`).

### Variables d'environnement

Le fichier `.env` se place à la racine du projet Django, à côté de `manage.py`. Le modèle est fourni dans `.env.example`.

```dotenv (.env)
DJANGO_SECRET_KEY=change-me
DEBUG=True
DATABASE_URL=postgres://USER:PASSWORD@localhost:5432/hygie_db
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

| Variable | Rôle |
|---|---|
| `DJANGO_SECRET_KEY` | Clé secrète de Django. La valeur `change-me` est à remplacer |
| `DEBUG` | Mode debug (`True` en local) |
| `DATABASE_URL` | Connexion à PostgreSQL (utilisateur, mot de passe, hôte, port, base) |
| `ALLOWED_HOSTS` | Hôtes autorisés, séparés par des virgules |
| `CORS_ALLOWED_ORIGINS` | Origines autorisées pour les appels cross-origin (ici le futur back-office Next.js en local) |

Le fichier `.env` contient des secrets : il ne doit jamais être envoyé sur GitHub.

---

## 11. Points d'accès de l'API

Routes déclarées dans `hygie_backend/urls.py`.

| Route | Rôle |
|---|---|
| `/admin/` | Interface d'administration Django |
| `/api/auth/login/` | Obtention d'une paire de jetons (accès + rafraîchissement) |
| `/api/auth/refresh/` | Rafraîchissement du jeton d'accès (avec rotation) |
| `/api/auth/verify/` | Vérification d'un jeton |
| `/api/schema/` | Schéma OpenAPI |
| `/api/docs/` | Documentation Swagger |
| `/api/redoc/` | Documentation Redoc |
| `/api/comptes/` | Routes de l'app `comptes` |
| `/api/reservations/` | Routes de l'app `reservations` |
| `/api/paiements/` | Routes de l'app `paiements` |
| `/api/missions/` | Routes de l'app `missions` |
| `/api/evaluations/` | Routes de l'app `evaluations` |

Le détail des routes de chaque app sera ajouté au fil de leur développement. L'affichage de `/api/docs/` n'a pas encore été validé.

---

## 12. Avancement et feuille de route

### Phase 1. Analyse et modélisation (terminée)

- [x] Modélisation MERISE (MCD v3)
- [x] Modélisation UML (cas d'utilisation, classes, activité, séquences, états, déploiement, composants, packages)

### Phase 2. Backend Django (en cours)

- [x] Structure du projet et réglages séparés (base / développement / production)
- [x] Cinq apps créées, modèles migrés
- [x] Authentification JWT (connexion, rafraîchissement, vérification)
- [x] App `comptes` terminée et commitée : inscription Client, création Agent/Administrateur réservée aux administrateurs habilités, CRUD complet Agent et Client (liste, détail, modification), désactivation de compte pour les trois profils, permissions à deux niveaux, création automatique du superuser, 21 tests passants
- [ ] App `reservations` : en cours, non terminée. Ordre prévu : `Vehicule`, puis `Abonnement`, puis `Reservation` avec ses services (RG3 à RG6)
- [ ] App `paiements`
- [ ] App `missions`
- [ ] App `evaluations`

### Phase 3. Interfaces (non commencée)

- [ ] Back-office web (Next.js)
- [ ] Application mobile (Flutter)
- [ ] Site vitrine public

### Phase 4. Évolutions ultérieures

- [ ] Paiement par mobile money (Wave, Orange Money, MTN Money)
- [ ] Intégration Odoo

---

## 13. Points ouverts

| Point | Détail |
|---|---|
| Claim JWT `role` | Prévue, mais non confirmée comme implémentée. Seules `username`, `email`, `is_staff` et `is_superuser` le sont |
| App `reservations` | Non terminée |
| Groupe « Administrateur - Gérer les tarifs » | À créer. La migration écrite n'a jamais été exécutée ni confirmée ; elle dépend du modèle `Tarif` (app `paiements`), qui doit être migré |
| Endpoint `GET /me/` | Jamais écrit, à ajouter si le besoin se confirme |
| Swagger `/api/docs/` | Affichage non validé |
| Licence | À définir |

---

## 14. Journal des étapes

La plus récente en premier.

| Date | Étape | Résumé |
|---|---|---|
| 2026-10-18 | Création du README | Premier README complet : présentation, architecture, installation, diagrammes, feuille de route |
| Avant | App `comptes` terminée | Inscription, CRUD, désactivation, permissions, 21 tests passants |
| Avant | Authentification JWT | Connexion, rafraîchissement avec rotation, vérification, claims personnalisées |
| Avant | Modélisation | MERISE et UML finalisés ; modèles des cinq apps migrés |

---

## 15. Conventions de travail

- Une préoccupation par session : chaque session est consacrée à un seul bloc technique, et le travail validé est commité avant de passer au suivant.
- Avant d'écrire du code, les fichiers existants concernés sont relus.
- La documentation n'est mise à jour qu'après validation explicite de l'étape.
- Aucune logique métier dans les views (voir [architecture du backend](#5-architecture-du-backend)).

---

## 16. Auteur et Remerciements

- Auteur : Moussa Ben Youssouf TRAORE, [github.com/n1n3t33n](https://github.com/n1n3t33n)
- Profession : Etudiant en L3 Computer Science à L'Institut Ivoirien de Technologie
- Remerciements : à venir
---
