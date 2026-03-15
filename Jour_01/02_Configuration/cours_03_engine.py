"""
=============================================================================
 COURS 03 - L'ENGINE (Moteur de connexion)
 Formation SQLAlchemy 2.0 - Jour 1
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Ce qu'est l'Engine (le point d'entrée vers la base de données)
 - Le format des URLs de connexion
 - Les options du pool de connexions
 - Comment se connecter à SQLite, PostgreSQL, MySQL

 Pour exécuter :
   python cours_03_engine.py
=============================================================================
"""

from sqlalchemy import create_engine, text

# ============================================================================
# 1. QU'EST-CE QUE L'ENGINE ?
# ============================================================================
#
# L'Engine est le MOTEUR de connexion à la base de données.
# C'est le tout premier objet que vous créez avec SQLAlchemy.
#
# Il fait deux choses :
#   1. Il sait COMMENT se connecter à votre base (URL, credentials)
#   2. Il gère un POOL de connexions (réutilise les connexions)
#
# Analogie : L'Engine est comme un standard téléphonique
#   → Il connaît le numéro de la base de données
#   → Il gère plusieurs lignes en même temps (pool)
#   → Il réutilise les lignes libres au lieu d'en créer de nouvelles

# ============================================================================
# 2. FORMAT DE L'URL DE CONNEXION
# ============================================================================
#
# L'URL suit ce format :
#   dialect+driver://username:password@host:port/database
#
# Décomposition :
#   dialect  = type de base (sqlite, postgresql, mysql)
#   driver   = bibliothèque Python pour se connecter (psycopg2, pymysql)
#   username = nom d'utilisateur de la base
#   password = mot de passe
#   host     = adresse du serveur (localhost, IP, domaine)
#   port     = port du serveur (5432 pour PostgreSQL, 3306 pour MySQL)
#   database = nom de la base de données

# ============================================================================
# 3. EXEMPLES DE CONNEXION
# ============================================================================

def exemples_connexion():
    """Différentes façons de créer un Engine selon la base de données"""

    print("=== EXEMPLES D'URLs DE CONNEXION ===\n")

    # ---- SQLite (pour le développement) ----
    # SQLite est une base de données LOCALE (un simple fichier)
    # Parfait pour apprendre et développer !

    # Base en mémoire (disparaît quand le programme s'arrête)
    engine_memory = create_engine("sqlite:///:memory:")
    print("1. SQLite en mémoire : sqlite:///:memory:")

    # Base dans un fichier (persistante)
    # Les 3 slashes /// = chemin relatif
    # engine_file = create_engine("sqlite:///app.db")
    print("2. SQLite fichier    : sqlite:///app.db")

    # ---- PostgreSQL (pour la production) ----
    # PostgreSQL est la base recommandée pour les applications pro
    # Nécessite un serveur PostgreSQL installé

    # engine_pg = create_engine(
    #     "postgresql+psycopg2://user:password@localhost:5432/mydb"
    # )
    print("3. PostgreSQL        : postgresql+psycopg2://user:password@localhost:5432/mydb")

    # ---- MySQL / MariaDB ----
    # engine_mysql = create_engine(
    #     "mysql+pymysql://user:password@localhost:3306/mydb"
    # )
    print("4. MySQL             : mysql+pymysql://user:password@localhost:3306/mydb")

    return engine_memory


# ============================================================================
# 4. OPTIONS DU POOL DE CONNEXIONS
# ============================================================================

def demo_pool_options():
    """Les options du pool de connexions (pour la production)"""

    print("\n=== OPTIONS DU POOL DE CONNEXIONS ===\n")

    # En production, on configure le pool pour optimiser les performances
    engine = create_engine(
        "sqlite:///:memory:",

        # echo=True : affiche les requêtes SQL dans la console
        # Très utile pour APPRENDRE et DÉBUGGER
        # Mettre False en production !
        echo=False,

        # pool_size : nombre de connexions gardées dans le pool
        # Par défaut = 5
        # Augmenter si beaucoup d'utilisateurs simultanés
        pool_size=5,

        # max_overflow : connexions SUPPLÉMENTAIRES temporaires
        # Si les 5 connexions du pool sont occupées,
        # on peut en créer 10 de plus temporairement
        max_overflow=10,

        # pool_timeout : combien de SECONDES attendre pour obtenir une connexion
        # Si toutes les connexions sont prises, on attend max 30 secondes
        pool_timeout=30,

        # pool_recycle : recycler les connexions après N secondes
        # Utile car certaines BDD ferment les connexions inactives
        # 1800 = 30 minutes
        pool_recycle=1800,
    )

    print("Options configurées :")
    print(f"  pool_size     = 5  (connexions dans le pool)")
    print(f"  max_overflow  = 10 (connexions supplémentaires)")
    print(f"  pool_timeout  = 30 (secondes d'attente max)")
    print(f"  pool_recycle  = 1800 (recycler après 30 min)")

    return engine


# ============================================================================
# 5. TESTER LA CONNEXION
# ============================================================================

def tester_connexion():
    """Vérifier que la connexion fonctionne"""

    print("\n=== TEST DE CONNEXION ===\n")

    # Créer un engine SQLite en mémoire
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Tester la connexion avec une requête simple
    with engine.connect() as conn:
        # text() permet d'écrire du SQL brut
        result = conn.execute(text("SELECT 1"))
        value = result.scalar()  # Récupérer la valeur unique
        print(f"  Résultat de 'SELECT 1' : {value}")
        print("  ✓ Connexion réussie !")

    # Informations sur l'engine
    print(f"\n  URL de la base : {engine.url}")
    print(f"  Dialect (type) : {engine.dialect.name}")


# ============================================================================
# 6. SÉCURITÉ : NE JAMAIS HARDCODER LES CREDENTIALS !
# ============================================================================
#
# MAUVAISE PRATIQUE (ne faites JAMAIS ça) :
#   engine = create_engine("postgresql://admin:MonMotDePasse123@prod-server/mydb")
#
# BONNE PRATIQUE : utiliser des variables d'environnement
#   import os
#   database_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
#   engine = create_engine(database_url)
#
# ENCORE MIEUX : utiliser pydantic-settings (voir cours_05)
#   → Les credentials sont dans un fichier .env (ignoré par git)
#   → Jamais dans le code source !

# ============================================================================
# 7. EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : L'Engine (Moteur de connexion)")
    print("=" * 60)

    exemples_connexion()
    demo_pool_options()
    tester_connexion()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 03")
    print("=" * 60)
