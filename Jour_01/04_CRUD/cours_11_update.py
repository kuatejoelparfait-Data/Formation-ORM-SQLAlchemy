"""
=============================================================================
 COURS 11 - UPDATE (Mise à jour de données)
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Mise à jour d'un seul objet (modifier les attributs)
 - Mise à jour en masse avec update()
 - Le pattern update_user avec **kwargs

 Pour exécuter :
   python cours_11_update.py
=============================================================================
"""

from datetime import datetime, timedelta
from sqlalchemy import create_engine, String, DateTime, update, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from typing import Optional

# ============================================================================
# PRÉPARATION
# ============================================================================

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    bio: Mapped[Optional[str]] = mapped_column(String(500))
    login_count: Mapped[int] = mapped_column(default=0)

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r}, active={self.is_active})"

engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

def preparer_donnees():
    """Insérer des données de test"""
    with Session(engine) as session:
        users = [
            User(name="Alice", email="alice@example.com", is_active=True, login_count=50),
            User(name="Bob", email="bob@example.com", is_active=True, login_count=3),
            User(name="Charlie", email="charlie@example.com", is_active=True, login_count=0),
            User(name="Diana", email="diana@example.com", is_active=False, login_count=25),
        ]
        session.add_all(users)
        session.commit()
    print("  ✓ 4 utilisateurs de test insérés\n")

# ============================================================================
# 1. MISE À JOUR D'UN SEUL OBJET
# ============================================================================

def demo_update_simple():
    """Modifier les attributs d'un objet puis sauvegarder"""

    print("=== 1. MISE À JOUR SIMPLE ===\n")

    with Session(engine) as session:
        # Étape 1 : Récupérer l'objet
        user = session.get(User, 1)  # Alice
        print(f"  Avant : {user}, bio={user.bio}")

        # Étape 2 : Modifier les attributs directement
        # C'est comme modifier un objet Python normal !
        user.name = "Alice Martin"
        user.bio = "Développeuse Python passionnée"

        # Étape 3 : Sauvegarder les modifications
        session.commit()

        # Étape 4 : Recharger pour confirmer
        session.refresh(user)
        print(f"  Après : {user}, bio={user.bio}")


# ============================================================================
# 2. FONCTION update_user AVEC **kwargs
# ============================================================================

def update_user(session: Session, user_id: int, **kwargs) -> Optional[User]:
    """
    Mettre à jour un utilisateur avec des champs variables.

    Paramètres :
        session  : session SQLAlchemy active
        user_id  : ID de l'utilisateur à modifier
        **kwargs : champs à modifier (clé=valeur)

    Retourne :
        L'utilisateur modifié, ou None si non trouvé

    Exemple d'utilisation :
        update_user(session, 1, name="Nouveau nom", bio="Nouvelle bio")
    """
    # Récupérer l'utilisateur
    user = session.get(User, user_id)

    # Si l'utilisateur n'existe pas, retourner None
    if user is None:
        return None

    # Modifier chaque champ passé en argument
    for key, value in kwargs.items():
        # hasattr vérifie que l'attribut existe sur l'objet
        if hasattr(user, key):
            # setattr modifie dynamiquement un attribut
            # setattr(user, "name", "Alice") ←→ user.name = "Alice"
            setattr(user, key, value)

    # Sauvegarder
    session.commit()
    session.refresh(user)
    return user


def demo_update_kwargs():
    """Utiliser la fonction update_user"""

    print("\n=== 2. FONCTION update_user(**kwargs) ===\n")

    with Session(engine) as session:
        # Modifier plusieurs champs en un appel
        user = update_user(
            session, 2,                        # User avec id=2 (Bob)
            name="Bob Dupont",                 # Nouveau nom
            bio="Ingénieur backend",           # Nouvelle bio
        )
        print(f"  Modifié : {user}, bio={user.bio}")

        # Modifier un seul champ
        user = update_user(session, 3, name="Charlie Brown")
        print(f"  Modifié : {user}")


# ============================================================================
# 3. MISE À JOUR EN MASSE (BULK UPDATE)
# ============================================================================

def demo_bulk_update():
    """Modifier plusieurs lignes en une seule requête SQL"""

    print("\n=== 3. MISE À JOUR EN MASSE ===\n")

    with Session(engine) as session:
        # Afficher l'état avant
        users = session.execute(select(User)).scalars().all()
        print("  Avant :")
        for u in users:
            print(f"    {u}")

        # Mise à jour en masse avec update()
        # Cette requête SQL met à jour TOUTES les lignes qui correspondent
        stmt = (
            update(User)                          # UPDATE users
            .where(User.login_count < 5)           # WHERE login_count < 5
            .values(is_active=False)               # SET is_active = False
        )

        # Exécuter la requête
        result = session.execute(stmt)
        session.commit()

        # result.rowcount = nombre de lignes modifiées
        print(f"\n  {result.rowcount} utilisateurs désactivés (login_count < 5)")

        # Vérifier le résultat
        # Expirer le cache pour recharger les données fraîches
        session.expire_all()
        users = session.execute(select(User)).scalars().all()
        print("\n  Après :")
        for u in users:
            print(f"    {u}")


# ============================================================================
# 4. INCRÉMENTER UNE VALEUR
# ============================================================================

def demo_increment():
    """Incrémenter un compteur de façon sûre"""

    print("\n=== 4. INCRÉMENTER UN COMPTEUR ===\n")

    with Session(engine) as session:
        user = session.get(User, 1)
        print(f"  Avant : login_count = {user.login_count}")

        # Méthode 1 : incrémentation Python (simple mais pas thread-safe)
        user.login_count += 1
        session.commit()
        session.refresh(user)
        print(f"  Après (+1 Python) : login_count = {user.login_count}")

        # Méthode 2 : incrémentation SQL (plus sûre, thread-safe)
        stmt = (
            update(User)
            .where(User.id == 1)
            .values(login_count=User.login_count + 1)  # Incrémentation côté SQL
        )
        session.execute(stmt)
        session.commit()
        session.expire_all()
        user = session.get(User, 1)
        print(f"  Après (+1 SQL)    : login_count = {user.login_count}")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : UPDATE (Mise à jour de données)")
    print("=" * 60)

    preparer_donnees()
    demo_update_simple()
    demo_update_kwargs()
    demo_bulk_update()
    demo_increment()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 11")
    print("=" * 60)
