"""
=============================================================================
 COURS 06 - DÉFINITION D'UN MODÈLE (SQLAlchemy 2.0)
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Comment créer un modèle avec la syntaxe SQLAlchemy 2.0
 - Mapped et mapped_column
 - __tablename__, primary_key, String, unique, index
 - Optional pour les champs nullables
 - Timestamps automatiques (created_at, updated_at)

 Pour exécuter :
   python cours_06_modele_base.py
=============================================================================
"""

from datetime import datetime
from typing import Optional               # Pour les champs qui peuvent être NULL
from sqlalchemy import create_engine, String, Text, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ============================================================================
# 1. LA CLASSE DE BASE
# ============================================================================

# Tous les modèles doivent hériter de DeclarativeBase
class Base(DeclarativeBase):
    pass


# ============================================================================
# 2. UN MODÈLE COMPLET : User
# ============================================================================

class User(Base):
    """
    Modèle User - représente la table 'users' dans la base de données.

    Chaque attribut de la classe = une colonne dans la table.
    Le typage Python (Mapped[int]) = le type de la colonne.
    """

    # __tablename__ : le nom de la table dans la base de données
    # Convention : nom au pluriel, en minuscules, avec underscores
    __tablename__ = "users"

    # ---- CLEF PRIMAIRE ----
    # primary_key=True : identifiant unique, auto-incrémenté
    # Mapped[int] : cette colonne contient un entier, OBLIGATOIRE
    id: Mapped[int] = mapped_column(primary_key=True)

    # ---- CHAMPS OBLIGATOIRES ----
    # Mapped[str] (sans Optional) = la colonne NE PEUT PAS être NULL
    # String(255) : texte avec une longueur maximale de 255 caractères
    # unique=True : chaque email doit être unique (pas de doublons)
    # index=True : crée un INDEX pour accélérer les recherches par email
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # String(50) : texte limité à 50 caractères
    username: Mapped[str] = mapped_column(String(50), unique=True)

    # Mot de passe HASHÉ (ne JAMAIS stocker en clair !)
    hashed_password: Mapped[str] = mapped_column(String(255))

    # ---- CHAMPS OPTIONNELS (NULLABLES) ----
    # Mapped[Optional[str]] : cette colonne PEUT être NULL
    # Un nouveau user peut ne pas avoir de nom complet
    full_name: Mapped[Optional[str]] = mapped_column(String(100))

    # Text : texte sans limite de longueur (pour les longues descriptions)
    bio: Mapped[Optional[str]] = mapped_column(Text)

    # ---- BOOLÉENS AVEC VALEUR PAR DÉFAUT ----
    # default=True : quand on crée un User sans préciser is_active,
    # la valeur sera True automatiquement
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)

    # ---- TIMESTAMPS AUTOMATIQUES ----
    # server_default=func.now() : la BDD met la date/heure actuelle
    # automatiquement quand on insère une nouvelle ligne
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),       # DateTime avec fuseau horaire
        server_default=func.now()      # Valeur par défaut côté SERVEUR (BDD)
    )

    # onupdate=func.now() : la BDD met à jour la date/heure
    # automatiquement quand on MODIFIE la ligne
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now()            # Mis à jour automatiquement
    )

    # ---- __repr__ : AFFICHAGE ----
    # Définit comment l'objet s'affiche quand on fait print()
    # !r après une variable = ajoute des guillemets autour des strings
    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r}, email={self.email!r})"


# ============================================================================
# 3. COMPRENDRE Mapped ET mapped_column
# ============================================================================
#
# Mapped[int]           → Colonne OBLIGATOIRE de type entier
# Mapped[str]           → Colonne OBLIGATOIRE de type texte
# Mapped[bool]          → Colonne OBLIGATOIRE de type booléen
# Mapped[Optional[str]] → Colonne qui PEUT être NULL (Optional)
# Mapped[datetime]      → Colonne de type date/heure
#
# mapped_column() accepte ces options :
#   primary_key=True     → C'est la clé primaire
#   unique=True          → Valeur unique dans toute la table
#   index=True           → Créer un index pour des recherches rapides
#   nullable=True/False  → La colonne peut-elle être NULL ?
#   default=valeur       → Valeur par défaut côté PYTHON
#   server_default=...   → Valeur par défaut côté BASE DE DONNÉES
#   onupdate=...         → Valeur mise à jour automatiquement à chaque UPDATE

# ============================================================================
# 4. DÉMONSTRATION
# ============================================================================

def demo():
    """Créer la table et insérer des utilisateurs"""

    print("=== DÉMONSTRATION : Modèle User ===\n")

    # Créer le moteur et les tables
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    print("  ✓ Tables créées")

    with Session(engine) as session:
        # Créer un utilisateur avec tous les champs
        user1 = User(
            email="alice@example.com",
            username="alice",
            hashed_password="hashed_secret",  # En vrai, utiliser bcrypt !
            full_name="Alice Martin",
            bio="Développeuse Python passionnée",
        )

        # Créer un utilisateur avec seulement les champs obligatoires
        # Les champs optionnels seront NULL
        # Les champs avec default auront leur valeur par défaut
        user2 = User(
            email="bob@example.com",
            username="bob",
            hashed_password="hashed_secret",
            # full_name sera NULL (Optional)
            # bio sera NULL (Optional)
            # is_active sera True (default=True)
            # is_admin sera False (default=False)
            # created_at sera maintenant (server_default)
        )

        # Ajouter et sauvegarder
        session.add_all([user1, user2])
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        # Afficher les résultats
        print(f"\n  User 1 : {user1}")
        print(f"    full_name  = {user1.full_name}")    # "Alice Martin"
        print(f"    bio        = {user1.bio}")           # "Développeuse..."
        print(f"    is_active  = {user1.is_active}")     # True (default)
        print(f"    is_admin   = {user1.is_admin}")      # False (default)
        print(f"    created_at = {user1.created_at}")    # Date/heure actuelle

        print(f"\n  User 2 : {user2}")
        print(f"    full_name  = {user2.full_name}")    # None (Optional, non renseigné)
        print(f"    bio        = {user2.bio}")           # None
        print(f"    is_active  = {user2.is_active}")     # True


# ============================================================================
# 5. EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Définition d'un Modèle SQLAlchemy 2.0")
    print("=" * 60)

    demo()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 06")
    print("=" * 60)
