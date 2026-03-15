"""
=============================================================================
 TP 2 - CRUD COMPLET SUR ARTICLES (1h)
 Formation SQLAlchemy 2.0 - Jour 1
=============================================================================

 OBJECTIF :
   Implémenter toutes les opérations CRUD pour le modèle Article.

 FONCTIONS À CRÉER (10 au total) :
   1. create_article(session, title, content, slug)
   2. get_article_by_id(session, article_id)
   3. get_article_by_slug(session, slug)
   4. list_articles(session, page, page_size, published_only)
   5. update_article(session, article_id, **updates)
   6. publish_article(session, article_id)
   7. increment_view_count(session, article_id)
   8. delete_article(session, article_id)
   9. count_articles(session, published_only)
   10. search_articles(session, query)

 SCRIPT DE TEST À LA FIN :
   - Créer 5 articles
   - Publier 3 d'entre eux
   - Lister avec pagination (page 1, 2 par page)
   - Mettre à jour le titre du premier
   - Rechercher "Python" dans les articles
   - Supprimer le dernier
=============================================================================
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, String, Text, Integer, Boolean, DateTime, func, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ============================================================================
# MODÈLE (copié du TP1)
# ============================================================================

class Base(DeclarativeBase):
    pass

class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    slug: Mapped[str] = mapped_column(String(250), unique=True)
    content: Mapped[str] = mapped_column(Text)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    def __repr__(self) -> str:
        return f"Article(id={self.id}, title={self.title!r})"

engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

# ============================================================================
# FONCTIONS CRUD À IMPLÉMENTER
# ============================================================================

def create_article(session: Session, title: str, content: str, slug: str) -> Article:
    """Créer un nouvel article"""
    # TODO : Créer l'objet, l'ajouter, commit, refresh, retourner
    # Indice : session.add(), session.commit(), session.refresh()
    pass


def get_article_by_id(session: Session, article_id: int) -> Optional[Article]:
    """Récupérer un article par son ID"""
    # TODO : Utiliser session.get()
    pass


def get_article_by_slug(session: Session, slug: str) -> Optional[Article]:
    """Récupérer un article par son slug"""
    # TODO : Utiliser select() et where()
    # Indice : session.execute(stmt).scalar_one_or_none()
    pass


def list_articles(session: Session, page: int = 1, page_size: int = 10, published_only: bool = False) -> list[Article]:
    """Lister les articles avec pagination"""
    # TODO : Calculer l'offset, filtrer si published_only, trier par created_at desc
    # Indice : offset = (page - 1) * page_size
    pass


def update_article(session: Session, article_id: int, **updates) -> Optional[Article]:
    """Mettre à jour un article"""
    # TODO : Récupérer l'article, modifier les attributs avec setattr, commit
    # Indice : for key, value in updates.items(): setattr(article, key, value)
    pass


def publish_article(session: Session, article_id: int) -> Optional[Article]:
    """Publier un article (is_published = True)"""
    # TODO : Récupérer et mettre is_published à True
    pass


def increment_view_count(session: Session, article_id: int) -> Optional[Article]:
    """Incrémenter le compteur de vues"""
    # TODO : Utiliser update() avec Article.view_count + 1
    # Indice : stmt = update(Article).where(...).values(view_count=Article.view_count + 1)
    pass


def delete_article(session: Session, article_id: int) -> bool:
    """Supprimer un article"""
    # TODO : Récupérer, supprimer, commit
    # Retourner True si supprimé, False si non trouvé
    pass


def count_articles(session: Session, published_only: bool = False) -> int:
    """Compter les articles"""
    # TODO : Utiliser func.count()
    pass


def search_articles(session: Session, query: str) -> list[Article]:
    """Rechercher dans le titre et le contenu"""
    # TODO : Utiliser ilike() avec or_()
    # Indice : Article.title.ilike(f"%{query}%")
    pass


# ============================================================================
# SCRIPT DE TEST (décommenter quand les fonctions sont prêtes)
# ============================================================================

# if __name__ == "__main__":
#     with Session(engine) as session:
#         # 1. Créer 5 articles
#         articles_data = [
#             ("Apprendre Python", "Guide complet Python...", "apprendre-python"),
#             ("SQLAlchemy 101", "Introduction à SQLAlchemy...", "sqlalchemy-101"),
#             ("FastAPI Tutorial", "Créer des APIs avec FastAPI...", "fastapi-tutorial"),
#             ("Docker pour débutants", "Conteneurisation avec Docker...", "docker-debutants"),
#             ("Python et les données", "Data science avec Python...", "python-donnees"),
#         ]
#         for title, content, slug in articles_data:
#             create_article(session, title, content, slug)
#         print(f"✓ {count_articles(session)} articles créés")
#
#         # 2. Publier 3 articles
#         for i in [1, 2, 3]:
#             publish_article(session, i)
#         print(f"✓ {count_articles(session, published_only=True)} articles publiés")
#
#         # 3. Lister page 1
#         page1 = list_articles(session, page=1, page_size=2, published_only=True)
#         print(f"✓ Page 1 : {[a.title for a in page1]}")
#
#         # 4. Mettre à jour
#         update_article(session, 1, title="Maîtriser Python")
#         print(f"✓ Article 1 mis à jour : {get_article_by_id(session, 1)}")
#
#         # 5. Rechercher
#         results = search_articles(session, "Python")
#         print(f"✓ Recherche 'Python' : {[a.title for a in results]}")
#
#         # 6. Supprimer
#         delete_article(session, 5)
#         print(f"✓ Article 5 supprimé, total : {count_articles(session)}")
