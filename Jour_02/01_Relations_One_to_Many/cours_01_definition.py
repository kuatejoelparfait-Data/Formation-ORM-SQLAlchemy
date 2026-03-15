"""
=============================================================================
 COURS 01 - RELATIONS ONE-TO-MANY (1-N)
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Ce qu'est une relation One-to-Many (1 utilisateur → N articles)
 - ForeignKey : la clé étrangère
 - relationship() : le lien entre les classes Python
 - back_populates : la relation bidirectionnelle
 - cascade : que faire quand on supprime le parent

 Pour exécuter :
   python cours_01_definition.py
=============================================================================
"""

from typing import List, Optional
from sqlalchemy import create_engine, String, Text, ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column,
    relationship, Session
)

# ============================================================================
# 1. QU'EST-CE QU'UNE RELATION ONE-TO-MANY ?
# ============================================================================
#
# One-to-Many = UN parent a PLUSIEURS enfants
#
# Exemples :
#   - 1 Utilisateur → N Articles  (un auteur écrit plusieurs articles)
#   - 1 Catégorie   → N Produits  (une catégorie contient plusieurs produits)
#   - 1 Équipe      → N Joueurs   (une équipe a plusieurs joueurs)
#
# En base de données, c'est l'ENFANT qui a la clé étrangère vers le parent.
#   Table articles : author_id → pointe vers users.id

# ============================================================================
# 2. DÉFINITION DES MODÈLES
# ============================================================================

class Base(DeclarativeBase):
    pass


class User(Base):
    """
    Le PARENT : un utilisateur peut avoir PLUSIEURS articles.
    C'est le côté "One" de la relation One-to-Many.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)

    # ---- LA RELATION ----
    # articles : liste des articles de cet utilisateur
    # Mapped[List["Article"]] : le type est une LISTE d'Articles
    # relationship() : crée le lien entre User et Article
    # back_populates="author" : lien bidirectionnel (Article.author → User)
    # cascade="all, delete-orphan" : si on supprime le User, ses articles sont aussi supprimés
    articles: Mapped[List["Article"]] = relationship(
        back_populates="author",           # Nom de l'attribut dans Article
        cascade="all, delete-orphan"       # Suppression en cascade
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"


class Article(Base):
    """
    L'ENFANT : un article appartient à UN seul utilisateur.
    C'est le côté "Many" de la relation One-to-Many.
    """
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)

    # ---- CLÉ ÉTRANGÈRE ----
    # author_id : référence vers l'ID de l'utilisateur
    # ForeignKey("users.id") : pointe vers la colonne id de la table users
    # C'est TOUJOURS l'enfant qui a la clé étrangère !
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # ---- LA RELATION INVERSE ----
    # author : l'objet User associé (pas juste l'ID)
    # Mapped["User"] : un seul User (pas une liste)
    # back_populates="articles" : lien vers User.articles
    author: Mapped["User"] = relationship(back_populates="articles")

    def __repr__(self) -> str:
        return f"Article(id={self.id}, title={self.title!r})"


# ============================================================================
# 3. DÉMONSTRATION
# ============================================================================

def demo():
    """Créer des utilisateurs avec des articles"""

    print("=== DÉMONSTRATION : Relation One-to-Many ===\n")

    # Créer la base de données en mémoire
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # ---- Méthode 1 : Créer le User AVEC ses articles ----
        print("  1. Créer un user avec ses articles :")
        user = User(
            username="alice",
            email="alice@example.com",
            articles=[
                Article(title="Mon premier article", content="Contenu du premier article..."),
                Article(title="SQLAlchemy 101", content="Guide complet de SQLAlchemy..."),
                Article(title="Python et les BDD", content="Comment utiliser Python avec les BDD..."),
            ]
        )
        session.add(user)  # Ajoute AUSSI les articles automatiquement (cascade)
        session.commit()

        print(f"    User créé : {user}")
        print(f"    Nombre d'articles : {len(user.articles)}")
        for article in user.articles:
            print(f"      - {article}")

        # ---- Méthode 2 : Ajouter un article à un user existant ----
        print("\n  2. Ajouter un article à un user existant :")
        new_article = Article(title="Nouvel article", content="Contenu...")
        user.articles.append(new_article)  # Ajouter à la liste
        session.commit()

        print(f"    Articles après ajout : {len(user.articles)}")

        # ---- Accéder à l'auteur depuis un article ----
        print("\n  3. Accéder à l'auteur depuis un article :")
        article = session.get(Article, 1)
        print(f"    Article : {article}")
        print(f"    Auteur  : {article.author}")           # L'objet User
        print(f"    Nom     : {article.author.username}")   # Accès aux attributs


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Relations One-to-Many (1-N)")
    print("=" * 60)

    demo()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 01 (Jour 2)")
    print("=" * 60)
