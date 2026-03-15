"""
=============================================================================
 COURS 05 - CONFIGURATION MODERNE AVEC PYDANTIC SETTINGS
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Comment organiser la configuration avec pydantic-settings
 - Le pattern config.py + database.py
 - L'utilisation du fichier .env pour les secrets
 - La classe Base (DeclarativeBase)

 Prérequis : pip install pydantic-settings

 Pour exécuter :
   python cours_05_config_pydantic.py
=============================================================================
"""

# ============================================================================
# 1. POURQUOI PYDANTIC SETTINGS ?
# ============================================================================
#
# En entreprise, on ne met JAMAIS les mots de passe dans le code.
# On utilise des VARIABLES D'ENVIRONNEMENT ou des fichiers .env
#
# pydantic-settings permet de :
#   1. Lire automatiquement les variables d'environnement
#   2. Lire un fichier .env
#   3. Valider les valeurs (types corrects)
#   4. Fournir des valeurs par défaut
#
# Fichier .env (à la racine du projet, JAMAIS commité dans git) :
#   DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/mydb
#   DATABASE_ECHO=false
#   DATABASE_POOL_SIZE=10

# ============================================================================
# 2. LE FICHIER config.py
# ============================================================================

# En vrai projet, ce code serait dans app/config.py

# Essayons d'importer pydantic_settings, sinon on simule
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        """
        Configuration de l'application.
        Les valeurs sont lues depuis :
          1. Les variables d'environnement (priorité haute)
          2. Le fichier .env (priorité basse)
          3. Les valeurs par défaut (si rien d'autre)
        """

        # model_config : configuration de Pydantic
        model_config = SettingsConfigDict(
            env_file=".env",           # Lire le fichier .env
            env_file_encoding="utf-8"  # Encodage du fichier
        )

        # Variables de configuration avec valeurs par défaut
        database_url: str = "sqlite:///./app.db"     # URL de la base (SQLite par défaut)
        database_echo: bool = False                   # Afficher les requêtes SQL ?
        database_pool_size: int = 5                   # Taille du pool de connexions

    # Créer une instance unique des settings
    settings = Settings()
    print("  ✓ pydantic-settings importé avec succès")

except ImportError:
    # Si pydantic-settings n'est pas installé, on simule
    print("  ⚠ pydantic-settings non installé, utilisation de valeurs par défaut")
    print("  → Pour installer : pip install pydantic-settings")

    class Settings:
        """Version simplifiée sans pydantic (pour la démo)"""
        database_url: str = "sqlite:///:memory:"
        database_echo: bool = False
        database_pool_size: int = 5

    settings = Settings()


# ============================================================================
# 3. LE FICHIER database.py
# ============================================================================

# En vrai projet, ce code serait dans app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Créer le moteur avec les settings
engine = create_engine(
    settings.database_url,          # URL depuis la config
    echo=settings.database_echo,    # Mode debug depuis la config
    # pool_size=settings.database_pool_size,  # Pas supporté par SQLite
)

# Créer la factory de sessions
SessionLocal = sessionmaker(
    autocommit=False,    # Pas de commit automatique
    autoflush=False,     # Pas de flush automatique
    bind=engine          # Lier au moteur
)

# Classe de Base pour TOUS les modèles
class Base(DeclarativeBase):
    """
    Classe de base pour tous les modèles SQLAlchemy.
    Tous vos modèles doivent hériter de cette classe.

    Exemple :
        class User(Base):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(primary_key=True)
    """
    pass


# ============================================================================
# 4. LE FICHIER .env
# ============================================================================

def montrer_fichier_env():
    """Montrer le contenu type d'un fichier .env"""

    print("\n=== EXEMPLE DE FICHIER .env ===\n")

    contenu_env = """
    # .env - Variables d'environnement (NE PAS COMMITER DANS GIT !)
    # Copier ce fichier en .env et remplir les valeurs

    # Base de données
    DATABASE_URL=sqlite:///./app.db          # Développement
    # DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/mydb  # Production

    DATABASE_ECHO=true                        # Afficher les requêtes SQL
    DATABASE_POOL_SIZE=5                      # Taille du pool
    """

    print(contenu_env)

    print("  IMPORTANT : Ajoutez .env dans votre .gitignore !")
    print("  → echo '.env' >> .gitignore")


# ============================================================================
# 5. STRUCTURE DE PROJET RECOMMANDÉE
# ============================================================================

def montrer_structure():
    """Structure de fichiers recommandée"""

    print("\n=== STRUCTURE DE PROJET ===\n")

    structure = """
    mon_projet/
    ├── .env                 ← Variables secrètes (pas dans git !)
    ├── .env.example         ← Modèle du .env (dans git, sans secrets)
    ├── .gitignore           ← Inclure .env, *.db
    ├── requirements.txt     ← Dépendances Python
    │
    ├── app/
    │   ├── __init__.py
    │   ├── config.py        ← Settings (pydantic)
    │   ├── database.py      ← Engine, Session, Base
    │   │
    │   ├── models/          ← Modèles SQLAlchemy
    │   │   ├── __init__.py
    │   │   ├── user.py
    │   │   └── article.py
    │   │
    │   └── main.py          ← Point d'entrée
    │
    └── tests/               ← Tests
        └── test_models.py
    """

    print(structure)


# ============================================================================
# 6. DÉMONSTRATION COMPLÈTE
# ============================================================================

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class User(Base):
    """Modèle de test pour la démo"""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r})"


def demo_complete():
    """Démonstration de la config en action"""

    print("\n=== DÉMONSTRATION COMPLÈTE ===\n")

    # Recréer le moteur en mémoire pour la démo
    demo_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(demo_engine)
    DemoSession = sessionmaker(bind=demo_engine)

    with DemoSession() as session:
        # Créer un utilisateur
        user = User(name="Alice")
        session.add(user)
        session.commit()
        session.refresh(user)

        print(f"  Configuration utilisée : {settings.database_url}")
        print(f"  Utilisateur créé : {user}")
        print("  ✓ Tout fonctionne !")


# ============================================================================
# 7. EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Configuration avec Pydantic Settings")
    print("=" * 60)

    montrer_fichier_env()
    montrer_structure()
    demo_complete()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 05")
    print("=" * 60)
