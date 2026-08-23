# API de réservation des ressources pédagogiques

Projet Master 1 IAGE — Sujet 3 (Conception d'API avec Django et Django REST Framework)

Application web permettant aux enseignants de réserver des ressources (salles, matériels), aux gestionnaires de valider ou refuser les demandes, et aux administrateurs de gérer le parc et les comptes.

---

## 1. Installation en local

```bash
# 1. Créer et activer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Fichier de configuration
cp .env.example .env

# 4. Appliquer les migrations
python manage.py migrate

# 5. Charger les données de démonstration
python manage.py jeu_de_donnees

# 6. Lancer le serveur
python manage.py runserver
```

L'API et sa documentation Swagger sont accessibles sur : http://localhost:8000/api/docs/

---

## 2. Comptes de test

Les comptes suivants sont créés automatiquement par la commande `jeu_de_donnees` :

| Identifiant | Rôle | Mot de passe | Description |
|---|---|---|---|
| `prof.malick` | Enseignant | `Demo1234!` | Peut effectuer des demandes et gérer ses propres réservations |
| `prof.diallo` | Enseignant | `Demo1234!` | Peut effectuer des demandes et gérer ses propres réservations |
| `gest.sow` | Gestionnaire | `Demo1234!` | Peut valider, refuser (avec motif) et clôturer les demandes |
| `admin.alpha` | Administrateur | `Demo1234!` | Gestion globale du parc et des utilisateurs |

---

## 3. Endpoints principaux

Toutes les routes sont préfixées par `/api/v1/` :

- **Authentification (JWT)** :
  - `POST /api/v1/auth/login/` (obtention des tokens access/refresh)
  - `POST /api/v1/auth/refresh/` (renouvellement du token)

- **Ressources et Indisponibilités** :
  - `GET /api/v1/ressources/` (liste des salles et équipements)
  - `GET /api/v1/indisponibilites/` (liste des périodes de maintenance)

- **Réservations** :
  - `GET /api/v1/reservations/` (liste selon les droits)
  - `POST /api/v1/reservations/` (nouvelle demande)
  - `POST /api/v1/reservations/{id}/valider/` (validation par gestionnaire)
  - `POST /api/v1/reservations/{id}/refuser/` (refus avec motif)
  - `POST /api/v1/reservations/{id}/annuler/` (annulation par l'auteur)
  - `POST /api/v1/reservations/{id}/terminer/` (clôture)

- **Supervision** :
  - `GET /health/` (état de l'API et de la base de données)

---

## 4. Tests automatisés

Pour lancer la suite de 69 tests et vérifier la couverture du code :

```bash
# Lancer les tests
python manage.py test

# Vérifier la couverture
coverage run manage.py test
coverage report -m
```

---

## 5. Déploiement Docker

```bash
# Lancer la pile (PostgreSQL + API + Nginx)
docker compose up --build -d

# Migrations et données dans Docker
docker compose exec api python manage.py migrate
docker compose exec api python manage.py jeu_de_donnees
```

Accès Swagger via Docker : http://localhost/api/docs/

