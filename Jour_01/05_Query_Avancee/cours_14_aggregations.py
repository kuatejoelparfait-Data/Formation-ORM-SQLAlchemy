"""
=============================================================================
 COURS 14 - AGRÉGATIONS (COUNT, SUM, AVG, MIN, MAX, GROUP BY)
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Les fonctions d'agrégation : COUNT, SUM, AVG, MIN, MAX
 - GROUP BY (regroupement)
 - HAVING (filtrer les groupes)
 - Le label() pour nommer les résultats

 Pour exécuter :
   python cours_14_aggregations.py
=============================================================================
"""

from decimal import Decimal
from sqlalchemy import create_engine, String, Integer, Numeric, select, func, desc
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ============================================================================
# PRÉPARATION
# ============================================================================

class Base(DeclarativeBase):
    pass

class Order(Base):
    """Modèle Commande pour illustrer les agrégations"""
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str] = mapped_column(String(100))   # Nom du client
    product: Mapped[str] = mapped_column(String(100))     # Nom du produit
    category: Mapped[str] = mapped_column(String(50))     # Catégorie
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Montant
    quantity: Mapped[int] = mapped_column(Integer)         # Quantité

    def __repr__(self) -> str:
        return f"Order(id={self.id}, customer={self.customer!r}, amount={self.amount})"

engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

def preparer_donnees():
    """Insérer des commandes de test"""
    with Session(engine) as session:
        orders = [
            Order(customer="Alice", product="Laptop", category="Tech", amount=Decimal("999.99"), quantity=1),
            Order(customer="Alice", product="Souris", category="Tech", amount=Decimal("29.99"), quantity=2),
            Order(customer="Alice", product="Livre Python", category="Livres", amount=Decimal("35.00"), quantity=1),
            Order(customer="Bob", product="Clavier", category="Tech", amount=Decimal("79.99"), quantity=1),
            Order(customer="Bob", product="Écran", category="Tech", amount=Decimal("299.99"), quantity=1),
            Order(customer="Charlie", product="Livre SQL", category="Livres", amount=Decimal("42.00"), quantity=3),
            Order(customer="Charlie", product="Livre Docker", category="Livres", amount=Decimal("38.00"), quantity=1),
            Order(customer="Diana", product="Casque", category="Tech", amount=Decimal("149.99"), quantity=1),
            Order(customer="Diana", product="Webcam", category="Tech", amount=Decimal("89.99"), quantity=2),
            Order(customer="Diana", product="Livre FastAPI", category="Livres", amount=Decimal("29.00"), quantity=1),
        ]
        session.add_all(orders)
        session.commit()
    print("  ✓ 10 commandes de test insérées\n")

# ============================================================================
# 1. FONCTIONS D'AGRÉGATION SIMPLES
# ============================================================================

def demo_agregations_simples():
    """COUNT, SUM, AVG, MIN, MAX"""

    print("=== 1. FONCTIONS D'AGRÉGATION ===\n")

    with Session(engine) as session:
        # ---- COUNT : compter ----
        total = session.execute(select(func.count(Order.id))).scalar_one()
        print(f"  COUNT  → Nombre de commandes : {total}")

        # ---- SUM : additionner ----
        total_amount = session.execute(select(func.sum(Order.amount))).scalar_one()
        print(f"  SUM    → Chiffre d'affaires total : {total_amount} €")

        # ---- AVG : moyenne ----
        avg_amount = session.execute(select(func.avg(Order.amount))).scalar_one()
        print(f"  AVG    → Montant moyen : {avg_amount:.2f} €")

        # ---- MIN : valeur minimale ----
        min_amount = session.execute(select(func.min(Order.amount))).scalar_one()
        print(f"  MIN    → Plus petite commande : {min_amount} €")

        # ---- MAX : valeur maximale ----
        max_amount = session.execute(select(func.max(Order.amount))).scalar_one()
        print(f"  MAX    → Plus grosse commande : {max_amount} €")

        # ---- Plusieurs agrégations en une requête ----
        print("\n  Toutes les stats en une requête :")
        stmt = select(
            func.count(Order.id).label("total_orders"),       # Nommer avec .label()
            func.sum(Order.amount).label("total_revenue"),
            func.avg(Order.amount).label("avg_order"),
            func.min(Order.amount).label("min_order"),
            func.max(Order.amount).label("max_order"),
        )
        stats = session.execute(stmt).one()
        # On accède aux résultats par le nom du label
        print(f"    Commandes : {stats.total_orders}")
        print(f"    CA total  : {stats.total_revenue} €")
        print(f"    Moyenne   : {float(stats.avg_order):.2f} €")
        print(f"    Min       : {stats.min_order} €")
        print(f"    Max       : {stats.max_order} €")


# ============================================================================
# 2. GROUP BY (REGROUPEMENT)
# ============================================================================

def demo_group_by():
    """Regrouper les résultats par catégorie, client, etc."""

    print("\n=== 2. GROUP BY (Regroupement) ===\n")

    with Session(engine) as session:
        # ---- Commandes par CLIENT ----
        print("  Commandes par client :")
        stmt = (
            select(
                Order.customer,                              # Le client
                func.count(Order.id).label("nb_commandes"),  # Nombre de commandes
                func.sum(Order.amount).label("total"),       # Total dépensé
            )
            .group_by(Order.customer)                        # Regrouper par client
            .order_by(desc("total"))                         # Trier par total décroissant
        )
        results = session.execute(stmt).all()
        for row in results:
            print(f"    {row.customer:10} → {row.nb_commandes} commandes, {row.total} €")

        # ---- Commandes par CATÉGORIE ----
        print("\n  Commandes par catégorie :")
        stmt = (
            select(
                Order.category,
                func.count(Order.id).label("nb_commandes"),
                func.sum(Order.amount).label("total"),
                func.avg(Order.amount).label("moyenne"),
            )
            .group_by(Order.category)
            .order_by(desc("total"))
        )
        results = session.execute(stmt).all()
        for row in results:
            print(f"    {row.category:10} → {row.nb_commandes} cmd, total={row.total} €, moy={float(row.moyenne):.2f} €")


# ============================================================================
# 3. HAVING (FILTRER LES GROUPES)
# ============================================================================

def demo_having():
    """HAVING = WHERE mais pour les groupes"""

    print("\n=== 3. HAVING (Filtrer les groupes) ===\n")

    with Session(engine) as session:
        # Clients qui ont dépensé plus de 100€ au total
        print("  Clients avec plus de 100€ de dépenses :")
        stmt = (
            select(
                Order.customer,
                func.sum(Order.amount).label("total"),
            )
            .group_by(Order.customer)
            .having(func.sum(Order.amount) > 100)  # HAVING = filtre sur les groupes
            .order_by(desc("total"))
        )
        results = session.execute(stmt).all()
        for row in results:
            print(f"    {row.customer:10} → {row.total} €")

        # Clients avec plus de 2 commandes
        print("\n  Clients avec plus de 2 commandes :")
        stmt = (
            select(
                Order.customer,
                func.count(Order.id).label("nb"),
            )
            .group_by(Order.customer)
            .having(func.count(Order.id) > 2)
        )
        results = session.execute(stmt).all()
        for row in results:
            print(f"    {row.customer:10} → {row.nb} commandes")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Agrégations (COUNT, SUM, AVG, GROUP BY)")
    print("=" * 60)

    preparer_donnees()
    demo_agregations_simples()
    demo_group_by()
    demo_having()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 14")
    print("=" * 60)
