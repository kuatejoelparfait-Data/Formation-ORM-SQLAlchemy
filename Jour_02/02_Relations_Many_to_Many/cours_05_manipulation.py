"""
=============================================================================
 COURS 05 - MANIPULATION DES RELATIONS N-N
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier montre :
 - Ajouter/retirer des tags d'un article
 - Requêtes sur les relations N-N (JOIN)
 - Trouver les articles d'un tag et vice versa

 Pour exécuter :
   python cours_05_manipulation.py
=============================================================================
"""

from typing import List
from sqlalchemy import create_engine, String, Table, Column, Integer, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

class Base(DeclarativeBase):
    pass

article_tags = Table(
    "article_tags", Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    tags: Mapped[List["Tag"]] = relationship(secondary=article_tags, back_populates="articles")
    def __repr__(self) -> str:
        return f"Article(id={self.id}, title={self.title!r})"

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    articles: Mapped[List["Article"]] = relationship(secondary=article_tags, back_populates="tags")
    def __repr__(self) -> str:
        return f"Tag({self.name!r})"

# ============================================================================
# PRÉPARATION
# ============================================================================

engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

def preparer():
    with Session(engine) as session:
        t1 = Tag(name="Python")
        t2 = Tag(name="Web")
        t3 = Tag(name="API")
        t4 = Tag(name="Data")
        a1 = Article(title="FastAPI Tutorial", tags=[t1, t2, t3])
        a2 = Article(title="Pandas Guide", tags=[t1, t4])
        a3 = Article(title="HTML Basics", tags=[t2])
        session.add_all([a1, a2, a3])
        session.commit()
    print("  ✓ Données insérées\n")

# ============================================================================
# 1. AJOUTER UN TAG À UN ARTICLE
# ============================================================================

def demo_ajouter_tag():
    """Ajouter un tag à un article existant"""

    print("=== 1. AJOUTER UN TAG ===\n")

    with Session(engine) as session:
        article = session.get(Article, 3)  # "HTML Basics"
        print(f"  Avant : {article.title} → tags: {[t.name for t in article.tags]}")

        # Ajouter un tag existant
        api_tag = session.execute(
            select(Tag).where(Tag.name == "API")
        ).scalar_one()

        article.tags.append(api_tag)
        session.commit()

        print(f"  Après : {article.title} → tags: {[t.name for t in article.tags]}")


# ============================================================================
# 2. RETIRER UN TAG D'UN ARTICLE
# ============================================================================

def demo_retirer_tag():
    """Retirer un tag d'un article (le tag n'est PAS supprimé)"""

    print("\n=== 2. RETIRER UN TAG ===\n")

    with Session(engine) as session:
        article = session.get(Article, 1)  # "FastAPI Tutorial"
        print(f"  Avant : {article.title} → tags: {[t.name for t in article.tags]}")

        # Trouver le tag à retirer
        web_tag = None
        for tag in article.tags:
            if tag.name == "Web":
                web_tag = tag
                break

        if web_tag:
            article.tags.remove(web_tag)  # Retire la RELATION, pas le tag !
            session.commit()

        print(f"  Après : {article.title} → tags: {[t.name for t in article.tags]}")

        # Le tag "Web" existe toujours !
        web = session.execute(select(Tag).where(Tag.name == "Web")).scalar_one_or_none()
        print(f"  Le tag 'Web' existe encore : {web is not None}")


# ============================================================================
# 3. REQUÊTES SUR LES RELATIONS N-N
# ============================================================================

def demo_requetes():
    """Requêtes avec JOIN sur les relations N-N"""

    print("\n=== 3. REQUÊTES N-N ===\n")

    with Session(engine) as session:
        # ---- Articles avec un tag spécifique ----
        print("  Articles avec le tag 'Python' :")
        stmt = select(Article).join(Article.tags).where(Tag.name == "Python")
        articles = session.execute(stmt).scalars().all()
        for a in articles:
            print(f"    - {a.title}")

        # ---- Tags d'un article spécifique ----
        print("\n  Tags de 'FastAPI Tutorial' :")
        stmt = select(Tag).join(Tag.articles).where(Article.title == "FastAPI Tutorial")
        tags = session.execute(stmt).scalars().all()
        for t in tags:
            print(f"    - #{t.name}")

        # ---- Nombre d'articles par tag ----
        print("\n  Nombre d'articles par tag :")
        from sqlalchemy import func
        stmt = (
            select(Tag.name, func.count(Article.id).label("count"))
            .join(Tag.articles)
            .group_by(Tag.name)
            .order_by(func.count(Article.id).desc())
        )
        results = session.execute(stmt).all()
        for name, count in results:
            print(f"    #{name} → {count} articles")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Manipulation des relations N-N")
    print("=" * 60)

    preparer()
    demo_ajouter_tag()
    demo_retirer_tag()
    demo_requetes()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 05 (Jour 2)")
    print("=" * 60)
