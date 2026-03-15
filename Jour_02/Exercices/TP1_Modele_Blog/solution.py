"""
=============================================================================
 TP 1 JOUR 2 - SOLUTION : Modèle de données Blog
 Formation SQLAlchemy 2.0 - Jour 2
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
    relationship, Session, selectinload
)

class Base(DeclarativeBase):
    pass

# ============================================================================
# TABLE D'ASSOCIATION Post ↔ Tag (relation N-N)
# ============================================================================

post_tags = Table(
    "post_tags", Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

# ============================================================================
# MODÈLE User
# ============================================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    bio: Mapped[Optional[str]] = mapped_column(Text)

    # Relations 1-N
    posts: Mapped[List["Post"]] = relationship(back_populates="author")
    comments: Mapped[List["Comment"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"

# ============================================================================
# MODÈLE Category
# ============================================================================

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Relation 1-N
    posts: Mapped[List["Post"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"Category(id={self.id}, name={self.name!r})"

# ============================================================================
# MODÈLE Post
# ============================================================================

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(250), unique=True)
    content: Mapped[str] = mapped_column(Text)
    is_published: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    # Clés étrangères
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    # Relations N-1
    author: Mapped["User"] = relationship(back_populates="posts")
    category: Mapped["Category"] = relationship(back_populates="posts")

    # Relation N-N avec Tag
    tags: Mapped[List["Tag"]] = relationship(
        secondary=post_tags, back_populates="posts"
    )

    # Relation 1-N avec Comment (cascade : supprimer les commentaires avec le post)
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Post(id={self.id}, title={self.title!r})"

# ============================================================================
# MODÈLE Tag
# ============================================================================

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    # Relation N-N inverse
    posts: Mapped[List["Post"]] = relationship(
        secondary=post_tags, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"Tag({self.name!r})"

# ============================================================================
# MODÈLE Comment
# ============================================================================

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Clés étrangères
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relations N-1
    post: Mapped["Post"] = relationship(back_populates="comments")
    user: Mapped["User"] = relationship(back_populates="comments")

    def __repr__(self) -> str:
        return f"Comment(id={self.id}, content={self.content[:30]!r}...)"

# ============================================================================
# SCRIPT DE TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" TP 1 JOUR 2 - SOLUTION : Modèle Blog")
    print("=" * 60)

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    print("\n  ✓ Tables créées")

    with Session(engine) as session:
        # --- 1. Créer 2 users ---
        alice = User(username="alice", email="alice@blog.com", bio="Dev Python")
        bob = User(username="bob", email="bob@blog.com", bio="DevOps Engineer")
        session.add_all([alice, bob])

        # --- 2. Créer 3 catégories ---
        tech = Category(name="Technologie", slug="technologie", description="Articles tech")
        tuto = Category(name="Tutoriels", slug="tutoriels", description="Guides pratiques")
        actu = Category(name="Actualités", slug="actualites", description="News")
        session.add_all([tech, tuto, actu])

        # --- 3. Créer 5 tags ---
        tags = [Tag(name=n) for n in ["Python", "Web", "Docker", "API", "Data"]]
        session.add_all(tags)
        session.commit()

        # --- 4. Créer 3 posts ---
        post1 = Post(
            title="Guide FastAPI", slug="guide-fastapi",
            content="Apprenez FastAPI étape par étape...",
            author=alice, category=tuto, is_published=True,
            tags=[tags[0], tags[1], tags[3]]  # Python, Web, API
        )
        post2 = Post(
            title="Docker en production", slug="docker-production",
            content="Déployer avec Docker et Docker Compose...",
            author=bob, category=tech, is_published=True,
            tags=[tags[2], tags[1]]  # Docker, Web
        )
        post3 = Post(
            title="Pandas pour l'analyse", slug="pandas-analyse",
            content="Analyser vos données avec Pandas...",
            author=alice, category=tuto, is_published=False,
            tags=[tags[0], tags[4]]  # Python, Data
        )
        session.add_all([post1, post2, post3])

        # --- 5. Ajouter des commentaires ---
        comments = [
            Comment(content="Super article, merci !", post=post1, user=bob),
            Comment(content="Très bien expliqué", post=post1, user=bob),
            Comment(content="J'attends la suite !", post=post2, user=alice),
        ]
        session.add_all(comments)
        session.commit()

        print("  ✓ Données de test insérées")

        # --- 6. Afficher les résultats ---
        print("\n  --- Posts par utilisateur ---")
        from sqlalchemy import select

        stmt = select(User).options(
            selectinload(User.posts).selectinload(Post.tags),
            selectinload(User.posts).selectinload(Post.comments),
        )
        users = session.execute(stmt).scalars().all()

        for user in users:
            post_titles = [p.title for p in user.posts]
            print(f"\n  Posts de {user.username} : {', '.join(post_titles)}")
            for post in user.posts:
                tag_names = [t.name for t in post.tags]
                print(f"    📄 '{post.title}'")
                print(f"       Catégorie : {post.category.name}")
                print(f"       Tags      : {', '.join(tag_names)}")
                print(f"       Commentaires : {len(post.comments)}")

    print("\n" + "=" * 60)
    print(" TP 1 JOUR 2 TERMINÉ avec succès !")
    print("=" * 60)
