"""
=============================================================================
 COURS 14 - DÉPENDANCE DE SESSION POUR FASTAPI
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Comment configurer database.py pour FastAPI
 - La dépendance get_db (pattern yield)
 - Comment chaque requête HTTP obtient sa propre session
=============================================================================
"""

# ============================================================================
# 1. FICHIER database.py
# ============================================================================

# Ce code irait dans app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from typing import Generator

# ---- Créer le moteur ----
# En production, DATABASE_URL viendrait des variables d'environnement
DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,          # True en développement pour voir les requêtes SQL
    # connect_args={"check_same_thread": False}  # Nécessaire pour SQLite + FastAPI
)

# ---- Créer la factory de sessions ----
SessionLocal = sessionmaker(
    autocommit=False,     # On gère les commits manuellement
    autoflush=False,      # On gère les flush manuellement
    bind=engine           # Lié à notre moteur
)

# ---- Classe de base pour les modèles ----
class Base(DeclarativeBase):
    pass


# ============================================================================
# 2. DÉPENDANCE get_db
# ============================================================================

# Ce code irait dans app/dependencies.py

def get_db() -> Generator[Session, None, None]:
    """
    Dépendance FastAPI qui fournit une session de base de données.

    Comment ça marche :
    1. FastAPI appelle get_db() au début de chaque requête HTTP
    2. yield db : donne la session au endpoint
    3. Le endpoint utilise la session pour ses opérations
    4. Après le endpoint : le bloc finally ferme la session

    Utilisation dans un endpoint :
        @app.get("/users")
        def list_users(db: Session = Depends(get_db)):
            return db.query(User).all()

    Le 'yield' est la clé :
    - Avant yield : préparation (créer la session)
    - yield : donner la session au endpoint
    - Après yield (finally) : nettoyage (fermer la session)
    """
    db = SessionLocal()   # Créer une nouvelle session
    try:
        yield db          # Donner la session au endpoint
    finally:
        db.close()        # TOUJOURS fermer la session après


# ============================================================================
# 3. EXEMPLE D'UTILISATION DANS UN ENDPOINT
# ============================================================================

EXEMPLE_ENDPOINT = """
=== EXEMPLE D'UTILISATION ===

  # app/routers/users.py
  from fastapi import APIRouter, Depends
  from sqlalchemy.orm import Session
  from app.dependencies import get_db
  from app.models.user import User

  router = APIRouter()

  @router.get("/users")
  def list_users(db: Session = Depends(get_db)):
      '''
      Chaque requête HTTP reçoit SA PROPRE session.
      La session est créée au début et fermée à la fin.
      '''
      users = db.query(User).all()
      return users

  @router.post("/users")
  def create_user(data: UserCreate, db: Session = Depends(get_db)):
      user = User(**data.model_dump())
      db.add(user)
      db.commit()
      db.refresh(user)
      return user

=== FLUX ===

  Requête HTTP arrive
       ↓
  get_db() crée une Session
       ↓
  Session donnée au endpoint via Depends(get_db)
       ↓
  Le endpoint utilise la session
       ↓
  Réponse envoyée au client
       ↓
  finally: db.close() ferme la session
"""

if __name__ == "__main__":
    print("=" * 60)
    print(" COURS : Dépendance de session pour FastAPI")
    print("=" * 60)

    print(EXEMPLE_ENDPOINT)

    print("  💡 Le pattern yield + finally garantit que la session")
    print("     est TOUJOURS fermée, même en cas d'erreur !")

    print("\n" + "=" * 60)
    print(" FIN DU COURS 14 (Jour 2)")
    print("=" * 60)
