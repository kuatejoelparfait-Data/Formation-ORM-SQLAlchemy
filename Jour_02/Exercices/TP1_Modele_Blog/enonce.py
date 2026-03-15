"""
=============================================================================
 TP 1 JOUR 2 - MODÈLE DE DONNÉES BLOG (45 min)
 Formation SQLAlchemy 2.0 - Jour 2
=============================================================================

 OBJECTIF :
   Créer un modèle de données complet pour un blog avec relations.

 MODÈLES À CRÉER :
   - User     : id, username, email, bio (optionnel)
   - Category : id, name, slug, description
   - Post     : id, title, slug, content, is_published, created_at, updated_at
                 Relation N-1 avec User (auteur)
                 Relation N-1 avec Category
   - Tag      : id, name
                 Relation N-N avec Post (via table post_tags)
   - Comment  : id, content, created_at
                 Relation N-1 avec Post
                 Relation N-1 avec User

 SCRIPT DE TEST :
   - Créer 2 users, 3 catégories, 5 tags
   - Créer 3 posts avec auteurs et catégories différents
   - Ajouter 2-3 tags par post
   - Ajouter des commentaires
   - Afficher "Posts de [user] : titre1, titre2..."
=============================================================================
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    create_engine, String, Text, ForeignKey, DateTime,
    Table, Column, Integer, func
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column,
    relationship, Session
)

class Base(DeclarativeBase):
    pass

# ============================================================================
# TABLE D'ASSOCIATION Post ↔ Tag
# ============================================================================

# TODO : Créer la table d'association post_tags
# post_tags = Table(
#     "post_tags", Base.metadata,
#     Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
#     Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
# )

# ============================================================================
# MODÈLE User
# ============================================================================

# TODO : class User(Base):
#     __tablename__ = "users"
#     id, username, email, bio (Optional)
#     posts: relation 1-N
#     comments: relation 1-N

# ============================================================================
# MODÈLE Category
# ============================================================================

# TODO : class Category(Base):
#     __tablename__ = "categories"
#     id, name, slug, description
#     posts: relation 1-N

# ============================================================================
# MODÈLE Post
# ============================================================================

# TODO : class Post(Base):
#     __tablename__ = "posts"
#     id, title, slug, content, is_published, created_at, updated_at
#     author_id → ForeignKey("users.id")
#     category_id → ForeignKey("categories.id")
#     author: relation N-1 avec User
#     category: relation N-1 avec Category
#     tags: relation N-N avec Tag (secondary=post_tags)
#     comments: relation 1-N avec Comment (cascade)

# ============================================================================
# MODÈLE Tag
# ============================================================================

# TODO : class Tag(Base):
#     __tablename__ = "tags"
#     id, name
#     posts: relation N-N (secondary=post_tags)

# ============================================================================
# MODÈLE Comment
# ============================================================================

# TODO : class Comment(Base):
#     __tablename__ = "comments"
#     id, content, created_at
#     post_id → ForeignKey("posts.id")
#     user_id → ForeignKey("users.id")
#     post: relation N-1
#     user: relation N-1

# ============================================================================
# TEST (décommenter quand les modèles sont prêts)
# ============================================================================

# engine = create_engine("sqlite:///:memory:", echo=False)
# Base.metadata.create_all(engine)
#
# with Session(engine) as session:
#     # Créer users, catégories, tags
#     # Créer posts avec relations
#     # Ajouter commentaires
#     # Afficher les résultats
#     pass
