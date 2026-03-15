"""
=============================================================================
 COURS 13 - TRI ET PAGINATION
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Tri avec order_by (asc, desc)
 - Pagination avec offset/limit
 - Comptage avec func.count()
 - Fonction de pagination réutilisable

 Pour exécuter :
   python cours_13_tri_pagination.py
=============================================================================
"""

from sqlalchemy import create_engine, String, Integer, select, desc, asc, func
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
    email: Mapped[str] = mapped_column(String(255))
    age: Mapped[int] = mapped_column(Integer, default=0)
    is_admin: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r}, age={self.age})"

engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

def preparer_donnees():
    """Insérer 10 utilisateurs de test"""
    with Session(engine) as session:
        users = [
            User(name="Alice", email="alice@test.com", age=28, is_admin=True),
            User(name="Bob", email="bob@test.com", age=35, is_admin=False),
            User(name="Charlie", email="charlie@test.com", age=22, is_admin=False),
            User(name="Diana", email="diana@test.com", age=31, is_admin=True),
            User(name="Eve", email="eve@test.com", age=27, is_admin=False),
            User(name="Frank", email="frank@test.com", age=42, is_admin=False),
            User(name="Grace", email="grace@test.com", age=19, is_admin=False),
            User(name="Henry", email="henry@test.com", age=38, is_admin=True),
            User(name="Iris", email="iris@test.com", age=25, is_admin=False),
            User(name="Jack", email="jack@test.com", age=33, is_admin=False),
        ]
        session.add_all(users)
        session.commit()
    print("  ✓ 10 utilisateurs insérés\n")

# ============================================================================
# 1. TRI AVEC order_by
# ============================================================================

def demo_tri():
    """Trier les résultats"""

    print("=== 1. TRI AVEC order_by ===\n")

    with Session(engine) as session:
        # ---- Tri ASCENDANT (du plus petit au plus grand) ----
        # Par défaut, order_by trie en ascendant
        stmt = select(User).order_by(User.age)  # ou User.age.asc()
        users = session.execute(stmt).scalars().all()
        print("  Tri par âge (ascendant) :")
        for u in users:
            print(f"    {u.name:10} → {u.age} ans")

        # ---- Tri DESCENDANT (du plus grand au plus petit) ----
        print()
        stmt = select(User).order_by(desc(User.age))  # ou User.age.desc()
        users = session.execute(stmt).scalars().all()
        print("  Tri par âge (descendant) :")
        for u in users[:5]:  # Afficher les 5 premiers
            print(f"    {u.name:10} → {u.age} ans")

        # ---- Tri MULTIPLE (plusieurs critères) ----
        print()
        stmt = select(User).order_by(
            User.is_admin.desc(),   # D'abord les admins
            User.name.asc()         # Puis par nom alphabétique
        )
        users = session.execute(stmt).scalars().all()
        print("  Tri multiple (admins d'abord, puis par nom) :")
        for u in users:
            admin = "ADMIN" if u.is_admin else "     "
            print(f"    [{admin}] {u.name}")


# ============================================================================
# 2. PAGINATION AVEC offset/limit
# ============================================================================

def demo_pagination():
    """Paginer les résultats (afficher par pages)"""

    print("\n=== 2. PAGINATION ===\n")

    with Session(engine) as session:
        page_size = 3  # 3 utilisateurs par page

        # ---- Page 1 ----
        # offset(0) = commencer au début
        # limit(3) = prendre 3 résultats
        stmt = select(User).order_by(User.id).offset(0).limit(page_size)
        page1 = session.execute(stmt).scalars().all()
        print(f"  Page 1 (offset=0, limit={page_size}) :")
        for u in page1:
            print(f"    {u}")

        # ---- Page 2 ----
        # offset(3) = sauter les 3 premiers
        stmt = select(User).order_by(User.id).offset(3).limit(page_size)
        page2 = session.execute(stmt).scalars().all()
        print(f"\n  Page 2 (offset=3, limit={page_size}) :")
        for u in page2:
            print(f"    {u}")

        # ---- Page 3 ----
        stmt = select(User).order_by(User.id).offset(6).limit(page_size)
        page3 = session.execute(stmt).scalars().all()
        print(f"\n  Page 3 (offset=6, limit={page_size}) :")
        for u in page3:
            print(f"    {u}")


# ============================================================================
# 3. FONCTION DE PAGINATION RÉUTILISABLE
# ============================================================================

def get_users_paginated(
    session: Session,
    page: int = 1,         # Numéro de page (commence à 1)
    page_size: int = 5     # Nombre d'éléments par page
) -> list[User]:
    """
    Récupérer les utilisateurs avec pagination.

    Paramètres :
        session   : session SQLAlchemy
        page      : numéro de la page (1, 2, 3...)
        page_size : nombre d'éléments par page

    Retourne :
        Liste d'utilisateurs pour la page demandée

    Formule :
        offset = (page - 1) * page_size
        Page 1 : offset = 0  → éléments 1 à 5
        Page 2 : offset = 5  → éléments 6 à 10
        Page 3 : offset = 10 → éléments 11 à 15
    """
    # Calculer l'offset à partir du numéro de page
    offset = (page - 1) * page_size

    stmt = (
        select(User)
        .order_by(User.id)      # Toujours trier pour une pagination cohérente
        .offset(offset)          # Sauter les éléments des pages précédentes
        .limit(page_size)        # Limiter au nombre d'éléments par page
    )

    return session.execute(stmt).scalars().all()


def demo_fonction_pagination():
    """Utiliser la fonction de pagination"""

    print("\n=== 3. FONCTION DE PAGINATION ===\n")

    with Session(engine) as session:
        # Compter le total
        total = session.execute(select(func.count(User.id))).scalar_one()
        page_size = 4
        total_pages = (total + page_size - 1) // page_size  # Arrondi supérieur

        print(f"  Total : {total} utilisateurs, {total_pages} pages de {page_size}")

        # Afficher chaque page
        for page_num in range(1, total_pages + 1):
            users = get_users_paginated(session, page=page_num, page_size=page_size)
            noms = [u.name for u in users]
            print(f"  Page {page_num}/{total_pages} : {noms}")


# ============================================================================
# 4. COMPTAGE
# ============================================================================

def demo_comptage():
    """Compter les éléments"""

    print("\n=== 4. COMPTAGE ===\n")

    with Session(engine) as session:
        # Compter TOUS les utilisateurs
        total = session.execute(select(func.count(User.id))).scalar_one()
        print(f"  Total utilisateurs    : {total}")

        # Compter avec filtre
        stmt = select(func.count(User.id)).where(User.is_admin == True)
        admins = session.execute(stmt).scalar_one()
        print(f"  Administrateurs       : {admins}")

        # Compter les utilisateurs de plus de 30 ans
        stmt = select(func.count(User.id)).where(User.age > 30)
        seniors = session.execute(stmt).scalar_one()
        print(f"  Plus de 30 ans        : {seniors}")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Tri et Pagination")
    print("=" * 60)

    preparer_donnees()
    demo_tri()
    demo_pagination()
    demo_fonction_pagination()
    demo_comptage()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 13")
    print("=" * 60)
