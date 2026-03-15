"""
=============================================================================
 TP 1 - CONFIGURATION ET PREMIERS MODÈLES (45 min)
 Formation SQLAlchemy 2.0 - Jour 1
=============================================================================

 OBJECTIF :
   Mettre en place la configuration SQLAlchemy et créer votre premier modèle.

 CONSIGNES :
   1. Configurer SQLite comme base de données de développement
   2. Créer le modèle Article avec les colonnes listées ci-dessous
   3. Créer les tables avec Base.metadata.create_all(engine)
   4. Insérer un article de test
   5. Le relire et afficher ses attributs

 INDICATIONS :
   - Utilisez Mapped[Optional[...]] pour les champs nullables
   - server_default=func.now() pour created_at côté SQL
   - onupdate=func.now() pour updated_at automatique
   - String(n) pour le texte limité, Text pour le texte long
=============================================================================
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, String, Text, Integer, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ============================================================================
# ÉTAPE 1 : Créer la classe de base
# ============================================================================

class Base(DeclarativeBase):
    pass


# ============================================================================
# ÉTAPE 2 : Créer le modèle Article
# ============================================================================
# Colonnes demandées :
#   - id          : clé primaire, auto-incrémentée
#   - title       : String(200), obligatoire, indexé
#   - slug        : String(250), unique (pour les URLs : "mon-article")
#   - content     : Text (texte long), obligatoire
#   - is_published: Boolean, défaut False
#   - view_count  : Integer, défaut 0
#   - created_at  : DateTime, valeur auto (server_default)
#   - updated_at  : DateTime, mis à jour auto (onupdate)

class Article(Base):
    __tablename__ = "articles"

    # TODO : Définir la clé primaire
    # id: Mapped[int] = ...

    # TODO : Définir le titre (String(200), obligatoire, indexé)
    # title: Mapped[str] = ...

    # TODO : Définir le slug (String(250), unique)
    # slug: Mapped[str] = ...

    # TODO : Définir le contenu (Text, obligatoire)
    # content: Mapped[str] = ...

    # TODO : Définir is_published (Boolean, défaut False)
    # is_published: Mapped[bool] = ...

    # TODO : Définir view_count (Integer, défaut 0)
    # view_count: Mapped[int] = ...

    # TODO : Définir created_at (DateTime, auto)
    # created_at: Mapped[datetime] = ...

    # TODO : Définir updated_at (DateTime, auto sur update)
    # updated_at: Mapped[Optional[datetime]] = ...

    # TODO : Définir __repr__
    pass


# ============================================================================
# ÉTAPE 3 : Configurer le moteur et créer les tables
# ============================================================================

# TODO : Créer le moteur avec SQLite en mémoire
# engine = create_engine(...)

# TODO : Créer les tables
# Base.metadata.create_all(engine)


# ============================================================================
# ÉTAPE 4 : Insérer un article de test
# ============================================================================

# TODO : Créer une session et insérer un article
# with Session(engine) as session:
#     article = Article(
#         title="Mon premier article",
#         slug="mon-premier-article",
#         content="Contenu de mon premier article avec SQLAlchemy !",
#     )
#     session.add(article)
#     session.commit()
#     session.refresh(article)
#     print(f"Article créé : {article}")
#     print(f"  ID         : {article.id}")
#     print(f"  Title      : {article.title}")
#     print(f"  Slug       : {article.slug}")
#     print(f"  Published  : {article.is_published}")
#     print(f"  Views      : {article.view_count}")
#     print(f"  Created at : {article.created_at}")
