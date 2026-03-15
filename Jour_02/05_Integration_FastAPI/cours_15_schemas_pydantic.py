"""
=============================================================================
 COURS 15 - SCHÉMAS PYDANTIC vs MODÈLES SQLALCHEMY
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - La différence entre Modèle SQLAlchemy et Schéma Pydantic
 - Schéma de création (input)
 - Schéma de réponse (output)
 - Schéma de mise à jour (partial)
 - ConfigDict(from_attributes=True) pour convertir ORM → Pydantic

 Pour exécuter :
   pip install pydantic email-validator
   python cours_15_schemas_pydantic.py
=============================================================================
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

# ============================================================================
# 1. POURQUOI SÉPARER MODÈLES ET SCHÉMAS ?
# ============================================================================
#
# MODÈLE SQLAlchemy (models/) :
#   → Représente la TABLE dans la base de données
#   → Contient TOUTES les colonnes (y compris les sensibles)
#   → Utilisé pour les opérations CRUD
#
# SCHÉMA Pydantic (schemas/) :
#   → Représente les données ENVOYÉES/REÇUES par l'API
#   → Validation automatique des données
#   → On peut EXCLURE des champs sensibles (mot de passe)
#   → Différent pour la création, la réponse, la mise à jour
#
# ANALOGIE :
#   Modèle = le dossier complet d'un patient (tout est dedans)
#   Schéma = le formulaire que le patient remplit (seulement ce qu'il faut)

# ============================================================================
# 2. SCHÉMA DE CRÉATION (Input - ce que le client envoie)
# ============================================================================

class UserCreate(BaseModel):
    """
    Schéma pour CRÉER un utilisateur.
    Le client envoie ces données dans le body de la requête POST.

    Exemple de body JSON :
    {
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret123"
    }
    """
    username: str                    # Obligatoire
    email: str                       # Obligatoire
    password: str                    # Obligatoire (le mot de passe en clair)
    # Note : le mot de passe sera HASHÉ avant d'être stocké en BDD
    # Il n'apparaîtra JAMAIS dans la réponse


# ============================================================================
# 3. SCHÉMA DE MISE À JOUR (Input partiel)
# ============================================================================

class UserUpdate(BaseModel):
    """
    Schéma pour METTRE À JOUR un utilisateur.
    TOUS les champs sont optionnels (mise à jour partielle).

    Exemple : ne mettre à jour que le username
    {
        "username": "alice_new"
    }
    """
    username: str | None = None      # Optionnel
    email: str | None = None         # Optionnel
    bio: str | None = None           # Optionnel
    # Pas de password ici (modification de mot de passe = autre endpoint)


# ============================================================================
# 4. SCHÉMA DE RÉPONSE (Output - ce que l'API retourne)
# ============================================================================

class UserResponse(BaseModel):
    """
    Schéma de RÉPONSE pour un utilisateur.
    C'est ce que l'API retourne au client.

    IMPORTANT : PAS de mot de passe ici !

    model_config = ConfigDict(from_attributes=True)
    → Permet de convertir un objet SQLAlchemy en schéma Pydantic
    → user_response = UserResponse.model_validate(user_orm)
    """
    # ConfigDict(from_attributes=True) permet la conversion ORM → Pydantic
    model_config = ConfigDict(from_attributes=True)

    id: int                          # L'ID généré par la BDD
    username: str
    email: str
    bio: str | None = None           # Peut être None
    created_at: datetime             # Timestamp de création
    # PAS de password, PAS de hashed_password !


# ============================================================================
# 5. SCHÉMA AVEC RELATIONS
# ============================================================================

class ArticleResponse(BaseModel):
    """Schéma de réponse pour un article"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime


class UserWithArticles(UserResponse):
    """
    Schéma de réponse avec les articles de l'utilisateur.
    Hérite de UserResponse et ajoute la liste d'articles.
    """
    articles: list[ArticleResponse] = []


# ============================================================================
# 6. DÉMONSTRATION
# ============================================================================

def demo():
    """Démonstration des schémas Pydantic"""

    print("=== DÉMONSTRATION : Schémas Pydantic ===\n")

    # ---- Schéma de création ----
    print("  1. UserCreate (validation d'entrée) :")
    user_data = UserCreate(
        username="alice",
        email="alice@example.com",
        password="secret123"
    )
    print(f"    {user_data}")
    print(f"    → username={user_data.username}")
    print(f"    → password={user_data.password} (sera hashé avant stockage)")

    # ---- Schéma de mise à jour partielle ----
    print("\n  2. UserUpdate (mise à jour partielle) :")
    update_data = UserUpdate(username="alice_new")  # Seulement le username
    print(f"    {update_data}")

    # model_dump(exclude_unset=True) : ne retourne QUE les champs fournis
    changes = update_data.model_dump(exclude_unset=True)
    print(f"    model_dump(exclude_unset=True) → {changes}")
    # → {'username': 'alice_new'}  (pas de email ni bio car non fournis)

    # ---- Schéma de réponse ----
    print("\n  3. UserResponse (réponse API) :")
    # Simuler un objet ORM
    class FakeUser:
        id = 1
        username = "alice"
        email = "alice@example.com"
        bio = "Dev Python"
        created_at = datetime.now()

    response = UserResponse.model_validate(FakeUser())
    print(f"    {response}")
    print(f"    → Pas de mot de passe dans la réponse !")

    # ---- Validation ----
    print("\n  4. Validation automatique :")
    try:
        # username est obligatoire → erreur si absent
        bad_data = UserCreate(email="test@test.com", password="123")
    except Exception as e:
        print(f"    ✓ Erreur de validation : username manquant")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" COURS : Schémas Pydantic vs Modèles SQLAlchemy")
    print("=" * 60)

    demo()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 15 (Jour 2)")
    print("=" * 60)
