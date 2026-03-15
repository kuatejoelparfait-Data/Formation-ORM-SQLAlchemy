"""
=============================================================================
 COURS 08 - EAGER LOADING (Solutions au problème N+1)
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique les 3 solutions au problème N+1 :
 1. joinedload  → 1 requête avec JOIN
 2. selectinload → 2 requêtes avec IN (RECOMMANDÉ)
 3. subqueryload → 2 requêtes avec sous-requête

 Pour exécuter :
   python cours_08_eager_loading.py
=============================================================================
"""

from typing import List
from sqlalchemy import create_engine, String, ForeignKey, select, event
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column,
    relationship, Session,
    joinedload, selectinload, subqueryload
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    articles: Mapped[List["Article"]] = relationship(back_populates="author")
    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"

class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="articles")

# Compteur de requêtes
query_count = 0

def setup_db():
    """Créer la base et insérer des données"""
    engine = create_engine("sqlite:///:memory:", echo=False)

    global query_count
    @event.listens_for(engine, "before_cursor_execute")
    def count(conn, cursor, stmt, params, context, executemany):
        global query_count
        query_count += 1

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        for i in range(5):
            user = User(username=f"user_{i}")
            for j in range(3):
                user.articles.append(Article(title=f"Article {j} de user_{i}"))
            session.add(user)
        session.commit()

    return engine

# ============================================================================
# 1. JOINEDLOAD (1 requête avec JOIN)
# ============================================================================

def demo_joinedload():
    """joinedload : charge tout en UNE seule requête avec LEFT JOIN"""

    global query_count

    print("=== 1. JOINEDLOAD (1 requête avec JOIN) ===\n")

    engine = setup_db()

    with Session(engine) as session:
        query_count = 0

        # .options(joinedload(...)) dit à SQLAlchemy de charger
        # les articles EN MÊME TEMPS que les users via un JOIN
        stmt = select(User).options(joinedload(User.articles))

        # .unique() est nécessaire avec joinedload car le JOIN
        # peut dupliquer les lignes User
        users = session.execute(stmt).unique().scalars().all()

        for user in users:
            # PAS de requête supplémentaire ! Tout est déjà chargé
            print(f"    {user.username}: {len(user.articles)} articles")

    print(f"\n  📊 TOTAL : {query_count} requêtes (au lieu de 6 !)")
    print("  ℹ️  SQL : SELECT users.*, articles.* FROM users LEFT JOIN articles...")
    print("  👍 Bien pour : relations 1-1 et petites collections")
    print("  ⚠️  Attention : duplique les données si beaucoup d'enfants")


# ============================================================================
# 2. SELECTINLOAD (2 requêtes avec IN) - RECOMMANDÉ
# ============================================================================

def demo_selectinload():
    """selectinload : 2 requêtes séparées, plus efficace"""

    global query_count

    print("\n=== 2. SELECTINLOAD (2 requêtes - RECOMMANDÉ) ===\n")

    engine = setup_db()

    with Session(engine) as session:
        query_count = 0

        # selectinload : charge les articles dans une 2ème requête
        # avec une clause IN
        stmt = select(User).options(selectinload(User.articles))
        users = session.execute(stmt).scalars().all()

        for user in users:
            print(f"    {user.username}: {len(user.articles)} articles")

    print(f"\n  📊 TOTAL : {query_count} requêtes")
    print("  ℹ️  SQL 1 : SELECT * FROM users")
    print("  ℹ️  SQL 2 : SELECT * FROM articles WHERE author_id IN (1, 2, 3, 4, 5)")
    print("  👍 RECOMMANDÉ pour les collections 1-N")
    print("  👍 Pas de duplication de données")


# ============================================================================
# 3. SUBQUERYLOAD (2 requêtes avec sous-requête)
# ============================================================================

def demo_subqueryload():
    """subqueryload : utilise une sous-requête"""

    global query_count

    print("\n=== 3. SUBQUERYLOAD (2 requêtes avec sous-requête) ===\n")

    engine = setup_db()

    with Session(engine) as session:
        query_count = 0

        stmt = select(User).options(subqueryload(User.articles))
        users = session.execute(stmt).scalars().all()

        for user in users:
            print(f"    {user.username}: {len(user.articles)} articles")

    print(f"\n  📊 TOTAL : {query_count} requêtes")
    print("  ℹ️  SQL : SELECT * FROM articles WHERE author_id IN (SELECT id FROM users)")
    print("  👍 Bien pour : requêtes avec LIMIT (pagination)")


# ============================================================================
# TABLEAU COMPARATIF
# ============================================================================

def afficher_comparaison():
    print("\n=== TABLEAU COMPARATIF ===\n")
    print("  ┌──────────────┬───────────┬─────────────────────────┬──────────────────┐")
    print("  │ Stratégie    │ Requêtes  │ Avantages               │ Usage            │")
    print("  ├──────────────┼───────────┼─────────────────────────┼──────────────────┤")
    print("  │ joinedload   │ 1 (JOIN)  │ Une seule requête       │ Relations 1-1    │")
    print("  │ selectinload │ 2 (IN)    │ Pas de duplication      │ Collections 1-N  │")
    print("  │ subqueryload │ 2 (sub)   │ Marche avec LIMIT       │ Pagination       │")
    print("  │ lazyload     │ N+1       │ Simple                  │ ÉVITER en boucle │")
    print("  └──────────────┴───────────┴─────────────────────────┴──────────────────┘")
    print()
    print("  🏆 RÈGLE D'OR : Utilisez selectinload pour les collections 1-N")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Eager Loading (Solutions N+1)")
    print("=" * 60)

    demo_joinedload()
    demo_selectinload()
    demo_subqueryload()
    afficher_comparaison()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 08 (Jour 2)")
    print("=" * 60)
