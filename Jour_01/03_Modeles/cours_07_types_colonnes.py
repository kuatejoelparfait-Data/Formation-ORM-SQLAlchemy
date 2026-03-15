"""
=============================================================================
 COURS 07 - TYPES DE COLONNES
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Tous les types de colonnes courants
 - La correspondance Python ↔ SQLAlchemy ↔ SQL
 - Des exemples pratiques pour chaque type

 Pour exécuter :
   python cours_07_types_colonnes.py
=============================================================================
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    create_engine, String, Text, Integer, Boolean,
    Float, Numeric, DateTime, Date, JSON, func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ============================================================================
# TABLEAU DE RÉFÉRENCE DES TYPES
# ============================================================================
#
# ┌───────────────┬─────────────────┬───────────────────┬──────────────────────┐
# │ Type Python   │ Type SQLAlchemy │ Type SQL (Postgres)│ Utilisation          │
# ├───────────────┼─────────────────┼───────────────────┼──────────────────────┤
# │ int           │ Integer         │ INTEGER           │ IDs, compteurs       │
# │ str           │ String(n)       │ VARCHAR(n)        │ Noms, emails (limité)│
# │ str           │ Text            │ TEXT              │ Descriptions longues │
# │ bool          │ Boolean         │ BOOLEAN           │ Flags, statuts       │
# │ float         │ Float           │ FLOAT             │ Mesures approx.      │
# │ Decimal       │ Numeric(p, s)   │ NUMERIC(p, s)     │ Prix, montants       │
# │ datetime      │ DateTime        │ TIMESTAMP         │ Dates + heures       │
# │ date          │ Date            │ DATE              │ Dates sans heures    │
# │ dict          │ JSON            │ JSONB             │ Données flexibles    │
# └───────────────┴─────────────────┴───────────────────┴──────────────────────┘

class Base(DeclarativeBase):
    pass

# ============================================================================
# MODÈLE COMPLET AVEC TOUS LES TYPES
# ============================================================================

class Product(Base):
    """
    Modèle Product qui illustre TOUS les types de colonnes courants.
    """
    __tablename__ = "products"

    # ---- INTEGER : nombres entiers ----
    # Utilisé pour : identifiants, compteurs, quantités
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock: Mapped[int] = mapped_column(Integer, default=0)

    # ---- STRING(n) : texte court avec limite ----
    # Utilisé pour : noms, emails, codes
    # Le nombre entre parenthèses = longueur MAXIMALE
    name: Mapped[str] = mapped_column(String(200))         # Max 200 caractères
    sku: Mapped[str] = mapped_column(String(50), unique=True)  # Code unique

    # ---- TEXT : texte long sans limite ----
    # Utilisé pour : descriptions, contenus, commentaires
    description: Mapped[Optional[str]] = mapped_column(Text)

    # ---- BOOLEAN : vrai ou faux ----
    # Utilisé pour : statuts, flags activé/désactivé
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    # ---- FLOAT : nombres décimaux (approximatifs) ----
    # Utilisé pour : mesures, poids, dimensions
    # ATTENTION : imprécis pour les calculs financiers !
    weight: Mapped[Optional[float]] = mapped_column(Float)

    # ---- NUMERIC(precision, scale) : nombres décimaux PRÉCIS ----
    # Utilisé pour : prix, montants, pourcentages
    # precision = nombre total de chiffres
    # scale = nombre de chiffres après la virgule
    # Numeric(10, 2) = max 99999999.99
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # ---- DATETIME : date ET heure ----
    # Utilisé pour : timestamps, moments précis
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # ---- DATE : date sans heure ----
    # Utilisé pour : dates de naissance, dates d'expiration
    release_date: Mapped[Optional[date]] = mapped_column(Date)

    # ---- JSON : données semi-structurées ----
    # Utilisé pour : métadonnées, configurations, données flexibles
    # Stocke un dict Python directement en BDD !
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"Product(id={self.id}, name={self.name!r}, price={self.price})"


# ============================================================================
# DÉMONSTRATION
# ============================================================================

def demo():
    """Créer des produits avec différents types de colonnes"""

    print("=== DÉMONSTRATION : Types de colonnes ===\n")

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Créer un produit avec TOUS les types
        produit = Product(
            name="MacBook Pro 16 pouces",         # String(200)
            sku="MBP-16-2024",                     # String(50), unique
            description="Ordinateur portable Apple avec puce M3 Pro",  # Text
            is_available=True,                     # Boolean
            weight=2.14,                           # Float (kg)
            price=Decimal("2999.99"),              # Numeric(10,2) - PRÉCIS !
            release_date=date(2024, 1, 15),        # Date
            metadata_json={                        # JSON - dict Python !
                "couleur": "Noir sidéral",
                "ram": "36 Go",
                "stockage": "1 To SSD",
                "tags": ["apple", "laptop", "pro"]
            }
        )

        session.add(produit)
        session.commit()
        session.refresh(produit)

        # Afficher chaque type
        print(f"  id (Integer)        = {produit.id}")
        print(f"  name (String)       = {produit.name}")
        print(f"  sku (String unique) = {produit.sku}")
        print(f"  description (Text)  = {produit.description}")
        print(f"  is_available (Bool) = {produit.is_available}")
        print(f"  weight (Float)      = {produit.weight}")
        print(f"  price (Numeric)     = {produit.price}")
        print(f"  created_at (DTime)  = {produit.created_at}")
        print(f"  release_date (Date) = {produit.release_date}")
        print(f"  metadata (JSON)     = {produit.metadata_json}")

        # Accéder aux données JSON comme un dict Python
        print(f"\n  Couleur (JSON)      = {produit.metadata_json['couleur']}")
        print(f"  RAM (JSON)          = {produit.metadata_json['ram']}")

    # CONSEIL IMPORTANT SUR FLOAT vs NUMERIC
    print("\n=== FLOAT vs NUMERIC ===")
    print(f"  Float  : 0.1 + 0.2 = {0.1 + 0.2}")  # 0.30000000000000004 !
    print(f"  Decimal: 0.1 + 0.2 = {Decimal('0.1') + Decimal('0.2')}")  # 0.3
    print("  → Utilisez TOUJOURS Numeric pour les PRIX et MONTANTS !")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Types de colonnes SQLAlchemy")
    print("=" * 60)

    demo()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 07")
    print("=" * 60)
