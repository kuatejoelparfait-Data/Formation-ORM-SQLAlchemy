"""
=============================================================================
 TP 2 - SOLUTION : CRUD Complet sur Articles
 Formation SQLAlchemy 2.0 - Jour 1
=============================================================================
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, String, Text, Integer, Boolean, DateTime
from sqlalchemy import func, select, update as sql_update, or_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ============================================================================
# MODÈLE
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
        status = "publié" if self.is_published else "brouillon"
        return f"Article(id={self.id}, title={self.title!r}, {status})"

engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

# ============================================================================
# 1. CREATE : Créer un article
# ============================================================================

def create_article(session: Session, title: str, content: str, slug: str) -> Article:
    """Créer un nouvel article et le retourner avec son ID"""
    # Créer l'objet Article
    article = Article(title=title, content=content, slug=slug)
    # Ajouter à la session (préparer l'insertion)
    session.add(article)
    # Sauvegarder en base de données
    session.commit()
    # Recharger pour obtenir l'ID auto-généré et le created_at
    session.refresh(article)
    return article

# ============================================================================
# 2. READ : Récupérer par ID
# ============================================================================

def get_article_by_id(session: Session, article_id: int) -> Optional[Article]:
    """Récupérer un article par sa clé primaire. Retourne None si non trouvé."""
    return session.get(Article, article_id)

# ============================================================================
# 3. READ : Récupérer par slug
# ============================================================================

def get_article_by_slug(session: Session, slug: str) -> Optional[Article]:
    """Récupérer un article par son slug (identifiant URL)"""
    stmt = select(Article).where(Article.slug == slug)
    return session.execute(stmt).scalar_one_or_none()

# ============================================================================
# 4. READ : Lister avec pagination
# ============================================================================

def list_articles(
    session: Session,
    page: int = 1,
    page_size: int = 10,
    published_only: bool = False
) -> list[Article]:
    """Lister les articles avec pagination et filtre optionnel"""
    # Calculer l'offset : page 1 → offset 0, page 2 → offset page_size, etc.
    offset = (page - 1) * page_size

    # Construire la requête de base
    stmt = select(Article)

    # Ajouter le filtre si demandé
    if published_only:
        stmt = stmt.where(Article.is_published == True)

    # Trier par date de création (les plus récents d'abord)
    # Puis paginer avec offset et limit
    stmt = stmt.order_by(Article.created_at.desc()).offset(offset).limit(page_size)

    return session.execute(stmt).scalars().all()

# ============================================================================
# 5. UPDATE : Mise à jour partielle
# ============================================================================

def update_article(session: Session, article_id: int, **updates) -> Optional[Article]:
    """Mettre à jour un article avec les champs fournis en kwargs"""
    # Récupérer l'article
    article = session.get(Article, article_id)
    if article is None:
        return None

    # Modifier chaque champ fourni
    for key, value in updates.items():
        if hasattr(article, key):
            setattr(article, key, value)

    session.commit()
    session.refresh(article)
    return article

# ============================================================================
# 6. UPDATE : Publier un article
# ============================================================================

def publish_article(session: Session, article_id: int) -> Optional[Article]:
    """Publier un article (mettre is_published à True)"""
    article = session.get(Article, article_id)
    if article is None:
        return None

    article.is_published = True
    session.commit()
    session.refresh(article)
    return article

# ============================================================================
# 7. UPDATE : Incrémenter le compteur de vues
# ============================================================================

def increment_view_count(session: Session, article_id: int) -> Optional[Article]:
    """Incrémenter le compteur de vues de 1 (côté SQL, thread-safe)"""
    # Utiliser update() SQL pour incrémenter de façon atomique
    stmt = (
        sql_update(Article)
        .where(Article.id == article_id)
        .values(view_count=Article.view_count + 1)
    )
    result = session.execute(stmt)
    session.commit()

    if result.rowcount == 0:
        return None

    # Expirer le cache et recharger
    session.expire_all()
    return session.get(Article, article_id)

# ============================================================================
# 8. DELETE : Supprimer un article
# ============================================================================

def delete_article(session: Session, article_id: int) -> bool:
    """Supprimer un article. Retourne True si supprimé, False sinon."""
    article = session.get(Article, article_id)
    if article is None:
        return False

    session.delete(article)
    session.commit()
    return True

# ============================================================================
# 9. COUNT : Compter les articles
# ============================================================================

def count_articles(session: Session, published_only: bool = False) -> int:
    """Compter les articles, avec filtre optionnel sur la publication"""
    stmt = select(func.count(Article.id))

    if published_only:
        stmt = stmt.where(Article.is_published == True)

    return session.execute(stmt).scalar_one()

# ============================================================================
# 10. SEARCH : Rechercher dans titre et contenu
# ============================================================================

def search_articles(session: Session, query: str) -> list[Article]:
    """Rechercher un texte dans le titre OU le contenu (insensible à la casse)"""
    stmt = select(Article).where(
        or_(
            Article.title.ilike(f"%{query}%"),
            Article.content.ilike(f"%{query}%"),
        )
    )
    return session.execute(stmt).scalars().all()


# ============================================================================
# SCRIPT DE TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" TP 2 - SOLUTION : CRUD Complet sur Articles")
    print("=" * 60)

    with Session(engine) as session:
        # 1. Créer 5 articles
        print("\n--- 1. Création de 5 articles ---")
        articles_data = [
            ("Apprendre Python", "Guide complet pour apprendre Python de zéro...", "apprendre-python"),
            ("SQLAlchemy 101", "Introduction à SQLAlchemy ORM pour Python...", "sqlalchemy-101"),
            ("FastAPI Tutorial", "Créer des APIs REST avec FastAPI et Python...", "fastapi-tutorial"),
            ("Docker pour débutants", "Conteneurisation avec Docker étape par étape...", "docker-debutants"),
            ("Python et les données", "Data science avec Python, Pandas et NumPy...", "python-donnees"),
        ]
        for title, content, slug in articles_data:
            article = create_article(session, title, content, slug)
            print(f"  ✓ Créé : {article}")

        total = count_articles(session)
        print(f"  Total : {total} articles")

        # 2. Publier 3 articles
        print("\n--- 2. Publication de 3 articles ---")
        for i in [1, 2, 3]:
            publish_article(session, i)
        published = count_articles(session, published_only=True)
        print(f"  ✓ {published} articles publiés")

        # 3. Lister avec pagination
        print("\n--- 3. Pagination (2 par page, publiés uniquement) ---")
        page1 = list_articles(session, page=1, page_size=2, published_only=True)
        print(f"  Page 1 : {[a.title for a in page1]}")
        page2 = list_articles(session, page=2, page_size=2, published_only=True)
        print(f"  Page 2 : {[a.title for a in page2]}")

        # 4. Mettre à jour le titre
        print("\n--- 4. Mise à jour du titre ---")
        updated = update_article(session, 1, title="Maîtriser Python en 30 jours")
        print(f"  ✓ Mis à jour : {updated}")

        # 5. Récupérer par slug
        print("\n--- 5. Récupérer par slug ---")
        article = get_article_by_slug(session, "fastapi-tutorial")
        print(f"  ✓ Trouvé par slug : {article}")

        # 6. Incrémenter les vues
        print("\n--- 6. Incrémenter les vues ---")
        for _ in range(5):
            increment_view_count(session, 1)
        article = get_article_by_id(session, 1)
        print(f"  ✓ Vues de l'article 1 : {article.view_count}")

        # 7. Rechercher
        print("\n--- 7. Recherche 'Python' ---")
        results = search_articles(session, "Python")
        print(f"  ✓ Résultats : {[a.title for a in results]}")

        # 8. Supprimer
        print("\n--- 8. Supprimer le dernier ---")
        deleted = delete_article(session, 5)
        print(f"  ✓ Supprimé : {deleted}")
        print(f"  Total restant : {count_articles(session)}")

    print("\n" + "=" * 60)
    print(" TP 2 TERMINÉ avec succès !")
    print("=" * 60)
