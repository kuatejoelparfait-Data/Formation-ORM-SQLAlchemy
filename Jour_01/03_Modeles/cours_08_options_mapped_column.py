"""
=============================================================================
 COURS 08 - OPTIONS DE mapped_column ET ENUMS
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Toutes les options de mapped_column
 - Comment utiliser les Enum Python avec SQLAlchemy
 - CheckConstraint pour les validations côté BDD

 Pour exécuter :
   python cours_08_options_mapped_column.py
=============================================================================
"""

import enum                                  # Module Python pour les énumérations
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    create_engine, String, Integer, Text, Numeric,
    DateTime, CheckConstraint, Enum as SQLEnum, func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):
    pass

# ============================================================================
# 1. LES ENUMS (ÉNUMÉRATIONS)
# ============================================================================

# Un Enum est une liste de valeurs FIXES et prédéfinies
# Exemple : un statut ne peut être que "pending", "confirmed", etc.
# C'est plus sûr qu'un simple String car on ne peut pas mettre n'importe quoi

class OrderStatus(enum.Enum):
    """Statuts possibles d'une commande"""
    PENDING = "pending"          # En attente
    CONFIRMED = "confirmed"      # Confirmée
    SHIPPED = "shipped"          # Expédiée
    DELIVERED = "delivered"      # Livrée
    CANCELLED = "cancelled"      # Annulée


class ProductCategory(enum.Enum):
    """Catégories de produits"""
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FOOD = "food"
    BOOKS = "books"


# ============================================================================
# 2. MODÈLE AVEC TOUTES LES OPTIONS
# ============================================================================

class Product(Base):
    """Modèle Product avec toutes les options de mapped_column"""

    __tablename__ = "products"

    # ---- primary_key : identifiant unique ----
    id: Mapped[int] = mapped_column(primary_key=True)

    # ---- unique + index : unicité et recherche rapide ----
    # unique=True : cette valeur ne peut pas exister en double
    # index=True : la BDD crée un index pour chercher plus vite
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    # ---- Champ obligatoire simple ----
    name: Mapped[str] = mapped_column(String(200))

    # ---- default : valeur par défaut CÔTÉ PYTHON ----
    # Quand on crée Product() sans préciser stock, il vaudra 0
    # C'est Python qui met la valeur AVANT d'envoyer à la BDD
    stock: Mapped[int] = mapped_column(default=0)

    # ---- server_default : valeur par défaut CÔTÉ SERVEUR (BDD) ----
    # C'est la BASE DE DONNÉES qui met la valeur
    # Plus fiable car ça fonctionne même si on insère directement en SQL
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()  # func.now() = NOW() en SQL
    )

    # ---- onupdate : valeur auto-mise à jour à chaque modification ----
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=func.now()  # Automatiquement mis à jour à chaque UPDATE
    )

    # ---- Numeric(precision, scale) : précision pour les montants ----
    # Numeric(10, 2) = 10 chiffres au total, 2 après la virgule
    # → Peut stocker de -99999999.99 à 99999999.99
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # ---- Enum : liste de valeurs prédéfinies ----
    # Le statut ne peut être QUE l'une des valeurs de OrderStatus
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus),           # Type SQLAlchemy Enum
        default=OrderStatus.PENDING     # Valeur par défaut
    )

    # ---- Enum pour la catégorie ----
    category: Mapped[ProductCategory] = mapped_column(
        SQLEnum(ProductCategory),
        default=ProductCategory.ELECTRONICS
    )

    # ---- nullable=True explicite ----
    # Mapped[Optional[str]] rend déjà la colonne nullable
    # Mais on peut le préciser explicitement
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ---- CheckConstraint : validation côté BDD ----
    # La BDD REFUSE les valeurs qui ne respectent pas la contrainte
    rating: Mapped[Optional[float]] = mapped_column()

    # Contraintes au niveau de la table
    __table_args__ = (
        # Le rating doit être entre 0 et 5
        CheckConstraint("rating >= 0 AND rating <= 5", name="check_rating"),
        # Le stock ne peut pas être négatif
        CheckConstraint("stock >= 0", name="check_stock_positive"),
    )

    def __repr__(self) -> str:
        return f"Product(id={self.id}, name={self.name!r}, status={self.status.value})"


# ============================================================================
# 3. DÉMONSTRATION
# ============================================================================

def demo():
    """Démontrer toutes les options de mapped_column"""

    print("=== DÉMONSTRATION : Options de mapped_column ===\n")

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Créer un produit avec valeurs par défaut
        p1 = Product(
            sku="PHONE-001",
            name="Smartphone X",
            price=Decimal("599.99"),
            # stock → default=0 (automatique)
            # status → default=PENDING (automatique)
            # category → default=ELECTRONICS (automatique)
            rating=4.5,
        )

        # Créer un produit avec toutes les valeurs
        p2 = Product(
            sku="BOOK-001",
            name="Python pour les nuls",
            price=Decimal("29.99"),
            stock=100,
            status=OrderStatus.CONFIRMED,
            category=ProductCategory.BOOKS,
            description="Le guide complet pour apprendre Python",
            rating=4.8,
        )

        session.add_all([p1, p2])
        session.commit()
        session.refresh(p1)
        session.refresh(p2)

        # Afficher les résultats
        print(f"  Produit 1 : {p1}")
        print(f"    sku        = {p1.sku}")
        print(f"    stock      = {p1.stock}  (default=0)")
        print(f"    status     = {p1.status}  (default=PENDING)")
        print(f"    category   = {p1.category}  (default=ELECTRONICS)")
        print(f"    rating     = {p1.rating}")
        print(f"    created_at = {p1.created_at}")

        print(f"\n  Produit 2 : {p2}")
        print(f"    status     = {p2.status}  (CONFIRMED)")
        print(f"    category   = {p2.category}  (BOOKS)")
        print(f"    description= {p2.description}")

        # Accéder à la VALEUR d'un enum
        print(f"\n  Valeur du status : {p1.status.value}")  # "pending"
        print(f"  Nom du status   : {p1.status.name}")     # "PENDING"

    # Tester la contrainte Check
    print("\n=== TEST CheckConstraint ===")
    with Session(engine) as session:
        try:
            mauvais = Product(
                sku="BAD-001",
                name="Mauvais produit",
                price=Decimal("10.00"),
                rating=6.0,  # > 5 → viole la contrainte !
            )
            session.add(mauvais)
            session.commit()
            print("  ✗ Pas d'erreur (SQLite ne vérifie pas toujours)")
        except Exception as e:
            session.rollback()
            print(f"  ✓ Erreur attendue : {e}")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Options de mapped_column et Enums")
    print("=" * 60)

    demo()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 08")
    print("=" * 60)
