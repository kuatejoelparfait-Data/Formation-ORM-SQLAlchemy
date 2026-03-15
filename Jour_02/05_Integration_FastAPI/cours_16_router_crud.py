"""
=============================================================================
 COURS 16 - ROUTER FASTAPI AVEC CRUD COMPLET
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier montre un router FastAPI complet avec :
 - POST   /users/      → Créer un utilisateur
 - GET    /users/      → Lister (avec pagination)
 - GET    /users/{id}  → Récupérer un utilisateur
 - PATCH  /users/{id}  → Mise à jour partielle
 - DELETE /users/{id}  → Supprimer

 Pour exécuter :
   pip install fastapi uvicorn sqlalchemy
   python cours_16_router_crud.py
   → Puis ouvrir http://127.0.0.1:8000/docs
=============================================================================
"""

from datetime import datetime
from typing import Optional, List, Generator
from pydantic import BaseModel, ConfigDict

from sqlalchemy import create_engine, String, Text, DateTime, func, select
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column,
    Session, sessionmaker, selectinload
)

# ============================================================================
# 1. BASE DE DONNÉES
# ============================================================================

engine = create_engine("sqlite:///./demo_fastapi.db", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# ============================================================================
# 2. MODÈLE SQLALCHEMY
# ============================================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"

# Créer les tables
Base.metadata.create_all(engine)

# ============================================================================
# 3. SCHÉMAS PYDANTIC
# ============================================================================

class UserCreate(BaseModel):
    """Données pour créer un utilisateur"""
    username: str
    email: str
    bio: str | None = None

class UserUpdate(BaseModel):
    """Données pour mettre à jour (tout optionnel)"""
    username: str | None = None
    email: str | None = None
    bio: str | None = None

class UserResponse(BaseModel):
    """Données retournées par l'API"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    bio: str | None
    is_active: bool
    created_at: datetime

# ============================================================================
# 4. DÉPENDANCE DE SESSION
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """Fournir une session par requête HTTP"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# 5. ROUTER FASTAPI AVEC CRUD COMPLET
# ============================================================================

try:
    from fastapi import FastAPI, APIRouter, Depends, HTTPException, status

    app = FastAPI(title="API Users - Démonstration CRUD")
    router = APIRouter(prefix="/users", tags=["users"])

    # ---- POST /users/ : Créer ----
    @router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
    def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
        """Créer un nouvel utilisateur"""
        # Vérifier si l'email existe déjà
        existing = db.execute(
            select(User).where(User.email == user_data.email)
        ).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé"
            )

        # Créer l'utilisateur
        user = User(**user_data.model_dump())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    # ---- GET /users/ : Lister avec pagination ----
    @router.get("/", response_model=list[UserResponse])
    def list_users(
        skip: int = 0,        # Nombre d'éléments à sauter
        limit: int = 20,      # Nombre max d'éléments à retourner
        db: Session = Depends(get_db)
    ):
        """Lister les utilisateurs avec pagination"""
        stmt = select(User).offset(skip).limit(limit).order_by(User.id)
        users = db.execute(stmt).scalars().all()
        return users

    # ---- GET /users/{id} : Récupérer un ----
    @router.get("/{user_id}", response_model=UserResponse)
    def get_user(user_id: int, db: Session = Depends(get_db)):
        """Récupérer un utilisateur par son ID"""
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        return user

    # ---- PATCH /users/{id} : Mise à jour partielle ----
    @router.patch("/{user_id}", response_model=UserResponse)
    def update_user(
        user_id: int,
        user_data: UserUpdate,
        db: Session = Depends(get_db)
    ):
        """Mise à jour partielle d'un utilisateur"""
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        # model_dump(exclude_unset=True) : ne prend que les champs envoyés
        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return user

    # ---- DELETE /users/{id} : Supprimer ----
    @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_user(user_id: int, db: Session = Depends(get_db)):
        """Supprimer un utilisateur"""
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        db.delete(user)
        db.commit()

    # Enregistrer le router dans l'app
    app.include_router(router)

    print("  ✓ FastAPI configuré avec succès")
    print("  → Lancer avec : uvicorn cours_16_router_crud:app --reload")
    print("  → Ouvrir http://127.0.0.1:8000/docs pour la doc interactive")

except ImportError:
    print("  ⚠️ FastAPI non installé")
    print("  → pip install fastapi uvicorn")
    print("  Ce fichier montre le code d'un router CRUD complet.")

# ============================================================================
# CODES HTTP IMPORTANTS
# ============================================================================

CODES_HTTP = """
=== CODES HTTP COURANTS ===

  200 OK              → Requête réussie (GET, PATCH)
  201 Created         → Ressource créée (POST)
  204 No Content      → Suppression réussie (DELETE)
  400 Bad Request     → Données invalides
  404 Not Found       → Ressource non trouvée
  422 Unprocessable   → Erreur de validation Pydantic
  500 Internal Error  → Erreur serveur
"""

if __name__ == "__main__":
    print("=" * 60)
    print(" COURS : Router FastAPI avec CRUD complet")
    print("=" * 60)
    print(CODES_HTTP)

    try:
        import uvicorn
        print("  Démarrage du serveur FastAPI...")
        print("  → Documentation : http://127.0.0.1:8000/docs")
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except (ImportError, NameError):
        print("  Pour lancer le serveur : pip install fastapi uvicorn")
        print("  Puis : python cours_16_router_crud.py")
