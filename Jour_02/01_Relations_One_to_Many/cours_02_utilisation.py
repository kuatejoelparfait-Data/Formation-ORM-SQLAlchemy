"""
=============================================================================
 COURS 02 - UTILISATION DES RELATIONS One-to-Many
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier montre :
 - Créer des objets avec relations
 - Naviguer les relations (parent → enfants, enfant → parent)
 - Requêtes avec relations

 Pour exécuter :
   python cours_02_utilisation.py
=============================================================================
"""

from typing import List
from sqlalchemy import create_engine, String, Text, ForeignKey, select
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column,
    relationship, Session
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    articles: Mapped[List["Article"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"

class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="articles")
    def __repr__(self) -> str:
        return f"Article(id={self.id}, title={self.title!r})"

# ============================================================================
# PRÉPARATION
# ============================================================================

engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

def preparer_donnees():
    """Insérer des données de test"""
    with Session(engine) as session:
        alice = User(username="alice", articles=[
            Article(title="Apprendre Python", content="Python est un langage..."),
            Article(title="SQLAlchemy Guide", content="SQLAlchemy est un ORM..."),
        ])
        bob = User(username="bob", articles=[
            Article(title="Docker pour débutants", content="Docker permet de..."),
        ])
        charlie = User(username="charlie")  # Pas d'articles
        session.add_all([alice, bob, charlie])
        session.commit()
    print("  ✓ Données de test insérées\n")

# ============================================================================
# 1. NAVIGUER LES RELATIONS
# ============================================================================

def demo_navigation():
    """Accéder aux relations parent ↔ enfant"""

    print("=== 1. NAVIGUER LES RELATIONS ===\n")

    with Session(engine) as session:
        # ---- Du PARENT vers les ENFANTS ----
        # User → Articles (1 vers N)
        alice = session.execute(
            select(User).where(User.username == "alice")
        ).scalar_one()

        print(f"  Articles de {alice.username} :")
        for article in alice.articles:
            print(f"    - {article.title}")

        # ---- De l'ENFANT vers le PARENT ----
        # Article → User (N vers 1)
        article = session.get(Article, 1)
        print(f"\n  L'article '{article.title}' a été écrit par : {article.author.username}")

        # ---- User sans articles ----
        charlie = session.execute(
            select(User).where(User.username == "charlie")
        ).scalar_one()
        print(f"\n  Articles de {charlie.username} : {charlie.articles}")  # Liste vide []


# ============================================================================
# 2. AJOUTER ET RETIRER DES RELATIONS
# ============================================================================

def demo_modifier_relations():
    """Ajouter et retirer des articles d'un utilisateur"""

    print("\n=== 2. MODIFIER LES RELATIONS ===\n")

    with Session(engine) as session:
        alice = session.execute(
            select(User).where(User.username == "alice")
        ).scalar_one()

        print(f"  Avant : {len(alice.articles)} articles")

        # ---- Ajouter un article ----
        nouvel_article = Article(title="FastAPI Tutorial", content="FastAPI est un framework...")
        alice.articles.append(nouvel_article)
        session.commit()
        print(f"  Après ajout : {len(alice.articles)} articles")

        # ---- Retirer un article (le supprime car cascade delete-orphan) ----
        article_a_supprimer = alice.articles[0]
        print(f"  Suppression de : {article_a_supprimer.title}")
        alice.articles.remove(article_a_supprimer)
        session.commit()
        print(f"  Après suppression : {len(alice.articles)} articles")

        # Afficher les articles restants
        for a in alice.articles:
            print(f"    - {a.title}")


# ============================================================================
# 3. REQUÊTES AVEC RELATIONS
# ============================================================================

def demo_requetes():
    """Faire des requêtes qui utilisent les relations"""

    print("\n=== 3. REQUÊTES AVEC RELATIONS ===\n")

    with Session(engine) as session:
        # ---- Articles d'un utilisateur spécifique ----
        stmt = select(Article).join(User).where(User.username == "alice")
        articles = session.execute(stmt).scalars().all()
        print(f"  Articles d'Alice : {[a.title for a in articles]}")

        # ---- Tous les articles avec leur auteur ----
        stmt = select(Article)
        articles = session.execute(stmt).scalars().all()
        print("\n  Tous les articles avec leur auteur :")
        for article in articles:
            print(f"    '{article.title}' par {article.author.username}")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Utilisation des relations 1-N")
    print("=" * 60)

    preparer_donnees()
    demo_navigation()
    demo_modifier_relations()
    demo_requetes()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 02 (Jour 2)")
    print("=" * 60)
