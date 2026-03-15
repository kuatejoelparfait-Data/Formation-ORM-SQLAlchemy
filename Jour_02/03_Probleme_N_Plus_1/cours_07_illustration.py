"""
=============================================================================
 COURS 07 - LE PROBLÈME N+1 (le piège #1 des ORM)
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Ce qu'est le problème N+1
 - Comment le détecter (avec echo=True)
 - Pourquoi c'est catastrophique en production
 - Exemple concret avec comptage des requêtes

 Pour exécuter :
   python cours_07_illustration.py
=============================================================================
"""

from typing import List
from sqlalchemy import create_engine, String, Text, ForeignKey, select, event
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column,
    relationship, Session
)

# ============================================================================
# 1. LE PROBLÈME N+1 EXPLIQUÉ SIMPLEMENT
# ============================================================================
#
# Imaginez que vous devez afficher une liste de 100 utilisateurs
# avec le nombre d'articles de chacun.
#
# MAUVAIS (N+1) :
#   Requête 1 : SELECT * FROM users               → 1 requête
#   Requête 2 : SELECT * FROM articles WHERE author_id = 1  → user 1
#   Requête 3 : SELECT * FROM articles WHERE author_id = 2  → user 2
#   ...
#   Requête 101 : SELECT * FROM articles WHERE author_id = 100 → user 100
#   TOTAL : 1 + 100 = 101 requêtes !!!
#
# BON (avec eager loading) :
#   Requête 1 : SELECT * FROM users
#   Requête 2 : SELECT * FROM articles WHERE author_id IN (1, 2, ..., 100)
#   TOTAL : 2 requêtes seulement !
#
# En production avec 10 000 utilisateurs :
#   N+1 : 10 001 requêtes → LENT (plusieurs secondes)
#   Eager : 2 requêtes → RAPIDE (quelques millisecondes)

# ============================================================================
# PRÉPARATION
# ============================================================================

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

# ============================================================================
# COMPTEUR DE REQUÊTES (pour la démo)
# ============================================================================

query_count = 0

def count_queries(engine):
    """Compter le nombre de requêtes SQL exécutées"""
    global query_count
    query_count = 0

    @event.listens_for(engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        global query_count
        query_count += 1

# ============================================================================
# 2. DÉMONSTRATION DU PROBLÈME N+1
# ============================================================================

def demo_n_plus_1():
    """Montrer le problème N+1 en action"""

    global query_count

    print("=== DÉMONSTRATION DU PROBLÈME N+1 ===\n")

    engine = create_engine("sqlite:///:memory:", echo=False)
    count_queries(engine)
    Base.metadata.create_all(engine)

    # Insérer des données de test
    with Session(engine) as session:
        for i in range(10):
            user = User(username=f"user_{i}")
            for j in range(3):
                user.articles.append(Article(title=f"Article {j} de user_{i}"))
            session.add(user)
        session.commit()

    # ---- Le code qui cause le N+1 ----
    print("  ❌ MAUVAIS CODE (N+1) :")
    print("  " + "-" * 50)

    with Session(engine) as session:
        query_count = 0  # Remettre le compteur à zéro

        # Requête 1 : charger tous les utilisateurs
        users = session.query(User).all()

        # Pour chaque utilisateur, accéder aux articles
        # → CHAQUE accès à user.articles déclenche une NOUVELLE requête SQL !
        for user in users:
            # Cette ligne cause une requête SELECT pour chaque user
            nb_articles = len(user.articles)
            print(f"    {user.username}: {nb_articles} articles")

    print(f"\n  📊 TOTAL : {query_count} requêtes SQL !")
    print(f"     → 1 (SELECT users) + {query_count - 1} (SELECT articles pour chaque user)")
    print(f"     → Avec 10 000 users, ce serait {10001} requêtes !")

    print("\n  💡 Solution → Voir le cours suivant (cours_08_eager_loading.py)")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Le Problème N+1")
    print("=" * 60)

    demo_n_plus_1()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 07 (Jour 2)")
    print("=" * 60)
