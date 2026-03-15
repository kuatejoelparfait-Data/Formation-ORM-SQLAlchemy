"""
=============================================================================
 COURS 01 - POURQUOI UN ORM ?
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Ce qu'est un ORM (Object-Relational Mapping)
 - Pourquoi on utilise un ORM au lieu du SQL brut
 - Les avantages : sécurité, maintenabilité, portabilité
 - Comparaison avant/après avec des exemples concrets

 Pour exécuter ce fichier :
   python cours_01_pourquoi_orm.py
=============================================================================
"""

# ============================================================================
# 1. QU'EST-CE QU'UN ORM ?
# ============================================================================

# ORM = Object-Relational Mapping (Mapping Objet-Relationnel)
#
# C'est une technique qui permet de faire le PONT entre :
#   - Le monde des OBJETS Python (classes, attributs, méthodes)
#   - Le monde des BASES DE DONNÉES relationnelles (tables, colonnes, SQL)
#
# Au lieu d'écrire du SQL à la main, on manipule des objets Python.
# L'ORM se charge de traduire nos opérations en requêtes SQL.
#
# Analogie simple :
#   - Sans ORM : vous parlez directement en SQL à la base de données
#   - Avec ORM : vous parlez en Python, et l'ORM traduit en SQL pour vous

# ============================================================================
# 2. SANS ORM - Le SQL brut (à éviter en production)
# ============================================================================

# Voici comment on fait SANS ORM, avec le module sqlite3 de Python :

import sqlite3

def exemple_sans_orm():
    """Démonstration du code SANS ORM - SQL brut"""

    # Étape 1 : Se connecter à la base de données
    # ":memory:" signifie qu'on crée la base en mémoire (elle disparaît à la fin)
    conn = sqlite3.connect(":memory:")

    # Étape 2 : Créer un curseur (objet qui exécute les requêtes SQL)
    cursor = conn.cursor()

    # Étape 3 : Créer la table manuellement avec du SQL
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)

    # Étape 4 : Insérer des données avec du SQL brut
    # ATTENTION : cette méthode est VULNÉRABLE aux injections SQL !
    name = "Alice"
    email = "alice@example.com"
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        (name, email)  # Les ? sont remplacés par les valeurs (paramètres)
    )
    conn.commit()  # Sauvegarder les changements

    # Étape 5 : Lire des données
    cursor.execute("SELECT * FROM users WHERE id = ?", (1,))
    row = cursor.fetchone()  # Récupérer un résultat

    # PROBLÈME : row est un TUPLE, pas un objet !
    # On accède aux données par INDEX (position), pas par NOM
    print("=== SANS ORM ===")
    print(f"row = {row}")           # (1, 'Alice', 'alice@example.com')
    print(f"row[0] = {row[0]}")     # 1 (id) - pas très lisible !
    print(f"row[1] = {row[1]}")     # 'Alice' (name) - on doit se rappeler l'ordre
    print(f"row[2] = {row[2]}")     # 'alice@example.com' (email)

    # Fermer la connexion
    conn.close()

# ============================================================================
# 3. AVEC ORM - SQLAlchemy (la bonne façon)
# ============================================================================

# Importation des outils SQLAlchemy nécessaires
from sqlalchemy import create_engine, String          # create_engine = connexion, String = type texte
from sqlalchemy.orm import DeclarativeBase             # Base pour nos modèles
from sqlalchemy.orm import Mapped, mapped_column       # Pour définir les colonnes
from sqlalchemy.orm import Session                     # Pour interagir avec la BDD

# Étape 1 : Créer une classe de Base
# Tous nos modèles (tables) hériteront de cette classe
class Base(DeclarativeBase):
    pass

# Étape 2 : Définir un MODÈLE (= une table sous forme de classe Python)
class User(Base):
    # Le nom de la table dans la base de données
    __tablename__ = "users"

    # Les colonnes de la table, définies comme des attributs Python
    id: Mapped[int] = mapped_column(primary_key=True)        # Clé primaire (identifiant unique)
    name: Mapped[str] = mapped_column(String(100))           # Nom (texte de max 100 caractères)
    email: Mapped[str] = mapped_column(String(255), unique=True)  # Email unique

    # __repr__ : comment afficher l'objet quand on fait print()
    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r}, email={self.email!r})"


def exemple_avec_orm():
    """Démonstration du code AVEC ORM - SQLAlchemy"""

    # Étape 3 : Créer le moteur de connexion
    # "sqlite:///:memory:" = base SQLite en mémoire
    # echo=True = afficher les requêtes SQL générées (utile pour apprendre)
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Étape 4 : Créer toutes les tables définies par nos modèles
    # SQLAlchemy génère automatiquement le SQL CREATE TABLE !
    Base.metadata.create_all(engine)

    # Étape 5 : Créer un utilisateur comme un OBJET Python
    print("\n=== AVEC ORM (SQLAlchemy) ===")

    with Session(engine) as session:
        # Créer un objet User (comme n'importe quel objet Python)
        user = User(name="Alice", email="alice@example.com")

        # Ajouter l'objet à la session (préparer l'insertion)
        session.add(user)

        # Sauvegarder dans la base de données
        session.commit()

        # Recharger pour obtenir l'ID généré automatiquement
        session.refresh(user)

        # Maintenant on peut accéder aux données PAR NOM (pas par index !)
        print(f"user = {user}")              # User(id=1, name='Alice', email='alice@example.com')
        print(f"user.id = {user.id}")        # 1 - accès naturel par attribut
        print(f"user.name = {user.name}")    # 'Alice' - beaucoup plus lisible !
        print(f"user.email = {user.email}")  # 'alice@example.com'


# ============================================================================
# 4. LES AVANTAGES DE L'ORM
# ============================================================================

def avantages_orm():
    """Les principaux avantages d'utiliser un ORM"""

    print("\n=== AVANTAGES DE L'ORM ===")
    print()
    print("1. SÉCURITÉ")
    print("   - Protection automatique contre les injections SQL")
    print("   - L'ORM échappe les paramètres pour vous")
    print()
    print("2. MAINTENABILITÉ")
    print("   - Code plus lisible (objets Python vs chaînes SQL)")
    print("   - Autocomplétion dans l'IDE (user.name au lieu de row[1])")
    print("   - Détection d'erreurs par le typage")
    print()
    print("3. PORTABILITÉ")
    print("   - Changez de base de données sans changer votre code")
    print("   - SQLite en dev → PostgreSQL en production")
    print("   - L'ORM adapte le SQL automatiquement")
    print()
    print("4. PRODUCTIVITÉ")
    print("   - Moins de code à écrire")
    print("   - Pas besoin de connaître le SQL par cœur")
    print("   - Gestion automatique des transactions")


# ============================================================================
# 5. EXÉCUTION DU PROGRAMME
# ============================================================================

if __name__ == "__main__":
    # On exécute les trois démonstrations
    print("=" * 60)
    print(" DÉMONSTRATION : Pourquoi utiliser un ORM ?")
    print("=" * 60)

    # Démonstration sans ORM
    exemple_sans_orm()

    # Démonstration avec ORM
    exemple_avec_orm()

    # Afficher les avantages
    avantages_orm()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 01")
    print("=" * 60)
