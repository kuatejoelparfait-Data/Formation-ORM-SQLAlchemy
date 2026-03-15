"""
=============================================================================
 COURS 04 - RELATIONS MANY-TO-MANY (N-N) avec Table d'Association
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Ce qu'est une relation Many-to-Many (N-N)
 - La table d'association (table intermédiaire)
 - Le paramètre secondary dans relationship()

 Pour exécuter :
   python cours_04_table_association.py
=============================================================================
"""

from typing import List
from sqlalchemy import create_engine, String, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

# ============================================================================
# 1. QU'EST-CE QU'UNE RELATION MANY-TO-MANY ?
# ============================================================================
#
# Many-to-Many = PLUSIEURS objets liés à PLUSIEURS autres
#
# Exemples :
#   - 1 Article peut avoir PLUSIEURS Tags
#   - 1 Tag peut être sur PLUSIEURS Articles
#   → C'est une relation N-N !
#
#   - 1 Étudiant suit PLUSIEURS Cours
#   - 1 Cours a PLUSIEURS Étudiants
#   → Aussi une relation N-N !
#
# PROBLÈME : En base de données relationnelle, on ne peut PAS
# avoir directement une relation N-N. Il faut une TABLE INTERMÉDIAIRE
# (appelée "table d'association" ou "table de jonction").
#
#   articles ←→ article_tags ←→ tags
#     (1-N)                    (N-1)

# ============================================================================
# 2. DÉFINITION
# ============================================================================

class Base(DeclarativeBase):
    pass

# ---- TABLE D'ASSOCIATION ----
# Cette table n'a PAS de classe Python (pas de modèle)
# Elle contient seulement les deux clés étrangères
article_tags = Table(
    "article_tags",                    # Nom de la table
    Base.metadata,                     # Métadonnées de la base
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)
# Les deux colonnes forment ensemble la CLÉ PRIMAIRE COMPOSITE
# → Un même article ne peut pas avoir le même tag deux fois


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))

    # ---- RELATION N-N avec Tag ----
    # secondary=article_tags : utiliser la table d'association
    # back_populates="articles" : lien bidirectionnel avec Tag.articles
    tags: Mapped[List["Tag"]] = relationship(
        secondary=article_tags,         # Table intermédiaire
        back_populates="articles"       # Relation inverse dans Tag
    )

    def __repr__(self) -> str:
        return f"Article(id={self.id}, title={self.title!r})"


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    # ---- RELATION INVERSE ----
    articles: Mapped[List["Article"]] = relationship(
        secondary=article_tags,         # Même table d'association
        back_populates="tags"           # Relation inverse dans Article
    )

    def __repr__(self) -> str:
        return f"Tag(id={self.id}, name={self.name!r})"


# ============================================================================
# 3. DÉMONSTRATION
# ============================================================================

def demo():
    """Créer des articles avec des tags (relation N-N)"""

    print("=== DÉMONSTRATION : Relation Many-to-Many ===\n")

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # ---- Créer des tags ----
        python_tag = Tag(name="Python")
        web_tag = Tag(name="Web")
        data_tag = Tag(name="Data")
        devops_tag = Tag(name="DevOps")
        session.add_all([python_tag, web_tag, data_tag, devops_tag])

        # ---- Créer des articles avec des tags ----
        article1 = Article(
            title="FastAPI Tutorial",
            tags=[python_tag, web_tag]              # 2 tags
        )
        article2 = Article(
            title="Pandas pour débutants",
            tags=[python_tag, data_tag]             # 2 tags
        )
        article3 = Article(
            title="Docker 101",
            tags=[devops_tag]                        # 1 tag
        )

        session.add_all([article1, article2, article3])
        session.commit()

        # ---- Afficher les articles avec leurs tags ----
        print("  Articles et leurs tags :")
        articles = session.query(Article).all()
        for article in articles:
            tag_names = [t.name for t in article.tags]
            print(f"    '{article.title}' → tags: {tag_names}")

        # ---- Afficher les tags avec leurs articles ----
        print("\n  Tags et leurs articles :")
        tags = session.query(Tag).all()
        for tag in tags:
            article_titles = [a.title for a in tag.articles]
            print(f"    #{tag.name} → articles: {article_titles}")

        # ---- Le tag Python est utilisé par combien d'articles ? ----
        print(f"\n  Le tag 'Python' est sur {len(python_tag.articles)} articles")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Relations Many-to-Many (N-N)")
    print("=" * 60)

    demo()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 04 (Jour 2)")
    print("=" * 60)
