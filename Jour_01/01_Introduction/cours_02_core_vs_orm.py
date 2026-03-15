"""
=============================================================================
 COURS 02 - SQLAlchemy CORE vs ORM
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - La différence entre SQLAlchemy Core et SQLAlchemy ORM
 - Quand utiliser l'un ou l'autre
 - Comment SQLAlchemy 2.0 unifie les deux approches

 Pour exécuter :
   python cours_02_core_vs_orm.py
=============================================================================
"""

# ============================================================================
# 1. SQLAlchemy = DEUX COUCHES
# ============================================================================
#
# SQLAlchemy est composé de deux parties :
#
# ┌─────────────────────────────────────────────┐
# │           SQLAlchemy ORM                     │  ← Haut niveau (objets Python)
# │  (classes, objets, relationships)            │
# ├─────────────────────────────────────────────┤
# │           SQLAlchemy Core                    │  ← Bas niveau (proche du SQL)
# │  (tables, colonnes, expressions SQL)         │
# ├─────────────────────────────────────────────┤
# │           DBAPI (psycopg2, sqlite3...)       │  ← Driver de base de données
# └─────────────────────────────────────────────┘
#
# COMPARAISON :
# ┌──────────────┬──────────────────────────┬──────────────────────────┐
# │   Aspect     │   SQLAlchemy Core        │   SQLAlchemy ORM         │
# ├──────────────┼──────────────────────────┼──────────────────────────┤
# │ Abstraction  │ Bas niveau (proche SQL)  │ Haut niveau (objets)     │
# │ Cas d'usage  │ ETL, requêtes complexes  │ CRUD, APIs REST          │
# │ Performance  │ Plus rapide              │ Plus lent mais productif │
# │ Apprentissage│ Besoin de connaître SQL  │ Plus intuitif            │
# │ Utilisation  │ ~10% des cas             │ ~90% des cas             │
# └──────────────┴──────────────────────────┴──────────────────────────┘

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select, insert
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ============================================================================
# 2. APPROCHE CORE (bas niveau)
# ============================================================================

def demo_core():
    """SQLAlchemy Core : on travaille avec des TABLES et des expressions SQL"""

    print("=== SQLAlchemy CORE ===")

    # Créer le moteur
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Avec Core, on définit la TABLE directement (pas de classe)
    metadata = MetaData()  # Conteneur pour les définitions de tables

    # Définition de la table users avec Core
    users_table = Table(
        "users",                                    # Nom de la table
        metadata,                                   # Métadonnées
        Column("id", Integer, primary_key=True),    # Colonne id
        Column("name", String(100)),                # Colonne name
        Column("email", String(255)),               # Colonne email
    )

    # Créer la table dans la base
    metadata.create_all(engine)

    # Insérer avec Core : on utilise des expressions SQL
    with engine.connect() as conn:
        # INSERT : on construit une expression SQL
        stmt = insert(users_table).values(name="Alice", email="alice@example.com")
        conn.execute(stmt)
        conn.commit()

        # SELECT : on construit une requête SQL
        stmt = select(users_table).where(users_table.c.name == "Alice")
        # users_table.c = accès aux colonnes (c = columns)
        result = conn.execute(stmt)
        row = result.fetchone()

        print(f"  Résultat Core : {row}")
        print(f"  Accès par nom : name={row.name}, email={row.email}")
        # Note : Core retourne des Row, pas des objets


# ============================================================================
# 3. APPROCHE ORM (haut niveau) - RECOMMANDÉE
# ============================================================================

# Avec l'ORM, on définit des CLASSES Python
class Base(DeclarativeBase):
    pass

class User(Base):
    """Modèle ORM : la table 'users' est représentée par une classe Python"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r})"


def demo_orm():
    """SQLAlchemy ORM : on travaille avec des OBJETS Python"""

    print("\n=== SQLAlchemy ORM ===")

    # Créer le moteur
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Créer les tables à partir des classes
    Base.metadata.create_all(engine)

    # Avec ORM, on utilise des Sessions (pas des connexions directes)
    with Session(engine) as session:
        # INSERT : on crée un objet Python
        user = User(name="Alice", email="alice@example.com")
        session.add(user)      # Ajouter à la session
        session.commit()       # Sauvegarder en BDD
        session.refresh(user)  # Recharger depuis la BDD

        # SELECT : on utilise select() avec la classe
        stmt = select(User).where(User.name == "Alice")
        found_user = session.execute(stmt).scalar_one_or_none()

        print(f"  Résultat ORM : {found_user}")
        print(f"  Accès par attribut : name={found_user.name}, email={found_user.email}")
        # Note : ORM retourne des objets User, avec autocomplétion !


# ============================================================================
# 4. SQLAlchemy 2.0 : L'UNIFICATION
# ============================================================================

def demo_sqlalchemy_2():
    """
    SQLAlchemy 2.0 unifie Core et ORM.
    On peut utiliser la syntaxe select() moderne avec les classes ORM.
    C'est le meilleur des deux mondes !
    """

    print("\n=== SQLAlchemy 2.0 (unifié) ===")
    print()
    print("  SQLAlchemy 2.0 permet de :")
    print("  - Utiliser select(User) au lieu de session.query(User)")
    print("  - Mélanger Core et ORM dans la même requête")
    print("  - Avoir un typage complet avec Mapped[]")
    print()
    print("  Conseil professionnel :")
    print("  → Utilisez l'ORM pour 90% de vos besoins (CRUD, APIs)")
    print("  → Descendez vers Core pour les requêtes complexes ou bulk")
    print("  → SQLAlchemy 2.0 rend le passage de l'un à l'autre facile")


# ============================================================================
# 5. EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : SQLAlchemy Core vs ORM")
    print("=" * 60)

    demo_core()
    demo_orm()
    demo_sqlalchemy_2()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 02")
    print("=" * 60)
