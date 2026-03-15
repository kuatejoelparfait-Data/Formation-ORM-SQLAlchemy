"""
=============================================================================
 COURS 13 - STRUCTURE DE PROJET FastAPI + SQLAlchemy
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier montre la structure de projet recommandée
 pour une application FastAPI avec SQLAlchemy.
=============================================================================
"""

STRUCTURE = """
=== STRUCTURE DE PROJET RECOMMANDÉE ===

  mon_projet/
  │
  ├── app/                        ← Code source principal
  │   ├── __init__.py             ← Marque le dossier comme package Python
  │   ├── main.py                 ← Point d'entrée FastAPI
  │   ├── config.py               ← Configuration (Pydantic Settings)
  │   ├── database.py             ← Engine, Session, Base
  │   ├── dependencies.py         ← Dépendances partagées (get_db)
  │   │
  │   ├── models/                 ← Modèles SQLAlchemy (tables BDD)
  │   │   ├── __init__.py         ← Exporter tous les modèles
  │   │   ├── user.py             ← class User(Base)
  │   │   └── article.py          ← class Article(Base)
  │   │
  │   ├── schemas/                ← Schémas Pydantic (validation API)
  │   │   ├── __init__.py
  │   │   ├── user.py             ← UserCreate, UserResponse, UserUpdate
  │   │   └── article.py          ← ArticleCreate, ArticleResponse
  │   │
  │   ├── crud/                   ← Opérations CRUD (accès BDD)
  │   │   ├── __init__.py
  │   │   ├── user.py             ← create_user, get_user, etc.
  │   │   └── article.py          ← create_article, get_article, etc.
  │   │
  │   └── routers/                ← Endpoints API (routes)
  │       ├── __init__.py
  │       ├── users.py            ← /users/...
  │       └── articles.py         ← /articles/...
  │
  ├── alembic/                    ← Migrations de base de données
  │   ├── env.py                  ← Configuration Alembic
  │   └── versions/               ← Fichiers de migration
  │
  ├── tests/                      ← Tests
  │   ├── __init__.py
  │   ├── test_users.py
  │   └── test_articles.py
  │
  ├── .env                        ← Variables d'environnement (PAS dans Git !)
  ├── .env.example                ← Modèle du .env (dans Git)
  ├── .gitignore                  ← Fichiers à ignorer
  ├── alembic.ini                 ← Configuration Alembic
  ├── requirements.txt            ← Dépendances Python
  └── README.md                   ← Documentation


=== RÔLE DE CHAQUE COUCHE ===

  models/   → QUOI stocker (structure des tables)
  schemas/  → QUOI accepter/retourner (validation des données API)
  crud/     → COMMENT accéder aux données (requêtes SQL)
  routers/  → OÙ exposer les endpoints (routes HTTP)


=== FLUX D'UNE REQUÊTE HTTP ===

  Client → Router → CRUD → Modèle → Base de données
           ↓
         Schema (validation)
           ↓
         get_db (session)

  1. Le client envoie une requête HTTP (ex: POST /users/)
  2. Le ROUTER reçoit la requête et valide avec le SCHEMA Pydantic
  3. Le ROUTER appelle une fonction CRUD
  4. La fonction CRUD utilise le MODÈLE SQLAlchemy pour accéder à la BDD
  5. Le résultat est converti en SCHEMA de réponse et renvoyé
"""

if __name__ == "__main__":
    print("=" * 60)
    print(" COURS : Structure de projet FastAPI + SQLAlchemy")
    print("=" * 60)
    print(STRUCTURE)
    print("=" * 60)
    print(" FIN DU COURS 13 (Jour 2)")
    print("=" * 60)
