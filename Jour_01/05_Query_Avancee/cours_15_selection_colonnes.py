"""
=============================================================================
 COURS 15 - SÉLECTION DE COLONNES SPÉCIFIQUES
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Sélectionner des colonnes spécifiques (plus performant)
 - NamedTuple pour l'autocomplétion
 - Alias et expressions avec label()

 Pour exécuter :
   python cours_15_selection_colonnes.py
=============================================================================
"""

from typing import NamedTuple
from sqlalchemy import create_engine, String, Integer, Text, select, func
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
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    age: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.first_name} {self.last_name})"

engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

def preparer_donnees():
    """Insérer des données de test"""
    with Session(engine) as session:
        users = [
            User(first_name="Alice", last_name="Martin", email="alice@test.com", bio="Dev Python depuis 5 ans", age=28),
            User(first_name="Bob", last_name="Dupont", email="bob@test.com", bio="Passionné de data science et machine learning", age=35),
            User(first_name="Charlie", last_name="Bernard", email="charlie@test.com", bio=None, age=22),
        ]
        session.add_all(users)
        session.commit()
    print("  ✓ 3 utilisateurs insérés\n")

# ============================================================================
# 1. SÉLECTIONNER DES COLONNES SPÉCIFIQUES
# ============================================================================

def demo_colonnes_specifiques():
    """
    Au lieu de SELECT * (tout charger), on peut sélectionner
    uniquement les colonnes dont on a besoin.

    Avantage : PLUS RAPIDE car moins de données transférées !
    Utile quand une table a beaucoup de colonnes ou des colonnes Text/JSON lourdes.
    """

    print("=== 1. COLONNES SPÉCIFIQUES ===\n")

    with Session(engine) as session:
        # ---- Sélectionner tout (lourd si beaucoup de colonnes) ----
        print("  SELECT * (tout) :")
        stmt = select(User)  # SELECT * FROM users
        users = session.execute(stmt).scalars().all()
        for u in users:
            print(f"    {u} - email={u.email} - bio={u.bio}")

        # ---- Sélectionner SEULEMENT certaines colonnes ----
        print("\n  SELECT id, email (léger) :")
        stmt = select(User.id, User.email)  # SELECT id, email FROM users
        results = session.execute(stmt).all()
        # Chaque résultat est un Row (tuple nommé)
        for row in results:
            print(f"    id={row.id}, email={row.email}")

        # ---- Accéder par index ou par nom ----
        print("\n  Accès par index vs par nom :")
        stmt = select(User.id, User.first_name, User.email)
        row = session.execute(stmt).first()
        print(f"    Par index : row[0]={row[0]}, row[1]={row[1]}")
        print(f"    Par nom   : row.id={row.id}, row.first_name={row.first_name}")


# ============================================================================
# 2. NamedTuple POUR L'AUTOCOMPLÉTION
# ============================================================================

# Définir un NamedTuple pour typer les résultats
class UserSummary(NamedTuple):
    """Résumé d'un utilisateur (seulement les champs essentiels)"""
    id: int
    email: str
    first_name: str


def demo_named_tuple():
    """Utiliser NamedTuple pour avoir l'autocomplétion dans l'IDE"""

    print("\n=== 2. NamedTuple ===\n")

    with Session(engine) as session:
        stmt = select(User.id, User.email, User.first_name)
        rows = session.execute(stmt).all()

        # Convertir chaque row en UserSummary
        summaries = [UserSummary(*row) for row in rows]
        # *row "déballe" le tuple : UserSummary(row[0], row[1], row[2])

        for s in summaries:
            # Autocomplétion dans l'IDE ! s.id, s.email, s.first_name
            print(f"    UserSummary(id={s.id}, email={s.email}, name={s.first_name})")


# ============================================================================
# 3. ALIAS ET EXPRESSIONS AVEC label()
# ============================================================================

def demo_expressions():
    """Créer des colonnes calculées avec label()"""

    print("\n=== 3. EXPRESSIONS ET label() ===\n")

    with Session(engine) as session:
        # ---- Concaténation de colonnes ----
        # Créer un "nom complet" en concaténant prénom + nom
        stmt = select(
            User.id,
            (User.first_name + " " + User.last_name).label("full_name"),
            # .label("full_name") = donner un NOM au résultat
        )
        results = session.execute(stmt).all()
        print("  Nom complet (concaténation) :")
        for row in results:
            print(f"    id={row.id}, full_name={row.full_name}")

        # ---- Fonctions SQL avec label ----
        print("\n  Longueur de la bio :")
        stmt = select(
            User.first_name,
            func.length(User.bio).label("bio_length"),
            # func.length() = LENGTH() en SQL
        )
        results = session.execute(stmt).all()
        for row in results:
            print(f"    {row.first_name:10} → bio_length={row.bio_length}")

        # ---- Expression UPPER ----
        print("\n  Nom en majuscules :")
        stmt = select(
            func.upper(User.first_name).label("upper_name"),
            User.email,
        )
        results = session.execute(stmt).all()
        for row in results:
            print(f"    {row.upper_name} ({row.email})")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Sélection de colonnes spécifiques")
    print("=" * 60)

    preparer_donnees()
    demo_colonnes_specifiques()
    demo_named_tuple()
    demo_expressions()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 15")
    print("=" * 60)
