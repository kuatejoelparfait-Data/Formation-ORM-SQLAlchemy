"""
=============================================================================
 COURS 12 - DELETE (Suppression de données)
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Suppression d'un seul objet (session.delete)
 - Suppression en masse (delete statement)
 - Soft Delete : la meilleure pratique en entreprise

 Pour exécuter :
   python cours_12_delete.py
=============================================================================
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, String, DateTime, delete, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

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
    # Champ pour le Soft Delete (voir section 3)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    @property
    def is_deleted(self) -> bool:
        """Vérifie si l'utilisateur est supprimé (soft delete)"""
        return self.deleted_at is not None

    def __repr__(self) -> str:
        deleted = " [SUPPRIMÉ]" if self.is_deleted else ""
        return f"User(id={self.id}, name={self.name!r}{deleted})"

engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

def preparer_donnees():
    """Insérer des données de test"""
    with Session(engine) as session:
        users = [
            User(name="Alice", email="alice@example.com", is_active=True),
            User(name="Bob", email="bob@example.com", is_active=True),
            User(name="Charlie", email="charlie@example.com", is_active=False),
            User(name="Diana", email="diana@example.com", is_active=False),
            User(name="Eve", email="eve@example.com", is_active=True),
        ]
        session.add_all(users)
        session.commit()
    print("  ✓ 5 utilisateurs insérés\n")

# ============================================================================
# 1. SUPPRESSION D'UN SEUL OBJET
# ============================================================================

def demo_delete_simple():
    """Supprimer un objet avec session.delete()"""

    print("=== 1. SUPPRESSION SIMPLE ===\n")

    with Session(engine) as session:
        # Compter avant
        total_avant = session.query(User).count()
        print(f"  Total avant : {total_avant}")

        # Étape 1 : Récupérer l'objet à supprimer
        user = session.get(User, 5)  # Eve (id=5)
        print(f"  Suppression de : {user}")

        if user:
            # Étape 2 : Supprimer
            session.delete(user)

            # Étape 3 : Valider
            session.commit()

        # Compter après
        total_apres = session.query(User).count()
        print(f"  Total après : {total_apres}")


# ============================================================================
# 2. SUPPRESSION EN MASSE
# ============================================================================

def demo_bulk_delete():
    """Supprimer plusieurs lignes avec une requête SQL"""

    print("\n=== 2. SUPPRESSION EN MASSE ===\n")

    with Session(engine) as session:
        # Afficher avant
        users = session.execute(select(User)).scalars().all()
        print("  Avant :")
        for u in users:
            print(f"    {u}")

        # Supprimer TOUS les utilisateurs inactifs en une requête
        stmt = delete(User).where(User.is_active == False)

        result = session.execute(stmt)
        session.commit()

        # result.rowcount = nombre de lignes supprimées
        print(f"\n  {result.rowcount} utilisateurs inactifs supprimés")

        # Afficher après
        session.expire_all()
        users = session.execute(select(User)).scalars().all()
        print("\n  Après :")
        for u in users:
            print(f"    {u}")


# ============================================================================
# 3. SOFT DELETE (MEILLEURE PRATIQUE EN ENTREPRISE)
# ============================================================================

def demo_soft_delete():
    """
    Le Soft Delete : marquer comme supprimé SANS supprimer physiquement.

    POURQUOI ?
    - Conservation de l'historique (audit, traçabilité)
    - Conformité légale (RGPD : garder les logs)
    - Possibilité de RESTAURER les données supprimées par erreur
    - Les suppressions physiques sont IRRÉVERSIBLES !

    COMMENT ?
    - Ajouter une colonne 'deleted_at' (datetime, nullable)
    - Si deleted_at est NULL → l'utilisateur est actif
    - Si deleted_at a une valeur → l'utilisateur est "supprimé"
    """

    print("\n=== 3. SOFT DELETE (MEILLEURE PRATIQUE) ===\n")

    with Session(engine) as session:
        # Récupérer Alice
        user = session.get(User, 1)
        print(f"  Avant soft delete : {user}")
        print(f"    deleted_at = {user.deleted_at}")
        print(f"    is_deleted = {user.is_deleted}")

        # "Supprimer" en mettant la date de suppression
        user.deleted_at = datetime.now()
        session.commit()
        session.refresh(user)

        print(f"\n  Après soft delete : {user}")
        print(f"    deleted_at = {user.deleted_at}")
        print(f"    is_deleted = {user.is_deleted}")

        # Pour LIRE les données, on filtre les "supprimés"
        stmt = select(User).where(User.deleted_at.is_(None))  # Non supprimés
        users_actifs = session.execute(stmt).scalars().all()
        print(f"\n  Utilisateurs non supprimés : {users_actifs}")

        # RESTAURER un utilisateur supprimé
        user.deleted_at = None  # Remettre à NULL
        session.commit()
        print(f"\n  Après restauration : {user}")
        print(f"    is_deleted = {user.is_deleted}")


# ============================================================================
# 4. FONCTION delete_user COMPLÈTE
# ============================================================================

def delete_user(session: Session, user_id: int, soft: bool = True) -> bool:
    """
    Supprimer un utilisateur.

    Paramètres :
        session : session SQLAlchemy
        user_id : ID de l'utilisateur
        soft    : True = soft delete (défaut), False = suppression physique

    Retourne :
        True si supprimé, False si non trouvé
    """
    user = session.get(User, user_id)
    if user is None:
        return False

    if soft:
        # Soft delete : marquer la date de suppression
        user.deleted_at = datetime.now()
    else:
        # Hard delete : suppression physique (irréversible !)
        session.delete(user)

    session.commit()
    return True


def demo_fonction_delete():
    """Utiliser la fonction delete_user"""

    print("\n=== 4. FONCTION delete_user ===\n")

    with Session(engine) as session:
        # Soft delete (par défaut)
        result = delete_user(session, 1, soft=True)
        print(f"  Soft delete user 1 : {'OK' if result else 'Non trouvé'}")

        # Utilisateur inexistant
        result = delete_user(session, 999)
        print(f"  Delete user 999    : {'OK' if result else 'Non trouvé'}")

        # Vérifier
        user = session.get(User, 1)
        print(f"  User 1 après soft delete : {user}")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : DELETE (Suppression de données)")
    print("=" * 60)

    preparer_donnees()
    demo_delete_simple()

    # Réinsérer des données pour les démos suivantes
    print("\n--- Réinitialisation ---")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    preparer_donnees()

    demo_bulk_delete()

    # Réinsérer pour le soft delete
    print("--- Réinitialisation ---")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    preparer_donnees()

    demo_soft_delete()
    demo_fonction_delete()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 12")
    print("=" * 60)
