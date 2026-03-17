# =============================================================
# CRUD COMPLET avec SQLAlchemy - Guide pour etudiants
# =============================================================
# CRUD = Create, Read, Update, Delete
# Ce sont les 4 operations de base pour manipuler des donnees :
#   - Create = Creer (INSERT INTO en SQL)
#   - Read   = Lire   (SELECT en SQL)
#   - Update = Modifier (UPDATE en SQL)
#   - Delete = Supprimer (DELETE FROM en SQL)
#
# Ce fichier montre comment faire tout cela avec SQLAlchemy,
# une bibliotheque Python qui permet d'utiliser des classes Python
# au lieu d'ecrire du SQL a la main. C'est ce qu'on appelle un ORM
# (Object-Relational Mapping = correspondance objet-relationnel).
# =============================================================


# --- IMPORTS ---

# create_engine : cree le "moteur" qui connecte Python a la base de donnees
# Column        : represente une colonne dans une table
# Integer       : type nombre entier (1, 2, 3, ...)
# String        : type texte ("Alice", "bob@mail.com", ...)
from sqlalchemy import create_engine, Column, Integer, String

# declarative_base : permet de creer des classes Python qui representent des tables SQL
# Session          : permet d'envoyer des commandes a la base (ajouter, lire, modifier, supprimer)
from sqlalchemy.orm import declarative_base, Session

# Path : permet de construire des chemins de fichiers de maniere propre et portable
from pathlib import Path


# --- CONFIGURATION DE LA BASE DE DONNEES ---

# __file__ = le chemin de CE fichier Python (crud_demo.py)
# .resolve() = transforme en chemin absolu (ex: D:/sql/crud_demo.py)
# .parent = le dossier parent (ex: D:/sql/)
BASE_DIR = Path(__file__).resolve().parent

# On construit le chemin vers le fichier de base de donnees
# Resultat : D:/sql/demo.db
DB_PATH = BASE_DIR / "demo2.db"

# On cree le moteur de connexion a la base SQLite
# f"sqlite:///{DB_PATH}" = protocole SQLite + chemin du fichier
# echo=False : n'affiche PAS les requetes SQL dans le terminal
#              (mettre echo=True pour voir le SQL genere, utile pour apprendre)
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# On cree la classe de base dont heriteront tous nos modeles (tables)
# C'est le point de depart obligatoire pour definir des tables avec SQLAlchemy
Base = declarative_base()


# =============================================================
# DEFINITION DU MODELE (= la structure de la table)
# =============================================================
# En SQLAlchemy, une classe Python = une table SQL
# Chaque attribut de la classe = une colonne de la table
# C'est le principe de l'ORM : on manipule des objets Python
# au lieu d'ecrire du SQL a la main.

class Utilisateur(Base):
    # __tablename__ : le nom de la table dans la base de donnees
    # En SQL, ca correspond a : CREATE TABLE utilisateurs (...)
    __tablename__ = "utilisateurs"

    # Colonne "id" :
    #   - Integer = nombre entier
    #   - primary_key=True = c'est la cle primaire (identifiant unique de chaque ligne)
    #   - La cle primaire s'auto-incremente : 1, 2, 3, ... (pas besoin de la donner)
    id = Column(Integer, primary_key=True)

    # Colonne "nom" :
    #   - String(50) = texte de 50 caracteres maximum
    #   - nullable=False = ce champ est obligatoire (ne peut pas etre vide/NULL)
    nom = Column(String(50), nullable=False)

    # Colonne "email" :
    #   - String(100) = texte de 100 caracteres maximum
    #   - nullable=False = ce champ est obligatoire
    email = Column(String(100), nullable=False)

    # __repr__ : definit comment l'objet s'affiche quand on fait print()
    # Sans cette methode, on verrait : <Utilisateur object at 0x7f...>
    # Avec, on voit : Utilisateur(id=1, nom='Alice', email='alice@example.com')
    def __repr__(self):
        return f"Utilisateur(id={self.id}, nom='{self.nom}', email='{self.email}')"


# On demande a SQLAlchemy de creer toutes les tables dans la base de donnees
# Equivalent SQL : CREATE TABLE IF NOT EXISTS utilisateurs (...)
# Si la table existe deja, cette ligne ne fait rien (pas d'erreur)
Base.metadata.create_all(engine)


# =============================================================
# CREATE - Ajouter un utilisateur
# =============================================================
# Equivalent SQL : INSERT INTO utilisateurs (nom, email) VALUES ('Alice', 'alice@example.com')

def ajouter_utilisateur(nom, email):
    """
    Ajoute un nouvel utilisateur dans la base de donnees.

    Parametres :
        nom   (str) : le nom de l'utilisateur
        email (str) : l'email de l'utilisateur

    Retourne :
        int ou None : l'ID du nouvel utilisateur, ou None si l'email existe deja
    """
    # On ouvre une session (= une connexion de travail avec la base)
    # "with" garantit que la session se ferme proprement a la fin,
    # meme si une erreur se produit
    with Session(engine) as session:

        # ETAPE 1 : Verifier si l'email est deja utilise par quelqu'un
        # filter_by(email=email) = WHERE email = 'alice@example.com'
        # .first() = renvoie le premier resultat, ou None si rien trouve
        existe = session.query(Utilisateur).filter_by(email=email).first()

        # Si un utilisateur avec cet email existe deja, on refuse l'ajout
        if existe:
            print(f"  Erreur : L'email '{email}' est deja utilise par {existe.nom}.")
            return None

        # ETAPE 2 : Creer un nouvel objet Utilisateur (= une nouvelle ligne)
        nouveau = Utilisateur(nom=nom, email=email)

        # ETAPE 3 : Ajouter l'objet a la session (en attente d'envoi)
        # A ce stade, rien n'est encore envoye a la base
        session.add(nouveau)

        # ETAPE 4 : Valider et envoyer les changements dans la base
        # C'est ici que le INSERT INTO est reellement execute
        session.commit()

        # ETAPE 5 : Rafraichir l'objet pour recuperer l'ID genere automatiquement
        # Avant refresh, nouveau.id pourrait etre None
        # Apres refresh, nouveau.id = 1, 2, 3... (la valeur donnee par la base)
        session.refresh(nouveau)

        print(f"  {nouveau.nom} ajoute avec l'ID {nouveau.id}")
        return nouveau.id


# =============================================================
# READ - Lire / Rechercher des utilisateurs
# =============================================================
# Equivalent SQL : SELECT * FROM utilisateurs

def lister_utilisateurs():
    """
    Affiche TOUS les utilisateurs de la table.
    Equivalent SQL : SELECT * FROM utilisateurs
    """
    with Session(engine) as session:

        # .query(Utilisateur) = SELECT * FROM utilisateurs
        # .all() = recuperer TOUS les resultats sous forme de liste Python
        tous = session.query(Utilisateur).all()

        # Si la liste est vide, il n'y a aucun utilisateur
        if not tous:
            print("  La table est vide.")
            return

        # On parcourt la liste et on affiche chaque utilisateur
        for u in tous:
            print(f"  [{u.id}] {u.nom} - {u.email}")


def chercher_par_id(user_id):
    """
    Cherche UN utilisateur par son ID (cle primaire).
    Equivalent SQL : SELECT * FROM utilisateurs WHERE id = 1

    Parametres :
        user_id (int) : l'ID de l'utilisateur a chercher

    Retourne :
        Utilisateur ou None : l'utilisateur trouve, ou None
    """
    with Session(engine) as session:

        # session.get() est le moyen le plus rapide de chercher par cle primaire
        # Il cherche d'abord dans le cache de la session, puis dans la base
        u = session.get(Utilisateur, user_id)

        if u:
            print(f"  Trouve : [{u.id}] {u.nom} - {u.email}")
        else:
            print(f"  Aucun utilisateur avec l'ID {user_id}.")

        return u


def chercher_par_nom(nom):
    """
    Cherche les utilisateurs dont le nom CONTIENT le texte donne.
    Equivalent SQL : SELECT * FROM utilisateurs WHERE nom LIKE '%alice%'

    Parametres :
        nom (str) : le texte a chercher dans les noms

    Retourne :
        list : la liste des utilisateurs trouves (peut etre vide)
    """
    with Session(engine) as session:

        # .filter() permet d'ecrire des conditions plus complexes que filter_by()
        # .like() = operateur SQL LIKE pour la recherche partielle
        # f"%{nom}%" = le % signifie "n'importe quels caracteres avant et apres"
        # Exemple : "%ali%" trouvera "Alice", "Alicia", "Malik", etc.
        resultats = session.query(Utilisateur).filter(
            Utilisateur.nom.like(f"%{nom}%")
        ).all()

        if not resultats:
            print(f"  Aucun resultat pour '{nom}'.")
        else:
            for u in resultats:
                print(f"  [{u.id}] {u.nom} - {u.email}")

        return resultats
# =============================================================
# UPDATE - Modifier un utilisateur
# =============================================================
# Equivalent SQL : UPDATE utilisateurs SET nom = 'Nouveau' WHERE id = 1

def modifier_utilisateur(user_id, nouveau_nom=None, nouvel_email=None):
    """
    Modifie le nom et/ou l'email d'un utilisateur existant.

    Parametres :
        user_id      (int) : l'ID de l'utilisateur a modifier
        nouveau_nom  (str) : le nouveau nom (ou None pour ne pas changer)
        nouvel_email (str) : le nouvel email (ou None pour ne pas changer)

    Retourne :
        bool : True si la modification a reussi, False sinon
    """
    with Session(engine) as session:
        # ETAPE 1 : Chercher l'utilisateur par son ID
        u = session.get(Utilisateur, user_id)
        # Si l'utilisateur n'existe pas, on arrete
        if not u:
            print(f"  Aucun utilisateur avec l'ID {user_id}.")
            return False
        # ETAPE 2 : Modifier les champs demandes
        # On ne modifie que les champs pour lesquels une valeur a ete fournie
        # (si nouveau_nom est None, on ne touche pas au nom)

        if nouveau_nom:
            # On change simplement l'attribut Python
            # SQLAlchemy detecte automatiquement le changement
            u.nom = nouveau_nom
            
        if nouvel_email:
            # Avant de changer l'email, on verifie qu'il n'est pas deja pris
            # par un AUTRE utilisateur (pas par lui-meme)
            # .filter() avec deux conditions = WHERE email = '...' AND id != ...
            doublon = session.query(Utilisateur).filter(
                Utilisateur.email == nouvel_email,  # l'email est le meme
                Utilisateur.id != user_id            # mais c'est un autre utilisateur
            ).first()

            if doublon:
                print(f"  Erreur : L'email '{nouvel_email}' est deja utilise par {doublon.nom}.")
                return False

            u.email = nouvel_email

        # ETAPE 3 : Valider les modifications
        # SQLAlchemy genere automatiquement : UPDATE utilisateurs SET nom=..., email=... WHERE id=...
        session.commit()

        print(f"  Mis a jour : [{u.id}] {u.nom} - {u.email}")
        return True


# =============================================================
# DELETE - Supprimer un utilisateur
# =============================================================
# Equivalent SQL : DELETE FROM utilisateurs WHERE id = 1

def supprimer_utilisateur(user_id):
    """
    Supprime un utilisateur par son ID.

    Parametres :
        user_id (int) : l'ID de l'utilisateur a supprimer

    Retourne :
        bool : True si la suppression a reussi, False sinon
    """
    with Session(engine) as session:

        # ETAPE 1 : Chercher l'utilisateur par son ID
        u = session.get(Utilisateur, user_id)
        # Si l'utilisateur n'existe pas, on ne peut pas le supprimer
        if not u:
            print(f"  Aucun utilisateur avec l'ID {user_id}.")
            return False

        # On garde le nom en memoire pour l'afficher apres la suppression
        # (car apres session.delete(), l'objet sera detache de la session)
        nom = u.nom

        # ETAPE 2 : Marquer l'objet pour suppression
        session.delete(u)

        # ETAPE 3 : Valider la suppression dans la base
        # C'est ici que le DELETE FROM est reellement execute
        session.commit()

        print(f"  {nom} (ID {user_id}) supprime.")
        return True
def supprimer_tout():
    """
    Supprime TOUS les utilisateurs de la table.
    Equivalent SQL : DELETE FROM utilisateurs
    Attention : cette action est irreversible !
    """
    with Session(engine) as session:

        # .delete() sans filtre = supprime toutes les lignes de la table
        # Retourne le nombre de lignes supprimees
        nb = session.query(Utilisateur).delete()

        # On valide la suppression
        session.commit()

        print(f"  {nb} utilisateur(s) supprime(s).")


# =============================================================
# MENU INTERACTIF
# =============================================================
# Le menu permet a l'utilisateur de tester toutes les operations
# CRUD sans avoir a modifier le code. Il tourne en boucle
# jusqu'a ce que l'utilisateur choisisse "0" pour quitter.

def afficher_menu():
    """Affiche les options du menu dans le terminal."""
    print("\n" + "=" * 45)
    print("       MENU CRUD - Gestion Utilisateurs")
    print("=" * 45)
    print("  1. Ajouter un utilisateur       (CREATE)")
    print("  2. Lister tous les utilisateurs  (READ)")
    print("  3. Chercher par ID               (READ)")
    print("  4. Chercher par nom              (READ)")
    print("  5. Modifier un utilisateur       (UPDATE)")
    print("  6. Supprimer un utilisateur      (DELETE)")
    print("  7. Supprimer tout                (DELETE)")
    print("  0. Quitter")
    print("=" * 45)


def menu():
    """
    Boucle principale du menu interactif.
    Demande un choix a l'utilisateur et appelle la fonction correspondante.
    La boucle continue jusqu'a ce que l'utilisateur tape "0".
    """
    # while True = boucle infinie, on en sort avec "break"
    while True:

        # Afficher le menu a chaque tour de boucle
        afficher_menu()

        # Demander le choix de l'utilisateur
        # .strip() enleve les espaces en debut et fin de saisie
        choix = input("Votre choix : ").strip()

        # --- Option 1 : CREATE ---
        if choix == "1":
            print("\n--- Ajouter un utilisateur ---")
            nom = input("  Nom : ").strip()
            email = input("  Email : ").strip()
            # On verifie que les deux champs sont remplis
            if nom and email:
                ajouter_utilisateur(nom, email)
            else:
                print("  Nom et email sont obligatoires.")

        # --- Option 2 : READ (tous) ---
        elif choix == "2":
            print("\n--- Liste des utilisateurs ---")
            lister_utilisateurs()

        # --- Option 3 : READ (par ID) ---
        elif choix == "3":
            print("\n--- Recherche par ID ---")
            try:
                # int() convertit le texte en nombre
                # Si l'utilisateur tape "abc", ca leve une erreur ValueError
                user_id = int(input("  ID : "))
                chercher_par_id(user_id)
            except ValueError:
                # On attrape l'erreur si l'utilisateur n'a pas tape un nombre
                print("  Entrez un nombre valide.")

        # --- Option 4 : READ (par nom) ---
        elif choix == "4":
            print("\n--- Recherche par nom ---")
            nom = input("  Nom a chercher : ").strip()
            if nom:
                chercher_par_nom(nom)

        # --- Option 5 : UPDATE ---
        elif choix == "5":
            print("\n--- Modifier un utilisateur ---")
            try:
                user_id = int(input("  ID de l'utilisateur a modifier : "))

                # On demande les nouvelles valeurs
                # Si l'utilisateur appuie sur Entree sans rien taper,
                # .strip() donne "" (chaine vide), et "or None" la transforme en None
                nouveau_nom = input("  Nouveau nom (laisser vide pour ne pas changer) : ").strip()
                nouvel_email = input("  Nouvel email (laisser vide pour ne pas changer) : ").strip()

                # On appelle la fonction avec les valeurs
                # "nouveau_nom or None" : si nouveau_nom est "" (vide), ca devient None
                modifier_utilisateur(
                    user_id,
                    nouveau_nom=nouveau_nom or None,
                    nouvel_email=nouvel_email or None
                )
            except ValueError:
                print("  Entrez un nombre valide.")

        # --- Option 6 : DELETE (un seul) ---
        elif choix == "6":
            print("\n--- Supprimer un utilisateur ---")
            try:
                user_id = int(input("  ID a supprimer : "))
                supprimer_utilisateur(user_id)
            except ValueError:
                print("  Entrez un nombre valide.")

        # --- Option 7 : DELETE (tout) ---
        elif choix == "7":
            print("\n--- Supprimer tout ---")
            # On demande une confirmation car c'est une action dangereuse
            confirm = input("  Etes-vous sur ? (oui/non) : ").strip().lower()
            if confirm == "oui":
                supprimer_tout()
            else:
                print("  Annule.")

        # --- Option 0 : Quitter ---
        elif choix == "0":
            print("Au revoir !")
            break  # On sort de la boucle while True

        # --- Choix invalide ---
        else:
            print("Choix invalide.")


# =============================================================
# POINT D'ENTREE DU PROGRAMME
# =============================================================
# if __name__ == "__main__" : ce bloc ne s'execute QUE si on lance
# ce fichier directement (python crud_demo.py).
# Si on importe ce fichier depuis un autre fichier (import crud_demo),
# ce bloc ne s'executera PAS. Cela permet de reutiliser les fonctions
# sans declencher le menu automatiquement.

if __name__ == "__main__":

    # On insere quelques utilisateurs de test pour avoir des donnees
    print("=== Insertion des donnees de test ===")
    ajouter_utilisateur("Alice", "alice@example.com")
    ajouter_utilisateur("Bob", "bob@example.com")
    ajouter_utilisateur("Charlie", "charlie@example.com")

    # On lance le menu interactif
    # L'utilisateur peut maintenant tester toutes les operations CRUD
    menu()
