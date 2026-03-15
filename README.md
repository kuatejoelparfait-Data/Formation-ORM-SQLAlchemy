# Formation ORM Python avec SQLAlchemy 2.0

**Formation complète - Niveau débutant (zéro)**

## Prérequis

- Python 3.10+ installé
- Connaissances de base en Python (variables, fonctions, classes)
- Notions de base en SQL (SELECT, INSERT, UPDATE, DELETE)

## Installation

```bash
pip install sqlalchemy pydantic pydantic-settings alembic fastapi uvicorn email-validator
```

## Structure de la formation

```
Formation_ORM_SQLAlchemy/
│
├── README.md                          ← Ce fichier
│
├── Jour_01/                           ← SQLAlchemy Core et ORM Fondamentaux
│   ├── LEXIQUE.md                     ← Lexique des termes du Jour 1
│   │
│   ├── 01_Introduction/
│   │   ├── cours_01_pourquoi_orm.py        Pourquoi utiliser un ORM
│   │   └── cours_02_core_vs_orm.py         Core vs ORM, quand utiliser quoi
│   │
│   ├── 02_Configuration/
│   │   ├── cours_03_engine.py              L'Engine (connexion à la BDD)
│   │   ├── cours_04_session.py             La Session (unité de travail)
│   │   └── cours_05_config_pydantic.py     Configuration avec Pydantic
│   │
│   ├── 03_Modeles/
│   │   ├── cours_06_modele_base.py         Définir un modèle (Mapped, mapped_column)
│   │   ├── cours_07_types_colonnes.py      Tous les types de colonnes
│   │   └── cours_08_options_mapped_column.py  Options et Enums
│   │
│   ├── 04_CRUD/
│   │   ├── cours_09_create.py              CREATE - Insertion de données
│   │   ├── cours_10_read.py                READ - Lecture et filtres
│   │   ├── cours_11_update.py              UPDATE - Mise à jour
│   │   └── cours_12_delete.py              DELETE - Suppression et Soft Delete
│   │
│   ├── 05_Query_Avancee/
│   │   ├── cours_13_tri_pagination.py      Tri, pagination, comptage
│   │   ├── cours_14_aggregations.py        COUNT, SUM, AVG, GROUP BY
│   │   └── cours_15_selection_colonnes.py  Sélection de colonnes spécifiques
│   │
│   ├── 06_Bonnes_Pratiques/
│   │   ├── cours_16_pattern_repository.py  Pattern Repository
│   │   └── cours_17_gestion_transactions.py  Transactions et erreurs
│   │
│   └── Exercices/
│       ├── TP1_Configuration_Premiers_Modeles/
│       │   ├── enonce.py                   Énoncé avec squelette à compléter
│       │   └── solution.py                 Solution complète commentée
│       └── TP2_CRUD_Articles/
│           ├── enonce.py                   10 fonctions CRUD à implémenter
│           └── solution.py                 Solution avec script de test
│
└── Jour_02/                           ← Relations et Optimisations
    ├── LEXIQUE.md                     ← Lexique des termes du Jour 2
    │
    ├── 01_Relations_One_to_Many/
    │   ├── cours_01_definition.py          Définir une relation 1-N
    │   ├── cours_02_utilisation.py         Utiliser les relations
    │   └── cours_03_cascade.py             Options de cascade
    │
    ├── 02_Relations_Many_to_Many/
    │   ├── cours_04_table_association.py   Table d'association (N-N)
    │   ├── cours_05_manipulation.py        Manipuler les relations N-N
    │   └── cours_06_association_object.py  Association Object (données sur la relation)
    │
    ├── 03_Probleme_N_Plus_1/
    │   ├── cours_07_illustration.py        Le problème N+1 expliqué
    │   ├── cours_08_eager_loading.py       joinedload, selectinload, subqueryload
    │   └── cours_09_comparaison_strategies.py  Eager loading en cascade
    │
    ├── 04_Migrations_Alembic/
    │   ├── cours_10_introduction.py        Pourquoi les migrations
    │   ├── cours_11_commandes.py           Aide-mémoire des commandes
    │   └── cours_12_exemple_migration.py   Exemples de fichiers de migration
    │
    ├── 05_Integration_FastAPI/
    │   ├── cours_13_structure_projet.py    Structure de projet recommandée
    │   ├── cours_14_dependance_session.py  Dépendance get_db
    │   ├── cours_15_schemas_pydantic.py    Schémas Pydantic vs Modèles ORM
    │   └── cours_16_router_crud.py         Router CRUD complet (exécutable !)
    │
    └── Exercices/
        ├── TP1_Modele_Blog/
        │   ├── enonce.py                   Blog complet avec 5 modèles
        │   └── solution.py                 Solution avec données de test
        └── TP2_API_Bibliotheque/
            ├── enonce.py                   API REST complète
            └── solution.py                 Application FastAPI fonctionnelle
```

## Comment utiliser cette formation

1. **Suivez les fichiers dans l'ordre** : cours_01, cours_02, etc.
2. **Exécutez chaque fichier** : `python cours_XX_nom.py` pour voir les résultats
3. **Lisez les commentaires** : chaque ligne est expliquée en français
4. **Faites les TP** : commencez par l'énoncé, puis comparez avec la solution
5. **Consultez le LEXIQUE** : en cas de doute sur un terme

## Jour 1 - SQLAlchemy Core et ORM Fondamentaux

| Horaire | Contenu |
|---------|---------|
| 9h00-10h30 | Introduction, Engine, Session, Configuration |
| 10h30-12h30 | Modèles, Types de colonnes, TP1 |
| 14h00-15h30 | CRUD complet (Create, Read, Update, Delete) |
| 15h30-17h30 | Query avancée, Bonnes pratiques, TP2 |

## Jour 2 - Relations et Optimisations

| Horaire | Contenu |
|---------|---------|
| 9h00-10h30 | Relations One-to-Many, Cascade |
| 10h30-12h30 | Relations Many-to-Many, Association Object, TP1 |
| 14h00-15h30 | Problème N+1, Eager Loading, Migrations Alembic |
| 15h30-17h30 | Intégration FastAPI, TP2 API Bibliothèque |

## Technologies utilisées

- **SQLAlchemy 2.0** : ORM Python
- **SQLite** : Base de données de développement
- **Pydantic** : Validation de données
- **Alembic** : Migrations de base de données
- **FastAPI** : Framework API REST
