"""
=============================================================================
 COURS 16 - PATTERN REPOSITORY
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Le pattern Repository (encapsuler l'accès aux données)
 - Comment séparer la logique métier de la logique BDD
 - Un exemple complet et réutilisable

 Pour exécuter :
   python cours_16_pattern_repository.py
=============================================================================
"""

from typing import Optional
from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ============================================================================
# 1. QU'EST-CE QUE LE PATTERN REPOSITORY ?
# ============================================================================
#
# Le Repository est une COUCHE qui encapsule l'accès aux données.
#
# SANS Repository :
#   → Les requêtes SQL sont éparpillées partout dans le code
#   → Difficile à maintenir, à tester, à modifier
#
# AVEC Repository :
#   → Toutes les requêtes pour une entité sont au même endroit
#   → Le reste du code appelle repo.get_by_id() sans connaître le SQL
#   → Facile à tester (on peut remplacer par un mock)
#
# Analogie :
#   Repository = un bibliothécaire
#   → Vous lui demandez "donne-moi le livre X"
#   → Il sait OÙ et COMMENT le trouver
#   → Vous n'avez pas besoin de connaître le système de rangement

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

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r}, active={self.is_active})"

# ============================================================================
# 2. LE REPOSITORY
# ============================================================================

class UserRepository:
    """
    Repository pour les utilisateurs.
    Encapsule TOUTES les opérations de base de données pour User.

    Utilisation :
        with Session(engine) as session:
            repo = UserRepository(session)
            user = repo.get_by_id(1)
            users = repo.list_active()
    """

    def __init__(self, session: Session):
        """
        Initialiser le repository avec une session.
        Le repository ne crée PAS la session, il la REÇOIT.
        → C'est l'appelant qui gère le cycle de vie de la session.
        """
        self.session = session

    # ---- LECTURE ----

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Récupérer un utilisateur par son ID"""
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        """Récupérer un utilisateur par son email"""
        stmt = select(User).where(User.email == email)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_all(self, limit: int = 100) -> list[User]:
        """Lister tous les utilisateurs"""
        stmt = select(User).limit(limit)
        return self.session.execute(stmt).scalars().all()

    def list_active(self, limit: int = 100) -> list[User]:
        """Lister uniquement les utilisateurs actifs"""
        stmt = select(User).where(User.is_active == True).limit(limit)
        return self.session.execute(stmt).scalars().all()

    def search_by_name(self, query: str) -> list[User]:
        """Rechercher des utilisateurs par nom (insensible à la casse)"""
        stmt = select(User).where(User.name.ilike(f"%{query}%"))
        return self.session.execute(stmt).scalars().all()

    # ---- CRÉATION ----

    def create(self, name: str, email: str, **kwargs) -> User:
        """Créer un nouvel utilisateur"""
        user = User(name=name, email=email, **kwargs)
        self.session.add(user)
        return user  # Pas de commit ici ! Le service gère les transactions

    # ---- MISE À JOUR ----

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Mettre à jour un utilisateur"""
        user = self.get_by_id(user_id)
        if user is None:
            return None
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user

    # ---- SUPPRESSION ----

    def delete(self, user_id: int) -> bool:
        """Supprimer un utilisateur"""
        user = self.get_by_id(user_id)
        if user is None:
            return False
        self.session.delete(user)
        return True

    # ---- SAUVEGARDE ----

    def save(self) -> None:
        """Sauvegarder les modifications (commit)"""
        self.session.commit()


# ============================================================================
# 3. DÉMONSTRATION
# ============================================================================

def demo():
    """Utiliser le Repository"""

    print("=== DÉMONSTRATION : Pattern Repository ===\n")

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Créer le repository
        repo = UserRepository(session)

        # ---- Créer des utilisateurs ----
        print("  1. Création :")
        repo.create("Alice", "alice@example.com")
        repo.create("Bob", "bob@example.com")
        repo.create("Charlie", "charlie@example.com", is_active=False)
        repo.save()  # Un seul commit pour tout
        print("    ✓ 3 utilisateurs créés")

        # ---- Lire ----
        print("\n  2. Lecture :")
        user = repo.get_by_id(1)
        print(f"    get_by_id(1) → {user}")

        user = repo.get_by_email("bob@example.com")
        print(f"    get_by_email('bob@...') → {user}")

        actifs = repo.list_active()
        print(f"    list_active() → {actifs}")

        # ---- Rechercher ----
        print("\n  3. Recherche :")
        found = repo.search_by_name("ali")
        print(f"    search_by_name('ali') → {found}")

        # ---- Mettre à jour ----
        print("\n  4. Mise à jour :")
        user = repo.update(1, name="Alice Martin")
        repo.save()
        print(f"    update(1, name=...) → {user}")

        # ---- Supprimer ----
        print("\n  5. Suppression :")
        result = repo.delete(3)
        repo.save()
        print(f"    delete(3) → {'OK' if result else 'Non trouvé'}")

        # ---- Vérifier ----
        print("\n  6. Vérification finale :")
        tous = repo.list_all()
        for u in tous:
            print(f"    {u}")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Pattern Repository")
    print("=" * 60)

    demo()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 16")
    print("=" * 60)
