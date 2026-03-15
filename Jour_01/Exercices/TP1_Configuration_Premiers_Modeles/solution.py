"""
=============================================================================
 TP 1 - SOLUTION : Configuration et Premiers Modèles
 Formation SQLAlchemy 2.0 - Jour 1
=============================================================================
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, String, Text, Integer, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ============================================================================
# ÉTAPE 1 : Classe de base
# ============================================================================

class Base(DeclarativeBase):
    pass

# ============================================================================
# ÉTAPE 2 : Modèle Article complet
# ============================================================================

class Article(Base):
    """Modèle Article pour un blog"""
    __tablename__ = "articles"

    # Clé primaire auto-incrémentée
    id: Mapped[int] = mapped_column(primary_key=True)

    # Titre : texte de max 200 caractères, obligatoire, avec index
    # L'index accélère les recherches par titre
    title: Mapped[str] = mapped_column(String(200), index=True)

    # Slug : identifiant URL-friendly, unique
    # Ex: "mon-premier-article" au lieu de l'ID
    slug: Mapped[str] = mapped_column(String(250), unique=True)

    # Contenu : texte long sans limite de taille
    content: Mapped[str] = mapped_column(Text)

    # Publié ou brouillon : False par défaut (brouillon)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    # Compteur de vues : 0 par défaut
    view_count: Mapped[int] = mapped_column(Integer, default=0)

    # Date de création : automatiquement mise par la BDD
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Date de dernière modification : mise à jour automatiquement
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=func.now()
    )

    def __repr__(self) -> str:
        status = "publié" if self.is_published else "brouillon"
        return f"Article(id={self.id}, title={self.title!r}, {status})"


# ============================================================================
# ÉTAPE 3 : Moteur et création des tables
# ============================================================================

# Moteur SQLite en mémoire (pour le test)
engine = create_engine("sqlite:///:memory:", echo=False)

# Créer toutes les tables définies par nos modèles
Base.metadata.create_all(engine)
print("✓ Tables créées avec succès")

# ============================================================================
# ÉTAPE 4 : Test complet
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" TP 1 - SOLUTION : Configuration et Premiers Modèles")
    print("=" * 60)

    with Session(engine) as session:
        # Créer un article
        article = Article(
            title="Mon premier article",
            slug="mon-premier-article",
            content="Contenu de mon premier article avec SQLAlchemy 2.0 !",
        )
        session.add(article)
        session.commit()
        session.refresh(article)

        print(f"\n  Article créé : {article}")
        print(f"    ID           : {article.id}")
        print(f"    Title        : {article.title}")
        print(f"    Slug         : {article.slug}")
        print(f"    Content      : {article.content[:50]}...")
        print(f"    is_published : {article.is_published}  (défaut False)")
        print(f"    view_count   : {article.view_count}  (défaut 0)")
        print(f"    created_at   : {article.created_at}")
        print(f"    updated_at   : {article.updated_at}  (None car pas encore modifié)")

        # Modifier l'article pour tester updated_at
        article.title = "Mon premier article (modifié)"
        session.commit()
        session.refresh(article)
        print(f"\n  Après modification :")
        print(f"    Title      : {article.title}")
        print(f"    updated_at : {article.updated_at}")

    print("\n" + "=" * 60)
    print(" TP 1 TERMINÉ avec succès !")
    print("=" * 60)
