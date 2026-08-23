# API de réservation des ressources pédagogiques 🏫

> **Master 1 IAGE — Sujet 3 : Conception d'API avec Django & Django REST Framework**

Un **enseignant** demande un créneau sur une salle ou un matériel ; un **gestionnaire** valide ou refuse ; un **administrateur** gère le parc et les comptes.

---

## ⚡ 1. Démarrage rapide en local (3 minutes)

```bash
# 1. Créer et activer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate        # On Windows : venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Créer le fichier de configuration local (.env)
cp .env.example .env

# 4. Préparer la base de données SQLite
python manage.py migrate

# 5. Charger le jeu de données de démo
python manage.py jeu_de_donnees

# 6. Lancer l'API
python manage.py runserver
```

👉 Ouvrez ensuite **[http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)** : toute l'API y est cliquable et documentée avec Swagger !

---

### 🔑 Comptes de démonstration disponibles

| Identifiant   | Rôle            | Mot de passe | Ce qu'il a le droit de faire |
|---------------|-----------------|--------------|------------------------------|
| `prof.malick` | Enseignant      | `Demo1234!`  | Faire des demandes, voir et annuler uniquement ses réservations |
| `prof.diallo` | Enseignant      | `Demo1234!`  | Faire des demandes, voir et annuler uniquement ses réservations |
| `gest.sow`    | Gestionnaire    | `Demo1234!`  | Valider, refuser (avec motif), clôturer les demandes et gérer les indisponibilités |
| `admin.alpha` | Administrateur  | `Demo1234!`  | Gérer les utilisateurs, les ressources (salles/matériels) et tout arbitrer |

*Pour créer un superadministrateur complet : `python manage.py createsuperuser`*

---

## 🐳 2. Démarrage avec Docker (Production / Test)

```bash
# 1. Préparer la configuration Docker
cp .env.example .env

# 2. Démarrer PostgreSQL, l'API (Gunicorn) et Nginx
docker compose up --build -d

# 3. Appliquer les migrations et injecter les données dans Docker
docker compose exec api python manage.py migrate
docker compose exec api python manage.py jeu_de_donnees

# 4. Lancer la suite de 69 tests dans Docker
docker compose exec api python manage.py test
```

👉 Accès à l'API via Nginx : **[http://localhost/api/docs/](http://localhost/api/docs/)**  
👉 Vérification de santé : `curl http://localhost/health/`

---

## 📌 3. Résumé des routes de l'API (`/api/v1/`)

### 🔐 Authentification (JWT)
- `POST /api/v1/auth/login/` ➔ Connexion (reçoit l'access token et le refresh token)
- `POST /api/v1/auth/refresh/` ➔ Renouvelle le jeton d'accès
- `POST /api/v1/auth/verify/` ➔ Vérifie la validité d'un jeton

### 🏫 Ressources & Indisponibilités
- `GET /api/v1/ressources/` ➔ Liste le parc (salles, matériels)
- `POST /api/v1/ressources/` ➔ Ajoute une ressource (Administrateur uniquement)
- `GET /api/v1/indisponibilites/` ➔ Liste les plages bloquées pour maintenance

### 📅 Réservations (Machine à états)
- `GET /api/v1/reservations/` ➔ Liste des réservations (Filtrée selon le rôle)
- `POST /api/v1/reservations/` ➔ Déposer une demande (Enseignant)
- `POST /api/v1/reservations/{id}/valider/` ➔ Valider la demande (Gestionnaire / Admin)
- `POST /api/v1/reservations/{id}/refuser/` ➔ Refuser avec motif (Gestionnaire / Admin)
- `POST /api/v1/reservations/{id}/annuler/` ➔ Annuler la demande (Auteur / Gestionnaire)
- `POST /api/v1/reservations/{id}/terminer/` ➔ Clôturer la séance terminée

---

## 🧪 4. Exécuter les tests & mesurer la couverture

```bash
# Lancer les 69 tests automatisés
python manage.py test

# Calculer la couverture du code (~95 %)
coverage run manage.py test
coverage report -m
```

---

## 🎯 5. Scénario de test rapide (3 minutes)

1. Connectez-vous avec `prof.malick` sur `POST /auth/login/` et copiez le jeton `access`.
2. Déposez une réservation sur le **Laboratoire réseau** sur `POST /reservations/` ➔ **HTTP 201 Created**, statut `en_attente`.
3. Connectez-vous avec `prof.diallo` et tentez d'accéder à la réservation de Malick ➔ **HTTP 404 Not Found** *(Isolation des données)*.
4. Connectez-vous avec `gest.sow` et validez la réservation de Malick ➔ **HTTP 200 OK**, statut `validee`.
5. Tentez de valider une deuxième réservation concurrente sur le même créneau ➔ **HTTP 409 Conflict** *(Protection contre les chevauchements)*.
