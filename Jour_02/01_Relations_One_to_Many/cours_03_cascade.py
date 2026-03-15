"""
=============================================================================
 COURS 03 - OPTIONS DE CASCADE
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique les options de cascade :
 - save-update : persister les objets liés automatiquement
 - delete : supprimer les enfants si le parent est supprimé
 - delete-orphan : supprimer les orphelins (détachés du parent)
 - all : raccourci pour save-update + merge + delete
 - "all, delete-orphan" : cascade complète (recommandé)

 Pour exécuter :
   python cours_03_cascade.py
=============================================================================
"""

from typing import List
from sqlalchemy import create_engine, String, Text, ForeignKey, select
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column,
    relationship, Session
)

# ============================================================================
# TABLEAU DES OPTIONS DE CASCADE
# ============================================================================
#
# ┌──────────────────────┬─────────────────────────────────────────────────┐
# │ Option               │ Description                                     │
# ├──────────────────────┼─────────────────────────────────────────────────┤
# │ save-update          │ Quand on ajoute le parent, les enfants sont    │
# │                      │ aussi ajoutés automatiquement (par défaut)     │
# ├──────────────────────┼─────────────────────────────────────────────────┤
# │ delete               │ Quand on SUPPRIME le parent, les enfants       │
# │                      │ sont AUSSI supprimés                           │
# ├──────────────────────┼─────────────────────────────────────────────────┤
# │ delete-orphan        │ Si un enfant est DÉTACHÉ du parent             │
# │                      │ (retiré de la liste), il est supprimé          │
# ├──────────────────────┼─────────────────────────────────────────────────┤
# │ all                  │ Raccourci pour save-update + merge + delete    │
# ├──────────────────────┼─────────────────────────────────────────────────┤
# │ all, delete-orphan   │ CASCADE COMPLÈTE (recommandé pour 1-N fort)    │
# │                      │ = all + delete-orphan                          │
# └──────────────────────┴─────────────────────────────────────────────────┘

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))

    # CASCADE COMPLÈTE : si on supprime le User, ses articles sont supprimés
    # Si on retire un article de la liste, il est aussi supprimé (orphan)
    articles: Mapped[List["Article"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"  # ← La cascade recommandée
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"

class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="articles")

    def __repr__(self) -> str:
        return f"Article(id={self.id}, title={self.title!r})"

# ============================================================================
# DÉMONSTRATIONS
# ============================================================================

def demo_save_update():
    """save-update : les enfants sont sauvés avec le parent"""

    print("=== 1. CASCADE save-update ===\n")

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # On ajoute SEULEMENT le user, mais les articles sont aussi sauvés !
        user = User(
            username="alice",
            articles=[
                Article(title="Article 1"),
                Article(title="Article 2"),
            ]
        )
        session.add(user)  # ← On n'ajoute PAS les articles explicitement
        session.commit()

        # Vérifier que les articles ont été sauvés
        count = session.query(Article).count()
        print(f"  session.add(user) → {count} articles aussi sauvés automatiquement")
        print("  → C'est grâce à cascade='save-update' (inclus dans 'all')")


def demo_delete_cascade():
    """delete : supprimer le parent supprime les enfants"""

    print("\n=== 2. CASCADE delete ===\n")

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(username="alice", articles=[
            Article(title="Article 1"),
            Article(title="Article 2"),
            Article(title="Article 3"),
        ])
        session.add(user)
        session.commit()

        print(f"  Avant suppression : {session.query(Article).count()} articles")

        # Supprimer le USER → ses articles sont AUSSI supprimés
        session.delete(user)
        session.commit()

        count = session.query(Article).count()
        print(f"  Après suppression du user : {count} articles")
        print("  → Les articles ont été supprimés avec le user (cascade delete)")


def demo_delete_orphan():
    """delete-orphan : retirer un enfant du parent le supprime"""

    print("\n=== 3. CASCADE delete-orphan ===\n")

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(username="alice", articles=[
            Article(title="Article 1"),
            Article(title="Article 2"),
            Article(title="Article 3"),
        ])
        session.add(user)
        session.commit()

        print(f"  Avant : {len(user.articles)} articles")

        # Retirer un article de la liste
        article_retire = user.articles[0]
        print(f"  Retrait de : {article_retire.title}")
        user.articles.remove(article_retire)
        session.commit()

        count = session.query(Article).count()
        print(f"  Après retrait : {count} articles en base")
        print("  → L'article orphelin a été SUPPRIMÉ (cascade delete-orphan)")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Options de Cascade")
    print("=" * 60)

    demo_save_update()
    demo_delete_cascade()
    demo_delete_orphan()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 03 (Jour 2)")
    print("=" * 60)
