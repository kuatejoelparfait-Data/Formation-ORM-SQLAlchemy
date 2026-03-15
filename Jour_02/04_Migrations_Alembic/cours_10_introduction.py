"""
=============================================================================
 COURS 10 - INTRODUCTION AUX MIGRATIONS AVEC ALEMBIC
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Pourquoi les migrations sont nécessaires
 - Ce qu'est Alembic
 - Comment initialiser et configurer Alembic
 - La structure des fichiers créés

 NOTE : Ce fichier est principalement DOCUMENTAIRE.
 Les migrations se font en ligne de commande, pas dans un script Python.
=============================================================================
"""

# ============================================================================
# 1. POURQUOI LES MIGRATIONS ?
# ============================================================================
#
# PROBLÈME :
#   En développement, on utilise Base.metadata.create_all(engine)
#   pour créer les tables. Mais cette commande :
#     - NE MODIFIE PAS les tables existantes
#     - NE PEUT PAS ajouter une colonne à une table existante
#     - NE PEUT PAS renommer ou supprimer une colonne
#
# EN PRODUCTION :
#   On ne peut PAS supprimer la base et la recréer !
#   Les données des utilisateurs seraient perdues !
#
# SOLUTION : Les MIGRATIONS
#   → Un système qui MODIFIE la base progressivement
#   → Chaque changement est un "fichier de migration"
#   → On peut avancer (upgrade) ou reculer (downgrade)
#   → L'historique est versionné dans Git
#
# ANALOGIE :
#   Les migrations sont comme un historique Git pour votre base de données.
#   Chaque migration = un commit qui modifie le schéma.

# ============================================================================
# 2. QU'EST-CE QU'ALEMBIC ?
# ============================================================================
#
# Alembic est l'outil de migration officiel de SQLAlchemy.
# Il permet de :
#   - Détecter automatiquement les changements dans vos modèles
#   - Générer des fichiers de migration
#   - Appliquer ou annuler les migrations
#   - Garder un historique de toutes les modifications
#
# Installation :
#   pip install alembic

# ============================================================================
# 3. INITIALISATION D'ALEMBIC
# ============================================================================
#
# Commande d'initialisation (dans le terminal) :
#   alembic init alembic
#
# Structure créée :
#
#   mon_projet/
#   ├── alembic/
#   │   ├── env.py           ← Configuration d'Alembic (à modifier !)
#   │   ├── script.py.mako   ← Template pour les fichiers de migration
#   │   └── versions/        ← Dossier contenant les fichiers de migration
#   │       ├── 001_create_users.py
#   │       ├── 002_add_email_column.py
#   │       └── ...
#   └── alembic.ini           ← Configuration principale

# ============================================================================
# 4. CONFIGURATION DE alembic.ini
# ============================================================================

ALEMBIC_INI_EXAMPLE = """
# alembic.ini (fichier principal de configuration)

[alembic]
# Chemin vers le dossier des migrations
script_location = alembic

# URL de connexion à la base de données
# IMPORTANT : en production, utiliser une variable d'environnement !
sqlalchemy.url = sqlite:///./app.db
# sqlalchemy.url = postgresql+psycopg2://user:pass@localhost/mydb
"""

# ============================================================================
# 5. CONFIGURATION DE env.py
# ============================================================================

ENV_PY_EXAMPLE = """
# alembic/env.py - Configuration d'Alembic

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# IMPORTANT : Importer vos modèles !
# Sans ça, Alembic ne peut pas détecter les changements
from app.database import Base
from app.models import User, Article, Tag  # Tous vos modèles !

# La métadonnée de vos modèles
target_metadata = Base.metadata

# ... (le reste est généré automatiquement)
"""

# ============================================================================
# 6. LES AVANTAGES DES MIGRATIONS
# ============================================================================

def afficher_avantages():
    """Les 4 avantages principaux des migrations"""

    print("=== POURQUOI UTILISER LES MIGRATIONS ? ===\n")
    print("  1. TRAÇABILITÉ")
    print("     → Historique complet de tous les changements de schéma")
    print("     → Qui a changé quoi et quand")
    print()
    print("  2. REPRODUCTIBILITÉ")
    print("     → Même schéma en dev, staging et production")
    print("     → Tout le monde a la même base de données")
    print()
    print("  3. ROLLBACK")
    print("     → Revenir en arrière si un changement pose problème")
    print("     → alembic downgrade -1 (revenir d'une étape)")
    print()
    print("  4. COLLABORATION")
    print("     → Les migrations sont dans Git")
    print("     → L'équipe partage les changements de schéma")
    print("     → Pas de 'ça marche sur ma machine'")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" COURS : Introduction aux Migrations avec Alembic")
    print("=" * 60)

    afficher_avantages()

    print("\n=== COMMANDES ESSENTIELLES ===\n")
    print("  pip install alembic         → Installer Alembic")
    print("  alembic init alembic        → Initialiser le projet")
    print("  alembic revision --autogenerate -m 'message'  → Créer une migration")
    print("  alembic upgrade head        → Appliquer toutes les migrations")
    print("  alembic downgrade -1        → Revenir d'une étape")
    print("  alembic current             → Voir la migration actuelle")
    print("  alembic history             → Voir l'historique")

    print("\n" + "=" * 60)
    print(" FIN DU COURS 10 (Jour 2)")
    print("=" * 60)
