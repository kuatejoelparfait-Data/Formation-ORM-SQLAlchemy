"""
=============================================================================
 COURS 09 - EAGER LOADING EN CASCADE (Multi-niveaux)
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Charger plusieurs niveaux de relations en cascade
 - User → Articles → Comments, Articles → Tags
 - La règle d'or : selectinload par défaut

 Pour exécuter :
   python cours_09_comparaison_strategies.py
=============================================================================
"""

from typing import List
from sqlalchemy import (
    create_engine, String, Text, ForeignKey, Table, Column, Integer, select
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column,
    relationship, Session, selectinload
)

class Base(DeclarativeBase):
    pass

# Table d'association Article ↔ Tag
article_tags = Table(
    "article_tags", Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    articles: Mapped[List["Article"]] = relationship(back_populates="author")
    def __repr__(self) -> str:
        return f"User({self.username!r})"

class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="articles")
    comments: Mapped[List["Comment"]] = relationship(back_populates="article")
    tags: Mapped[List["Tag"]] = relationship(secondary=article_tags, back_populates="articles")
    def __repr__(self) -> str:
        return f"Article({self.title!r})"

class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))
    article: Mapped["Article"] = relationship(back_populates="comments")

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    articles: Mapped[List["Article"]] = relationship(secondary=article_tags, back_populates="tags")

# ============================================================================
# PRÉPARATION
# ============================================================================

def setup():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        t1 = Tag(name="Python")
        t2 = Tag(name="Web")
        t3 = Tag(name="Data")

        alice = User(username="alice")
        bob = User(username="bob")

        a1 = Article(title="FastAPI Guide", author=alice, tags=[t1, t2])
        a2 = Article(title="Pandas Tips", author=alice, tags=[t1, t3])
        a3 = Article(title="Docker 101", author=bob, tags=[t2])

        c1 = Comment(content="Super article !", article=a1)
        c2 = Comment(content="Merci beaucoup", article=a1)
        c3 = Comment(content="Très utile", article=a2)

        session.add_all([alice, bob, t1, t2, t3, a1, a2, a3, c1, c2, c3])
        session.commit()

    return engine

# ============================================================================
# EAGER LOADING EN CASCADE
# ============================================================================

def demo_cascade():
    """Charger User → Articles → Comments ET Articles → Tags"""

    print("=== EAGER LOADING EN CASCADE ===\n")

    engine = setup()

    with Session(engine) as session:
        # Charger TOUT en quelques requêtes
        stmt = (
            select(User)
            .options(
                # Charger User.articles avec selectinload
                selectinload(User.articles)
                # Puis charger Article.comments (en cascade)
                .selectinload(Article.comments),

                # Aussi charger Article.tags
                selectinload(User.articles)
                .selectinload(Article.tags),
            )
        )
        users = session.execute(stmt).scalars().all()

        # Maintenant on peut naviguer TOUTES les relations
        # sans déclencher de requêtes supplémentaires !
        for user in users:
            print(f"  👤 {user.username}")
            for article in user.articles:
                tags = [t.name for t in article.tags]
                print(f"    📄 {article.title}  [tags: {', '.join(tags)}]")
                for comment in article.comments:
                    print(f"       💬 {comment.content}")

    print("\n  💡 Tout chargé en quelques requêtes grâce au eager loading !")
    print("     Sans ça, ce code aurait généré des dizaines de requêtes N+1")


# ============================================================================
# RÈGLE D'OR
# ============================================================================

def regle_dor():
    print("\n=== RÈGLE D'OR ===\n")
    print("  1. Activez echo=True en DÉVELOPPEMENT pour voir les requêtes SQL")
    print("  2. Si vous voyez des requêtes répétitives dans une boucle → N+1 !")
    print("  3. Utilisez selectinload() par défaut pour les collections 1-N")
    print("  4. Utilisez joinedload() pour les relations 1-1")
    print("  5. Chaînez les .selectinload() pour charger en cascade")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Eager Loading en Cascade")
    print("=" * 60)

    demo_cascade()
    regle_dor()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 09 (Jour 2)")
    print("=" * 60)
