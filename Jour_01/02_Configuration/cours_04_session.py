"""
=============================================================================
 COURS 04 - LA SESSION (Unité de travail)
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Ce qu'est une Session (pattern "Unit of Work")
 - Comment créer une factory de sessions avec sessionmaker
 - L'utilisation basique (try/except/finally)
 - La meilleure pratique : le context manager (with)

 Pour exécuter :
   python cours_04_session.py
=============================================================================
"""

from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import sessionmaker, Session

# ============================================================================
# 1. QU'EST-CE QU'UNE SESSION ?
# ============================================================================
#
# La Session est comme un PANIER D'ACHATS :
#   1. Vous ajoutez des articles au panier (session.add)
#   2. Vous modifiez des quantités (modifier des objets)
#   3. Vous supprimez des articles (session.delete)
#   4. Vous VALIDEZ la commande (session.commit) → les changements sont sauvés
#   5. OU vous ANNULEZ (session.rollback) → tout est annulé
#
# C'est le pattern "Unit of Work" (Unité de travail) :
#   → La session accumule les modifications
#   → Elle les envoie TOUTES en une fois à la base de données au commit
#   → Si une erreur survient, on peut tout annuler (rollback)

# ============================================================================
# PRÉPARATION : Créer un modèle et un engine pour les démos
# ============================================================================

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r})"

# Créer le moteur de connexion
engine = create_engine("sqlite:///:memory:", echo=False)

# Créer les tables
Base.metadata.create_all(engine)

# ============================================================================
# 2. CRÉER UNE FACTORY DE SESSIONS (sessionmaker)
# ============================================================================

# sessionmaker crée une "fabrique" de sessions
# C'est une fonction qui crée des sessions pré-configurées
SessionLocal = sessionmaker(
    bind=engine,           # Lier au moteur de connexion
    autocommit=False,      # NE PAS valider automatiquement (on veut contrôler)
    autoflush=False,       # NE PAS envoyer les requêtes automatiquement
)

# Pourquoi "SessionLocal" ?
# → C'est une convention de nommage (surtout avec FastAPI)
# → "Local" car chaque requête HTTP aura sa propre session

# ============================================================================
# 3. UTILISATION BASIQUE (try/except/finally)
# ============================================================================

def demo_basique():
    """Utilisation basique de la session avec gestion d'erreurs"""

    print("=== UTILISATION BASIQUE (try/except/finally) ===\n")

    # Créer une nouvelle session
    session = SessionLocal()

    try:
        # ÉTAPE 1 : Créer un objet User
        user = User(name="Alice", email="alice@example.com")

        # ÉTAPE 2 : Ajouter à la session (pas encore en BDD !)
        session.add(user)
        print(f"  Après add()   → user.id = {user.id}")  # None ! Pas encore sauvé

        # ÉTAPE 3 : Valider (sauvegarder en BDD)
        session.commit()
        print(f"  Après commit() → user.id = {user.id}")  # Maintenant on a un ID !

        # ÉTAPE 4 : Recharger depuis la BDD (pour avoir les valeurs auto-générées)
        session.refresh(user)
        print(f"  Après refresh() → {user}")

    except Exception as e:
        # En cas d'erreur, ANNULER tous les changements
        session.rollback()
        print(f"  ERREUR : {e}")
        raise  # Relancer l'exception

    finally:
        # TOUJOURS fermer la session (libérer la connexion)
        session.close()
        print("  Session fermée ✓")


# ============================================================================
# 4. MEILLEURE PRATIQUE : CONTEXT MANAGER (with)
# ============================================================================

def demo_context_manager():
    """Utilisation avec 'with' - la session se ferme automatiquement"""

    print("\n=== MEILLEURE PRATIQUE (context manager) ===\n")

    # Le 'with' ferme automatiquement la session à la fin du bloc
    # Plus besoin de try/finally !
    with SessionLocal() as session:
        # Créer un utilisateur
        user = User(name="Bob", email="bob@example.com")
        session.add(user)
        session.commit()
        session.refresh(user)

        print(f"  Créé : {user}")

        # Lire tous les utilisateurs
        users = session.query(User).all()
        print(f"  Tous les users : {users}")

    # La session est automatiquement fermée ici !
    print("  Session fermée automatiquement ✓")


# ============================================================================
# 5. CYCLE DE VIE D'UN OBJET DANS LA SESSION
# ============================================================================

def demo_cycle_de_vie():
    """Les différents états d'un objet dans la session"""

    print("\n=== CYCLE DE VIE D'UN OBJET ===\n")

    # Un objet passe par ces états :
    #
    # 1. TRANSIENT  : objet créé mais pas dans la session
    # 2. PENDING    : ajouté à la session, pas encore sauvé (add)
    # 3. PERSISTENT : sauvé en base de données (commit)
    # 4. DETACHED   : la session est fermée, l'objet est "détaché"

    from sqlalchemy import inspect

    with SessionLocal() as session:
        # 1. TRANSIENT : objet créé, pas dans la session
        user = User(name="Charlie", email="charlie@example.com")
        state = inspect(user)
        print(f"  1. Après création     → transient={state.transient}")

        # 2. PENDING : ajouté à la session
        session.add(user)
        state = inspect(user)
        print(f"  2. Après add()       → pending={state.pending}")

        # 3. PERSISTENT : sauvé en BDD
        session.commit()
        state = inspect(user)
        print(f"  3. Après commit()    → persistent={state.persistent}")

    # 4. DETACHED : session fermée
    state = inspect(user)
    print(f"  4. Après fermeture   → detached={state.detached}")


# ============================================================================
# 6. ERREURS COURANTES
# ============================================================================

def demo_erreurs_courantes():
    """Les erreurs à éviter avec les sessions"""

    print("\n=== ERREURS COURANTES ===\n")

    print("  1. OUBLIER LE COMMIT")
    print("     → Les données ne sont PAS sauvées en base")
    print("     → Toujours appeler session.commit() !")
    print()
    print("  2. NE PAS FERMER LA SESSION")
    print("     → Fuite de connexions → le pool se vide")
    print("     → Utilisez 'with' pour fermer automatiquement")
    print()
    print("  3. MODIFIER UN OBJET DÉTACHÉ")
    print("     → Un objet hors session n'est plus suivi")
    print("     → Ré-attachez avec session.merge(objet)")
    print()
    print("  4. UTILISER UNE SESSION POUR TOUT")
    print("     → Une session par requête HTTP (FastAPI)")
    print("     → Ne partagez pas une session entre threads")


# ============================================================================
# 7. EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : La Session (Unité de travail)")
    print("=" * 60)

    demo_basique()
    demo_context_manager()
    demo_cycle_de_vie()
    demo_erreurs_courantes()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 04")
    print("=" * 60)
