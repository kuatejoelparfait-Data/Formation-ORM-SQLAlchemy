"""
=============================================================================
 COURS 10 - READ (Lecture de données)
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - session.get() pour récupérer par clé primaire
 - Query API (style SQLAlchemy 1.x)
 - Select API (style SQLAlchemy 2.0 moderne)
 - Filtres avancés : and_, or_, in_, like, ilike, is_

 Pour exécuter :
   python cours_10_read.py
=============================================================================
"""

from sqlalchemy import create_engine, String, select, and_, or_, not_
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

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r}, active={self.is_active})"

engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

# Insérer des données de test
def preparer_donnees():
    """Insérer des utilisateurs de test"""
    with Session(engine) as session:
        users = [
            User(name="Alice", email="alice@gmail.com", is_active=True),
            User(name="Bob", email="bob@outlook.com", is_active=True),
            User(name="Charlie", email="charlie@gmail.com", is_active=False),
            User(name="Diana", email="diana@yahoo.com", is_active=True),
            User(name="Eve", email="eve@outlook.com", is_active=False),
        ]
        session.add_all(users)
        session.commit()
    print("  ✓ 5 utilisateurs de test insérés\n")

# ============================================================================
# 1. session.get() - PAR CLÉ PRIMAIRE
# ============================================================================

def demo_get():
    """Récupérer un objet par sa clé primaire (le plus rapide)"""

    print("=== 1. session.get() - Par clé primaire ===\n")

    with Session(engine) as session:
        # session.get(Classe, id) : récupérer par clé primaire
        user = session.get(User, 1)        # Chercher l'user avec id=1
        print(f"  get(User, 1) → {user}")

        # Si l'ID n'existe pas, retourne None
        user = session.get(User, 999)
        print(f"  get(User, 999) → {user}")  # None


# ============================================================================
# 2. QUERY API (style SQLAlchemy 1.x - toujours supporté)
# ============================================================================

def demo_query_api():
    """L'ancienne API de requêtes (toujours valide en 2.0)"""

    print("\n=== 2. Query API (style 1.x) ===\n")

    with Session(engine) as session:
        # ---- filter() : filtrer avec des expressions ----
        user = session.query(User).filter(User.email == "alice@gmail.com").first()
        print(f"  filter(email==...) → {user}")

        # ---- filter_by() : filtrer avec des mots-clés (plus simple) ----
        user = session.query(User).filter_by(name="Bob").first()
        print(f"  filter_by(name=...) → {user}")

        # ---- .first() : premier résultat ou None ----
        premier = session.query(User).first()
        print(f"  .first() → {premier}")

        # ---- .all() : TOUS les résultats (liste) ----
        tous = session.query(User).all()
        print(f"  .all() → {len(tous)} utilisateurs")

        # ---- .one() : exactement UN résultat (erreur si 0 ou >1) ----
        try:
            unique = session.query(User).filter_by(name="Alice").one()
            print(f"  .one() → {unique}")
        except Exception as e:
            print(f"  .one() erreur → {e}")


# ============================================================================
# 3. SELECT API (style SQLAlchemy 2.0 - RECOMMANDÉ)
# ============================================================================

def demo_select_api():
    """La nouvelle API moderne (recommandée pour les nouveaux projets)"""

    print("\n=== 3. Select API (style 2.0 - RECOMMANDÉ) ===\n")

    with Session(engine) as session:
        # ---- select() + where() ----
        # Construire la requête
        stmt = select(User).where(User.email == "alice@gmail.com")
        # Exécuter et récupérer UN résultat
        user = session.execute(stmt).scalar_one_or_none()
        print(f"  select + where → {user}")

        # ---- scalar_one_or_none() : un résultat ou None ----
        # scalar_one_or_none() = like first() mais retourne l'objet directement

        # ---- scalars().all() : liste d'objets ----
        stmt = select(User).where(User.is_active == True)
        users = session.execute(stmt).scalars().all()
        print(f"  users actifs → {users}")

        # ---- Différence execute() vs scalars() ----
        # execute() retourne des Row (tuples)
        # scalars() retourne directement les objets
        # scalars().all() = liste d'objets


# ============================================================================
# 4. FILTRES AVANCÉS
# ============================================================================

def demo_filtres():
    """Tous les types de filtres disponibles"""

    print("\n=== 4. Filtres avancés ===\n")

    with Session(engine) as session:
        # ---- AND implicite (plusieurs where) ----
        stmt = select(User).where(
            User.is_active == True,    # Première condition
            User.name != "Alice"       # ET deuxième condition
        )
        users = session.execute(stmt).scalars().all()
        print(f"  AND implicite (actifs sauf Alice) → {[u.name for u in users]}")

        # ---- OR explicite ----
        stmt = select(User).where(
            or_(
                User.email.like("%@gmail.com"),     # Email Gmail
                User.email.like("%@outlook.com")    # OU Email Outlook
            )
        )
        users = session.execute(stmt).scalars().all()
        print(f"  OR (gmail ou outlook) → {[u.name for u in users]}")

        # ---- IN : dans une liste ----
        ids = [1, 3, 5]
        stmt = select(User).where(User.id.in_(ids))
        users = session.execute(stmt).scalars().all()
        print(f"  IN (ids 1,3,5) → {[u.name for u in users]}")

        # ---- LIKE : contient un texte (sensible à la casse) ----
        stmt = select(User).where(User.name.like("A%"))  # Commence par A
        users = session.execute(stmt).scalars().all()
        print(f"  LIKE 'A%' → {[u.name for u in users]}")

        # ---- ILIKE : comme LIKE mais INSENSIBLE à la casse ----
        stmt = select(User).where(User.name.ilike("%ali%"))
        users = session.execute(stmt).scalars().all()
        print(f"  ILIKE '%ali%' → {[u.name for u in users]}")

        # ---- IS NULL / IS NOT NULL ----
        # Note : ici pas de champ nullable, mais la syntaxe est :
        # stmt = select(User).where(User.bio.is_(None))       # IS NULL
        # stmt = select(User).where(User.bio.is_not(None))    # IS NOT NULL

        # ---- NOT ----
        stmt = select(User).where(not_(User.is_active))
        users = session.execute(stmt).scalars().all()
        print(f"  NOT active → {[u.name for u in users]}")

        # ---- Combinaison AND + OR ----
        stmt = select(User).where(
            and_(
                User.is_active == True,
                or_(
                    User.email.like("%@gmail.com"),
                    User.name == "Diana"
                )
            )
        )
        users = session.execute(stmt).scalars().all()
        print(f"  AND + OR combinés → {[u.name for u in users]}")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : READ (Lecture de données)")
    print("=" * 60)

    preparer_donnees()
    demo_get()
    demo_query_api()
    demo_select_api()
    demo_filtres()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 10")
    print("=" * 60)
