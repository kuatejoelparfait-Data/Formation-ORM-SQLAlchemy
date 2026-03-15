"""
=============================================================================
 COURS 17 - GESTION DES TRANSACTIONS
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Les transactions (commit/rollback)
 - Le context manager pour les transactions
 - Le pattern get_db pour FastAPI
 - Les erreurs courantes à éviter

 Pour exécuter :
   python cours_17_gestion_transactions.py
=============================================================================
"""

from contextlib import contextmanager
from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, sessionmaker

# ============================================================================
# 1. QU'EST-CE QU'UNE TRANSACTION ?
# ============================================================================
#
# Une transaction est un GROUPE D'OPÉRATIONS qui doit réussir EN TOTALITÉ
# ou échouer EN TOTALITÉ. Il n'y a pas de "milieu".
#
# Exemple concret : un virement bancaire
#   1. Débiter 100€ du compte A
#   2. Créditer 100€ sur le compte B
#
# Si l'étape 2 échoue après l'étape 1, on doit ANNULER l'étape 1.
# Sinon, 100€ disparaissent ! C'est le rôle du ROLLBACK.
#
# COMMIT   = tout a réussi, on SAUVEGARDE
# ROLLBACK = quelque chose a échoué, on ANNULE tout

# ============================================================================
# PRÉPARATION
# ============================================================================

class Base(DeclarativeBase):
    pass

class Account(Base):
    """Compte bancaire simplifié"""
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    balance: Mapped[float] = mapped_column(default=0.0)

    def __repr__(self) -> str:
        return f"Account({self.name!r}, solde={self.balance:.2f}€)"

engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# ============================================================================
# 2. TRANSACTION MANUELLE (try/except/finally)
# ============================================================================

def demo_transaction_manuelle():
    """Gestion manuelle des transactions"""

    print("=== 2. TRANSACTION MANUELLE ===\n")

    with SessionLocal() as session:
        # Créer deux comptes
        compte_a = Account(name="Alice", balance=1000.0)
        compte_b = Account(name="Bob", balance=500.0)
        session.add_all([compte_a, compte_b])
        session.commit()

        print(f"  Avant virement : {compte_a}, {compte_b}")

    # Virement réussi
    with SessionLocal() as session:
        try:
            # Récupérer les comptes
            alice = session.get(Account, 1)
            bob = session.get(Account, 2)

            montant = 200.0

            # Débiter Alice
            alice.balance -= montant

            # Créditer Bob
            bob.balance += montant

            # Tout a réussi → COMMIT
            session.commit()
            session.refresh(alice)
            session.refresh(bob)
            print(f"  Après virement (+{montant}€) : {alice}, {bob}")

        except Exception as e:
            # Quelque chose a échoué → ROLLBACK
            session.rollback()
            print(f"  ERREUR → Rollback : {e}")


# ============================================================================
# 3. CONTEXT MANAGER POUR LES TRANSACTIONS
# ============================================================================

@contextmanager
def transaction(session_factory):
    """
    Context manager réutilisable pour les transactions.

    Utilisation :
        with transaction(SessionLocal) as session:
            # Faire des opérations
            session.add(...)
            # Commit automatique si pas d'exception
            # Rollback automatique en cas d'erreur
    """
    session = session_factory()
    try:
        yield session              # Donner la session au code appelant
        session.commit()           # Commit automatique si tout va bien
    except Exception:
        session.rollback()         # Rollback automatique en cas d'erreur
        raise                      # Relancer l'exception
    finally:
        session.close()            # Toujours fermer la session


def demo_context_manager():
    """Utiliser le context manager de transaction"""

    print("\n=== 3. CONTEXT MANAGER DE TRANSACTION ===\n")

    # Transaction réussie
    with transaction(SessionLocal) as session:
        alice = session.get(Account, 1)
        alice.balance += 100.0
        # Commit automatique à la fin du bloc !

    with SessionLocal() as session:
        alice = session.get(Account, 1)
        print(f"  Après +100€ (auto-commit) : {alice}")

    # Transaction échouée
    print()
    try:
        with transaction(SessionLocal) as session:
            alice = session.get(Account, 1)
            alice.balance -= 50000.0  # Solde négatif (on simule une erreur)
            if alice.balance < 0:
                raise ValueError("Solde insuffisant !")
            # Le commit n'est PAS atteint car l'exception est levée
    except ValueError as e:
        print(f"  Erreur interceptée : {e}")
        print("  → Transaction annulée automatiquement (rollback)")

    # Vérifier que le solde n'a pas changé
    with SessionLocal() as session:
        alice = session.get(Account, 1)
        print(f"  Solde inchangé après rollback : {alice}")


# ============================================================================
# 4. PATTERN get_db POUR FASTAPI
# ============================================================================

def get_db():
    """
    Dépendance FastAPI pour obtenir une session de base de données.

    En FastAPI, chaque requête HTTP reçoit SA PROPRE session.
    La session est fermée automatiquement après la requête.

    Utilisation dans FastAPI :
        @app.get("/users")
        def list_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db           # La session est donnée au endpoint
        db.commit()        # Commit si tout va bien
    except Exception:
        db.rollback()      # Rollback si erreur
        raise
    finally:
        db.close()         # Toujours fermer


def demo_pattern_fastapi():
    """Simuler le pattern get_db"""

    print("\n=== 4. PATTERN get_db (FastAPI) ===\n")

    print("  En FastAPI, on utilise la dépendance get_db() :")
    print()
    print("    @app.get('/users')")
    print("    def list_users(db: Session = Depends(get_db)):")
    print("        return db.query(User).all()")
    print()
    print("  → Chaque requête HTTP reçoit sa propre session")
    print("  → La session est fermée automatiquement après")
    print("  → Commit auto si succès, rollback auto si erreur")


# ============================================================================
# 5. ERREURS COURANTES À ÉVITER
# ============================================================================

def demo_erreurs_courantes():
    """Liste des erreurs courantes avec les transactions"""

    print("\n=== 5. ERREURS COURANTES À ÉVITER ===\n")

    print("  1. OUBLIER LE COMMIT")
    print("     session.add(user)")
    print("     # ← Où est le commit ? Les données ne sont PAS sauvées !")
    print("     session.commit()  # ← À ne JAMAIS oublier !")
    print()
    print("  2. NE PAS FERMER LA SESSION")
    print("     session = SessionLocal()")
    print("     # ... opérations ...")
    print("     # ← Où est session.close() ?")
    print("     # → Fuite de connexions → le pool se vide → crash !")
    print("     # Solution : utiliser 'with' pour fermer automatiquement")
    print()
    print("  3. MODIFIER UN OBJET DÉTACHÉ")
    print("     with SessionLocal() as session:")
    print("         user = session.get(User, 1)")
    print("     # ← La session est fermée, user est 'détaché'")
    print("     user.name = 'Nouveau'  # ← Pas suivi par la session !")
    print("     # Solution : garder la session ouverte ou utiliser merge()")
    print()
    print("  4. LE PROBLÈME N+1 (voir Jour 2)")
    print("     # Accéder aux relations dans une boucle")
    print("     # → Génère une requête SQL par élément !")
    print("     # Solution : eager loading (joinedload, selectinload)")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Gestion des Transactions")
    print("=" * 60)

    demo_transaction_manuelle()
    demo_context_manager()
    demo_pattern_fastapi()
    demo_erreurs_courantes()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 17")
    print("=" * 60)
