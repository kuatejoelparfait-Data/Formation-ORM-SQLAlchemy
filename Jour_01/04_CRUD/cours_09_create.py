"""
=============================================================================
 COURS 09 - CREATE (Insertion de données)
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Comment insérer UN objet (session.add)
 - Comment insérer PLUSIEURS objets (session.add_all)
 - Le rôle de commit() et refresh()
 - Comment récupérer l'ID auto-généré

 Pour exécuter :
   python cours_09_create.py
=============================================================================
"""

from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ============================================================================
# PRÉPARATION : Modèle et base de données
# ============================================================================

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r}, email={self.email!r})"

# Créer le moteur et les tables
engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

# ============================================================================
# 1. INSERTION D'UN SEUL OBJET
# ============================================================================

def demo_insert_un():
    """Insérer un seul utilisateur dans la base"""

    print("=== 1. INSERTION D'UN SEUL OBJET ===\n")

    with Session(engine) as session:
        # ÉTAPE 1 : Créer l'objet Python
        # À ce stade, l'objet n'est PAS encore en base de données
        user = User(name="Alice", email="alice@example.com")
        print(f"  Avant add()    → id = {user.id}")  # None !

        # ÉTAPE 2 : Ajouter à la session
        # L'objet est "marqué" pour être inséré, mais pas encore en BDD
        session.add(user)
        print(f"  Après add()    → id = {user.id}")  # Toujours None

        # ÉTAPE 3 : Valider la transaction (sauvegarder en BDD)
        # C'est ici que le SQL INSERT est envoyé à la base
        session.commit()
        print(f"  Après commit() → id = {user.id}")  # ID auto-généré !

        # ÉTAPE 4 : Recharger depuis la BDD
        # Pour obtenir les valeurs générées par la BDD (comme server_default)
        session.refresh(user)
        print(f"  Après refresh() → {user}")


# ============================================================================
# 2. INSERTION DE PLUSIEURS OBJETS
# ============================================================================

def demo_insert_plusieurs():
    """Insérer plusieurs utilisateurs en une seule transaction"""

    print("\n=== 2. INSERTION DE PLUSIEURS OBJETS ===\n")

    with Session(engine) as session:
        # Créer une liste d'objets
        users = [
            User(name="Bob", email="bob@example.com"),
            User(name="Charlie", email="charlie@example.com"),
            User(name="Diana", email="diana@example.com"),
        ]

        # session.add_all() : ajouter plusieurs objets à la fois
        # Plus efficace que d'appeler add() en boucle
        session.add_all(users)

        # Un seul commit pour tous les objets
        # → C'est UNE SEULE TRANSACTION
        # → Si une insertion échoue, TOUT est annulé (rollback)
        session.commit()

        # Recharger chaque utilisateur pour avoir les IDs
        for user in users:
            session.refresh(user)
            print(f"  Créé : {user}")


# ============================================================================
# 3. PATTERN : FONCTION create_user
# ============================================================================

def create_user(session: Session, name: str, email: str) -> User:
    """
    Fonction réutilisable pour créer un utilisateur.

    Paramètres :
        session : la session SQLAlchemy active
        name    : le nom de l'utilisateur
        email   : l'email (doit être unique)

    Retourne :
        L'objet User créé avec son ID
    """
    # Créer l'objet
    user = User(name=name, email=email)

    # Ajouter à la session
    session.add(user)

    # Sauvegarder en BDD
    session.commit()

    # Recharger pour avoir l'ID et les valeurs auto-générées
    session.refresh(user)

    # Retourner l'objet créé
    return user


def demo_fonction_create():
    """Utiliser la fonction create_user"""

    print("\n=== 3. FONCTION create_user ===\n")

    with Session(engine) as session:
        # Utiliser la fonction
        user = create_user(session, "Eve", "eve@example.com")
        print(f"  Créé via fonction : {user}")


# ============================================================================
# 4. INSERTION EN MASSE (BULK)
# ============================================================================

def demo_bulk_insert():
    """Insertion en masse pour de gros volumes de données"""

    print("\n=== 4. INSERTION EN MASSE (BULK) ===\n")

    with Session(engine) as session:
        # Préparer les données
        users_data = [
            {"name": f"User_{i}", "email": f"user_{i}@example.com"}
            for i in range(1, 6)  # 5 utilisateurs
        ]

        # Créer les objets à partir des dictionnaires
        users = [User(**data) for data in users_data]

        # ** est l'opérateur de déballage de dictionnaire
        # User(**{"name": "User_1", "email": "..."})
        # équivaut à User(name="User_1", email="...")

        session.add_all(users)
        session.commit()

        # Compter le total
        total = session.query(User).count()
        print(f"  {len(users)} utilisateurs ajoutés en masse")
        print(f"  Total en base : {total} utilisateurs")


# ============================================================================
# 5. GESTION DES ERREURS (DOUBLONS)
# ============================================================================

def demo_erreur_doublon():
    """Que se passe-t-il si on insère un doublon ?"""

    print("\n=== 5. GESTION DES ERREURS ===\n")

    with Session(engine) as session:
        try:
            # Tenter de créer un user avec un email déjà existant
            doublon = User(name="Alice 2", email="alice@example.com")
            session.add(doublon)
            session.commit()
        except Exception as e:
            # ROLLBACK : annuler la transaction échouée
            session.rollback()
            print(f"  ✓ Erreur détectée (email en doublon)")
            print(f"    → {type(e).__name__}")
            print("    → La transaction a été annulée (rollback)")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : CREATE (Insertion de données)")
    print("=" * 60)

    demo_insert_un()
    demo_insert_plusieurs()
    demo_fonction_create()
    demo_bulk_insert()
    demo_erreur_doublon()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 09")
    print("=" * 60)
