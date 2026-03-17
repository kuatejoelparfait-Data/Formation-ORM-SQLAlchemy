# =============================================================
# EXERCICE COMPLET - Relations SQLAlchemy & Migrations Alembic
# =============================================================
# Objectif : Construire une base de donnees pour une BIBLIOTHEQUE
# en utilisant les concepts avances de SQLAlchemy :
#   1. Relations One-to-Many (1-N)
#   2. Relations Many-to-Many (N-N)
#   3. Probleme N+1 et Eager Loading
#   4. Introduction aux Migrations Alembic
#
# Scenario : Une bibliotheque municipale veut gerer :
#   - Ses AUTEURS (qui ecrivent des livres)
#   - Ses LIVRES (ecrits par un auteur, classes par categories)
#   - Ses CATEGORIES (Python, Web, Data Science, etc.)
#   - Ses EMPRUNTS (qui a emprunte quoi et quand)
#
# Schema de la base :
#
#   Auteur (1) ──────< (N) Livre (N) >──────< (N) Categorie
#      │                      │
#      │                      │
#      │               Livre (1) ──────< (N) Emprunt
#      │
#   Un auteur ecrit          Un livre peut etre
#   plusieurs livres         emprunte plusieurs fois
#
# =============================================================


# --- IMPORTS ---
from sqlalchemy import (
    create_engine, Column, Integer, String, Text,
    ForeignKey, Table, DateTime, Boolean
)
from sqlalchemy.orm import (
    declarative_base, Session, relationship,
    joinedload, selectinload, subqueryload
)
from pathlib import Path
from datetime import datetime, timedelta


# --- CONFIGURATION ---
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "bibliotheque.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Base = declarative_base()


# =============================================================
# PARTIE 1 : RELATION ONE-TO-MANY (1-N)
# =============================================================
# Un AUTEUR ecrit PLUSIEURS LIVRES
# Un LIVRE est ecrit par UN SEUL AUTEUR
#
# C'est exactement comme la relation User -> Articles du cours.
#
# En SQL, ca se traduit par une cle etrangere (ForeignKey)
# dans la table enfant (Livre) qui pointe vers la table parent (Auteur).
#
#   Table auteurs          Table livres
#   ┌────────────┐         ┌──────────────────┐
#   │ id (PK)    │◄────────│ auteur_id (FK)   │
#   │ nom        │         │ id (PK)          │
#   │ nationalite│         │ titre            │
#   └────────────┘         │ annee_publication│
#                          └──────────────────┘
#
# Regle : Le ForeignKey est TOUJOURS du cote "Many" (le cote N)
# =============================================================

class Auteur(Base):
    __tablename__ = "auteurs"

    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    nationalite = Column(String(50), default="Inconnue")

    # relationship() : cree le lien LOGIQUE entre Auteur et Livre
    # - "Livre" : la classe cible (entre guillemets car definie plus bas)
    # - back_populates="auteur" : lien bidirectionnel (Livre.auteur pointe ici)
    # - cascade="all, delete-orphan" : si on supprime un auteur,
    #   ses livres sont automatiquement supprimes aussi
    livres = relationship("Livre", back_populates="auteur", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Auteur(id={self.id}, nom='{self.nom}')"


class Livre(Base):
    __tablename__ = "livres"

    id = Column(Integer, primary_key=True)
    titre = Column(String(200), nullable=False)
    annee_publication = Column(Integer)

    # ForeignKey : cle etrangere qui pointe vers auteurs.id
    # C'est le lien PHYSIQUE dans la base de donnees
    # nullable=False : chaque livre DOIT avoir un auteur
    auteur_id = Column(Integer, ForeignKey("auteurs.id"), nullable=False)

    # relationship() : lien logique vers l'auteur (cote enfant)
    # back_populates="livres" : correspond a Auteur.livres
    auteur = relationship("Auteur", back_populates="livres")

    # Relation 1-N avec les emprunts (definie plus bas)
    emprunts = relationship("Emprunt", back_populates="livre", cascade="all, delete-orphan")

    # Relation N-N avec les categories (definie plus bas)
    categories = relationship(
        "Categorie",
        secondary="livre_categories",  # table d'association
        back_populates="livres"
    )

    def __repr__(self):
        return f"Livre(id={self.id}, titre='{self.titre}')"


# =============================================================
# PARTIE 2 : RELATION MANY-TO-MANY (N-N)
# =============================================================
# Un LIVRE peut appartenir a PLUSIEURS CATEGORIES
# Une CATEGORIE peut contenir PLUSIEURS LIVRES
#
# Probleme : on ne peut PAS stocker plusieurs valeurs dans une colonne.
# Solution : creer une TABLE D'ASSOCIATION (table de jointure)
#
#   Table livres           Table livre_categories      Table categories
#   ┌──────────┐           ┌────────────────────┐      ┌──────────────┐
#   │ id (PK)  │◄──────────│ livre_id (FK, PK)  │      │ id (PK)      │
#   │ titre    │           │ categorie_id(FK,PK)│─────►│ nom          │
#   └──────────┘           └────────────────────┘      │ description  │
#                                                      └──────────────┘
#
# La table d'association n'a PAS de classe Python (sauf si on veut
# y ajouter des colonnes supplementaires, cf. "Association Object")
# =============================================================

# Table d'association pour la relation N-N entre Livre et Categorie
# On utilise Table() directement (pas de classe, car pas de colonnes supplementaires)

livre_categories = Table(
    "livre_categories",     # nom de la table dans la base
    Base.metadata,          # rattachee au meme Base que nos modeles
    Column("livre_id", Integer, ForeignKey("livres.id"), primary_key=True),
    Column("categorie_id", Integer, ForeignKey("categories.id"), primary_key=True)
)


class Categorie(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    nom = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

    # Relation N-N vers Livre, via la table d'association
    # secondary="livre_categories" : indique la table de jointure
    # back_populates="categories" : correspond a Livre.categories
    livres = relationship(
        "Livre",
        secondary="livre_categories",
        back_populates="categories"
    )

    def __repr__(self):
        return f"Categorie(id={self.id}, nom='{self.nom}')"


# =============================================================
# RELATION 1-N SUPPLEMENTAIRE : Livre -> Emprunts
# =============================================================
# Un LIVRE peut etre emprunte PLUSIEURS FOIS (par differentes personnes)
# Chaque EMPRUNT concerne UN SEUL LIVRE
#
# On ajoute aussi le nom de l'emprunteur et les dates

class Emprunt(Base):
    __tablename__ = "emprunts"

    id = Column(Integer, primary_key=True)
    emprunteur = Column(String(100), nullable=False)        # nom de la personne
    date_emprunt = Column(DateTime, default=datetime.now)    # date d'emprunt
    date_retour = Column(DateTime, nullable=True)            # None = pas encore rendu
    rendu = Column(Boolean, default=False)                   # True = livre rendu

    # Cle etrangere vers le livre emprunte
    livre_id = Column(Integer, ForeignKey("livres.id"), nullable=False)

    # Relation vers le livre
    livre = relationship("Livre", back_populates="emprunts")

    def __repr__(self):
        statut = "rendu" if self.rendu else "en cours"
        return f"Emprunt(id={self.id}, '{self.emprunteur}', {statut})"


# --- Creation des tables ---
Base.metadata.create_all(engine)


# =============================================================
# FONCTIONS CRUD
# =============================================================

# --- CREATE ---

def ajouter_auteur(nom, nationalite="Inconnue"):
    """Ajoute un auteur dans la base."""
    with Session(engine) as session:
        auteur = Auteur(nom=nom, nationalite=nationalite)
        session.add(auteur)
        session.commit()
        session.refresh(auteur)
        print(f"  Auteur ajoute : {auteur}")
        return auteur.id


def ajouter_livre(titre, auteur_id, annee=None, categories_noms=None):
    """
    Ajoute un livre avec son auteur et eventuellement des categories.

    Parametres :
        titre            (str)  : titre du livre
        auteur_id        (int)  : ID de l'auteur
        annee            (int)  : annee de publication (optionnel)
        categories_noms  (list) : liste de noms de categories (optionnel)
                                  ex: ["Python", "Web"]
    """
    with Session(engine) as session:
        # Verifier que l'auteur existe
        auteur = session.get(Auteur, auteur_id)
        if not auteur:
            print(f"  Erreur : Aucun auteur avec l'ID {auteur_id}")
            return None

        # Creer le livre
        livre = Livre(titre=titre, auteur_id=auteur_id, annee_publication=annee)

        # Associer les categories (relation N-N)
        if categories_noms:
            for nom_cat in categories_noms:
                # Chercher la categorie existante ou la creer
                cat = session.query(Categorie).filter_by(nom=nom_cat).first()
                if not cat:
                    cat = Categorie(nom=nom_cat)
                    session.add(cat)
                # Ajouter la categorie au livre (insertion dans livre_categories)
                livre.categories.append(cat)

        session.add(livre)
        session.commit()
        session.refresh(livre)
        print(f"  Livre ajoute : {livre}")
        return livre.id


def ajouter_categorie(nom, description=None):
    """Ajoute une categorie."""
    with Session(engine) as session:
        existe = session.query(Categorie).filter_by(nom=nom).first()
        if existe:
            print(f"  La categorie '{nom}' existe deja (ID {existe.id}).")
            return existe.id

        cat = Categorie(nom=nom, description=description)
        session.add(cat)
        session.commit()
        session.refresh(cat)
        print(f"  Categorie ajoutee : {cat}")
        return cat.id


def emprunter_livre(livre_id, emprunteur):
    """Enregistre un emprunt de livre."""
    with Session(engine) as session:
        livre = session.get(Livre, livre_id)
        if not livre:
            print(f"  Erreur : Aucun livre avec l'ID {livre_id}")
            return None

        emprunt = Emprunt(
            livre_id=livre_id,
            emprunteur=emprunteur,
            date_emprunt=datetime.now()
        )
        session.add(emprunt)
        session.commit()
        session.refresh(emprunt)
        print(f"  Emprunt enregistre : {emprunteur} a emprunte '{livre.titre}'")
        return emprunt.id


# --- READ ---

    def lister_auteurs():
        """Affiche tous les auteurs avec le nombre de livres ecrits."""
        with Session(engine) as session:
            auteurs = session.query(Auteur).all()
            if not auteurs:
                print("  Aucun auteur dans la base.")
                return
            for a in auteurs:
                nb_livres = len(a.livres)
                print(f"  [{a.id}] {a.nom} ({a.nationalite}) - {nb_livres} livre(s)")


    def lister_livres():
        """Affiche tous les livres avec leur auteur et leurs categories."""
        with Session(engine) as session:
            livres = session.query(Livre).all()
            if not livres:
                print("  Aucun livre dans la base.")
                return
            for l in livres:
                cats = ", ".join([c.nom for c in l.categories]) or "Aucune"
                print(f"  [{l.id}] '{l.titre}' par {l.auteur.nom} ({l.annee_publication}) "
                    f"- Categories: {cats}")


    def lister_categories():
        """Affiche toutes les categories avec le nombre de livres."""
        with Session(engine) as session:
            categories = session.query(Categorie).all()
            if not categories:
                print("  Aucune categorie dans la base.")
                return
            for c in categories:
                print(f"  [{c.id}] {c.nom} - {len(c.livres)} livre(s)")


    def lister_emprunts():
        """Affiche tous les emprunts en cours."""
        with Session(engine) as session:
            emprunts = session.query(Emprunt).filter_by(rendu=False).all()
            if not emprunts:
                print("  Aucun emprunt en cours.")
                return
            for e in emprunts:
                print(f"  [{e.id}] {e.emprunteur} -> '{e.livre.titre}' "
                    f"(depuis le {e.date_emprunt.strftime('%d/%m/%Y')})")


    def livres_par_categorie(nom_categorie):
        """Affiche tous les livres d'une categorie donnee."""
        with Session(engine) as session:
            cat = session.query(Categorie).filter_by(nom=nom_categorie).first()
            if not cat:
                print(f"  Categorie '{nom_categorie}' introuvable.")
                return
            print(f"  Livres dans la categorie '{cat.nom}' :")
            for livre in cat.livres:
                print(f"    - '{livre.titre}' par {livre.auteur.nom}")


    # --- UPDATE ---

    def rendre_livre(emprunt_id):
        """Marque un emprunt comme rendu."""
        with Session(engine) as session:
            emprunt = session.get(Emprunt, emprunt_id)
            if not emprunt:
                print(f"  Aucun emprunt avec l'ID {emprunt_id}.")
                return False
            if emprunt.rendu:
                print(f"  Cet emprunt est deja marque comme rendu.")
                return False

            emprunt.rendu = True
            emprunt.date_retour = datetime.now()
            session.commit()
            print(f"  Livre rendu par {emprunt.emprunteur} le "
                f"{emprunt.date_retour.strftime('%d/%m/%Y')}")
            return True


    def ajouter_categorie_a_livre(livre_id, nom_categorie):
        """Ajoute une categorie a un livre existant (relation N-N)."""
        with Session(engine) as session:
            livre = session.get(Livre, livre_id)
            if not livre:
                print(f"  Aucun livre avec l'ID {livre_id}.")
                return False

            # Chercher ou creer la categorie
            cat = session.query(Categorie).filter_by(nom=nom_categorie).first()
            if not cat:
                cat = Categorie(nom=nom_categorie)
                session.add(cat)

            # Verifier que l'association n'existe pas deja
            if cat in livre.categories:
                print(f"  '{livre.titre}' est deja dans la categorie '{nom_categorie}'.")
                return False

            # Ajouter l'association (INSERT dans livre_categories)
            livre.categories.append(cat)
            session.commit()
            print(f"  Categorie '{nom_categorie}' ajoutee a '{livre.titre}'")
            return True


    # --- DELETE ---

    def supprimer_auteur(auteur_id):
        """
        Supprime un auteur ET tous ses livres (cascade delete-orphan).
        Attention : les emprunts lies aux livres seront aussi supprimes !
        """
        with Session(engine) as session:
            auteur = session.get(Auteur, auteur_id)
            if not auteur:
                print(f"  Aucun auteur avec l'ID {auteur_id}.")
                return False

            nom = auteur.nom
            nb_livres = len(auteur.livres)
            session.delete(auteur)
            session.commit()
            print(f"  {nom} supprime (avec ses {nb_livres} livre(s)).")
            return True


    def retirer_categorie_de_livre(livre_id, nom_categorie):
        """Retire une categorie d'un livre (sans supprimer la categorie elle-meme)."""
        with Session(engine) as session:
            livre = session.get(Livre, livre_id)
            if not livre:
                print(f"  Aucun livre avec l'ID {livre_id}.")
                return False

            cat = session.query(Categorie).filter_by(nom=nom_categorie).first()
            if not cat or cat not in livre.categories:
                print(f"  '{livre.titre}' n'a pas la categorie '{nom_categorie}'.")
                return False

            # Retirer l'association (DELETE dans livre_categories)
            # La categorie elle-meme N'EST PAS supprimee
            livre.categories.remove(cat)
            session.commit()
            print(f"  Categorie '{nom_categorie}' retiree de '{livre.titre}'")
            return True


    # =============================================================
    # PARTIE 3 : PROBLEME N+1 - DEMONSTRATION
    # =============================================================
    # Le probleme N+1 survient quand on accede aux relations dans
    # une boucle. SQLAlchemy utilise le "lazy loading" par defaut :
    # il ne charge les relations que quand on y accede.
    #
    # Exemple : pour afficher 10 auteurs avec leurs livres,
    # SQLAlchemy execute :
    #   - 1 requete  : SELECT * FROM auteurs          (les auteurs)
    #   - 10 requetes : SELECT * FROM livres WHERE ... (les livres de chaque auteur)
    #   = 11 requetes au lieu de 1 ou 2 !
    #
    # Avec 1000 auteurs, ca ferait 1001 requetes... tres lent !
    # =============================================================

    # Compteur de requetes SQL (pour mesurer le probleme)
    compteur_requetes = {"count": 0}

    def activer_compteur():
        """Active le compteur de requetes SQL pour mesurer les performances."""
        from sqlalchemy import event

        @event.listens_for(engine, "before_cursor_execute")
        def compter(conn, cursor, statement, parameters, context, executemany):
            compteur_requetes["count"] += 1


    def demo_probleme_n_plus_1():
        """
        Demontre le probleme N+1 : trop de requetes SQL.
        """
        print("\n" + "=" * 60)
        print("  DEMONSTRATION DU PROBLEME N+1")
        print("=" * 60)

        activer_compteur()

        with Session(engine) as session:
            # --- SANS eager loading (probleme N+1) ---
            print("\n  [LAZY LOADING] - Comportement par defaut :")
            compteur_requetes["count"] = 0

            # 1 requete : SELECT * FROM auteurs
            auteurs = session.query(Auteur).all()

            for auteur in auteurs:
                # A chaque tour : 1 requete supplementaire pour charger les livres !
                # SELECT * FROM livres WHERE auteur_id = ?
                nb = len(auteur.livres)

            print(f"    Nombre d'auteurs : {len(auteurs)}")
            print(f"    Requetes SQL executees : {compteur_requetes['count']}")
            print(f"    (1 pour les auteurs + {compteur_requetes['count'] - 1} pour les livres)")

        with Session(engine) as session:
            # --- AVEC selectinload (solution recommandee) ---
            print("\n  [SELECTINLOAD] - Solution recommandee :")
            compteur_requetes["count"] = 0

            # 2 requetes seulement :
            #   1. SELECT * FROM auteurs
            #   2. SELECT * FROM livres WHERE auteur_id IN (1, 2, 3, ...)
            auteurs = session.query(Auteur).options(
                selectinload(Auteur.livres)
            ).all()

            for auteur in auteurs:
                nb = len(auteur.livres)  # Pas de requete supplementaire !

            print(f"    Nombre d'auteurs : {len(auteurs)}")
            print(f"    Requetes SQL executees : {compteur_requetes['count']}")
            print(f"    (Seulement 2 requetes, quelle que soit la quantite !)")

        with Session(engine) as session:
            # --- AVEC joinedload ---
            print("\n  [JOINEDLOAD] - Tout en 1 seule requete (JOIN) :")
            compteur_requetes["count"] = 0

            # 1 seule requete avec LEFT JOIN :
            #   SELECT * FROM auteurs LEFT JOIN livres ON ...
            auteurs = session.query(Auteur).options(
                joinedload(Auteur.livres)
            ).unique().all()  # .unique() obligatoire avec joinedload

            for auteur in auteurs:
                nb = len(auteur.livres)

            print(f"    Nombre d'auteurs : {len(auteurs)}")
            print(f"    Requetes SQL executees : {compteur_requetes['count']}")

        print("\n  Conclusion :")
        print("  ┌─────────────────┬───────────────┬─────────────────────────┐")
        print("  │ Strategie       │ Nb requetes   │ Quand l'utiliser        │")
        print("  ├─────────────────┼───────────────┼─────────────────────────┤")
        print("  │ lazyload        │ 1 + N         │ EVITER dans les boucles │")
        print("  │ selectinload    │ 2             │ RECOMMANDE (1-N)        │")
        print("  │ joinedload      │ 1 (JOIN)      │ Relations 1-1           │")
        print("  │ subqueryload    │ 2 (subquery)  │ Avec pagination (LIMIT) │")
        print("  └─────────────────┴───────────────┴─────────────────────────┘")


    # =============================================================
    # PARTIE 4 : MIGRATIONS ALEMBIC (GUIDE)
    # =============================================================
    # Alembic = outil de migration officiel de SQLAlchemy
    # Migration = modifier la structure de la base (ajouter/supprimer
    # des colonnes, des tables, etc.) sans perdre les donnees.
    #
    # C'est comme Git pour le schema de la base de donnees :
    #   - git commit  <->  alembic revision (creer une migration)
    #   - git push    <->  alembic upgrade (appliquer les changements)
    #   - git revert  <->  alembic downgrade (annuler les changements)
    # =============================================================

    def guide_alembic():
        """Affiche un guide des commandes Alembic essentielles."""
        print("\n" + "=" * 60)
        print("  GUIDE DES MIGRATIONS ALEMBIC")
        print("=" * 60)

        print("""
    1. INITIALISATION (une seule fois par projet) :
        $ pip install alembic
        $ alembic init alembic

        Cela cree :
        alembic/
        ├── env.py            <- Configuration (importer vos modeles ici !)
        ├── script.py.mako    <- Template des migrations
        └── versions/         <- Les fichiers de migration
        alembic.ini           <- URL de la base de donnees

    2. CONFIGURATION :
        - Dans alembic.ini, modifier la ligne :
        sqlalchemy.url = sqlite:///bibliotheque.db

        - Dans alembic/env.py, ajouter :
        from exercice_relations_complet import Base
        target_metadata = Base.metadata

    3. CREER UNE MIGRATION :
        $ alembic revision --autogenerate -m "creation initiale"

        Alembic compare vos modeles Python avec la base et genere
        automatiquement le code de migration (upgrade + downgrade).

    4. APPLIQUER LA MIGRATION :
        $ alembic upgrade head

    5. ANNULER LA DERNIERE MIGRATION :
        $ alembic downgrade -1

    6. VOIR L'HISTORIQUE :
        $ alembic history
        $ alembic current

    EXEMPLE DE WORKFLOW :
    ─────────────────────
    Imaginez qu'on veut ajouter un champ "isbn" aux livres :

        Etape 1 : Modifier le modele Python
        class Livre(Base):
            ...
            isbn = Column(String(13))  # <- nouveau champ

        Etape 2 : Generer la migration
        $ alembic revision --autogenerate -m "ajout isbn aux livres"

        Etape 3 : Verifier le fichier genere dans alembic/versions/
        def upgrade():
            op.add_column('livres', sa.Column('isbn', sa.String(13)))

        def downgrade():
            op.drop_column('livres', 'isbn')

        Etape 4 : Appliquer
        $ alembic upgrade head

    BONNES PRATIQUES :
    ──────────────────
        - Toujours verifier le fichier de migration avant de l'appliquer
        - 1 changement = 1 migration (pas tout d'un coup)
        - Ne jamais modifier une migration deja appliquee en production
        - Tester le downgrade avant de pousser
        - Commiter les migrations dans Git avec le code
    """)


    # =============================================================
    # INSERTION DES DONNEES DE TEST
    # =============================================================

    def inserer_donnees_test():
        """Insere un jeu de donnees complet pour tester toutes les fonctionnalites."""
        print("=== Insertion des donnees de test ===\n")

        # --- Auteurs ---
        print("--- Auteurs ---")
        id_guido = ajouter_auteur("Guido van Rossum", "Neerlandais")
        id_linus = ajouter_auteur("Linus Torvalds", "Finlandais")
        id_ada = ajouter_auteur("Ada Lovelace", "Britannique")
        id_grace = ajouter_auteur("Grace Hopper", "Americaine")

        # --- Categories ---
        print("\n--- Categories ---")
        ajouter_categorie("Python", "Tout sur le langage Python")
        ajouter_categorie("Web", "Developpement web")
        ajouter_categorie("Data Science", "Analyse de donnees et IA")
        ajouter_categorie("Systeme", "Systemes d'exploitation et bas niveau")
        ajouter_categorie("Debutant", "Pour les debutants")

        # --- Livres (avec categories = relation N-N) ---
        print("\n--- Livres ---")
        id_l1 = ajouter_livre("Python pour tous", id_guido, 2020,
                            ["Python", "Debutant"])
        id_l2 = ajouter_livre("Django en pratique", id_guido, 2021,
                            ["Python", "Web"])
        id_l3 = ajouter_livre("Data Science avec Python", id_guido, 2022,
                            ["Python", "Data Science"])
        id_l4 = ajouter_livre("Le noyau Linux", id_linus, 2019,
                            ["Systeme"])
        id_l5 = ajouter_livre("Git pour les nuls", id_linus, 2020,
                            ["Debutant"])
        id_l6 = ajouter_livre("Les bases de l'algorithmique", id_ada, 2018,
                            ["Debutant"])
        id_l7 = ajouter_livre("Compilateurs modernes", id_grace, 2021,
                            ["Systeme"])

        # --- Emprunts ---
        print("\n--- Emprunts ---")
        emprunter_livre(id_l1, "Marie Dupont")
        emprunter_livre(id_l2, "Jean Martin")
        emprunter_livre(id_l3, "Marie Dupont")
        emprunter_livre(id_l4, "Pierre Bernard")
        emprunter_livre(id_l5, "Sophie Petit")

        print("\n=== Donnees de test inserees avec succes ===")


    # =============================================================
    # MENU INTERACTIF
    # =============================================================

    def afficher_menu():
        """Affiche les options du menu."""
        print("\n" + "=" * 55)
        print("     BIBLIOTHEQUE - Menu de gestion")
        print("=" * 55)
        print("  --- CREATE ---")
        print("  1.  Ajouter un auteur")
        print("  2.  Ajouter un livre")
        print("  3.  Ajouter une categorie")
        print("  4.  Emprunter un livre")
        print()
        print("  --- READ ---")
        print("  5.  Lister les auteurs")
        print("  6.  Lister les livres")
        print("  7.  Lister les categories")
        print("  8.  Voir les emprunts en cours")
        print("  9.  Livres par categorie")
        print()
        print("  --- UPDATE ---")
        print("  10. Rendre un livre")
        print("  11. Ajouter une categorie a un livre")
        print()
        print("  --- DELETE ---")
        print("  12. Supprimer un auteur (et ses livres)")
        print("  13. Retirer une categorie d'un livre")
        print()
        print("  --- AVANCE ---")
        print("  14. Demo probleme N+1")
        print("  15. Guide Alembic")
        print()
        print("  0.  Quitter")
        print("=" * 55)


    def menu():
        """Boucle principale du menu interactif."""
        while True:
            afficher_menu()
            choix = input("Votre choix : ").strip()

            if choix == "1":
                print("\n--- Ajouter un auteur ---")
                nom = input("  Nom : ").strip()
                nationalite = input("  Nationalite (Entree pour 'Inconnue') : ").strip()
                if nom:
                    ajouter_auteur(nom, nationalite or "Inconnue")
                else:
                    print("  Le nom est obligatoire.")

            elif choix == "2":
                print("\n--- Ajouter un livre ---")
                titre = input("  Titre : ").strip()
                try:
                    auteur_id = int(input("  ID de l'auteur : "))
                    annee = input("  Annee de publication (optionnel) : ").strip()
                    cats = input("  Categories (separees par des virgules, optionnel) : ").strip()
                    categories_noms = [c.strip() for c in cats.split(",") if c.strip()] if cats else None
                    ajouter_livre(titre, auteur_id, int(annee) if annee else None, categories_noms)
                except ValueError:
                    print("  Entrez des nombres valides.")

            elif choix == "3":
                print("\n--- Ajouter une categorie ---")
                nom = input("  Nom : ").strip()
                desc = input("  Description (optionnel) : ").strip()
                if nom:
                    ajouter_categorie(nom, desc or None)

            elif choix == "4":
                print("\n--- Emprunter un livre ---")
                try:
                    livre_id = int(input("  ID du livre : "))
                    emprunteur = input("  Nom de l'emprunteur : ").strip()
                    if emprunteur:
                        emprunter_livre(livre_id, emprunteur)
                    else:
                        print("  Le nom est obligatoire.")
                except ValueError:
                    print("  Entrez un nombre valide.")

            elif choix == "5":
                print("\n--- Auteurs ---")
                lister_auteurs()

            elif choix == "6":
                print("\n--- Livres ---")
                lister_livres()

            elif choix == "7":
                print("\n--- Categories ---")
                lister_categories()

            elif choix == "8":
                print("\n--- Emprunts en cours ---")
                lister_emprunts()

            elif choix == "9":
                print("\n--- Livres par categorie ---")
                nom = input("  Nom de la categorie : ").strip()
                if nom:
                    livres_par_categorie(nom)

            elif choix == "10":
                print("\n--- Rendre un livre ---")
                try:
                    emprunt_id = int(input("  ID de l'emprunt : "))
                    rendre_livre(emprunt_id)
                except ValueError:
                    print("  Entrez un nombre valide.")

            elif choix == "11":
                print("\n--- Ajouter une categorie a un livre ---")
                try:
                    livre_id = int(input("  ID du livre : "))
                    nom_cat = input("  Nom de la categorie : ").strip()
                    if nom_cat:
                        ajouter_categorie_a_livre(livre_id, nom_cat)
                except ValueError:
                    print("  Entrez un nombre valide.")

            elif choix == "12":
                print("\n--- Supprimer un auteur ---")
                try:
                    auteur_id = int(input("  ID de l'auteur a supprimer : "))
                    confirm = input("  Cela supprimera aussi ses livres. Confirmer ? (oui/non) : ").strip().lower()
                    if confirm == "oui":
                        supprimer_auteur(auteur_id)
                    else:
                        print("  Annule.")
                except ValueError:
                    print("  Entrez un nombre valide.")

            elif choix == "13":
                print("\n--- Retirer une categorie d'un livre ---")
                try:
                    livre_id = int(input("  ID du livre : "))
                    nom_cat = input("  Nom de la categorie a retirer : ").strip()
                    if nom_cat:
                        retirer_categorie_de_livre(livre_id, nom_cat)
                except ValueError:
                    print("  Entrez un nombre valide.")

            elif choix == "14":
                demo_probleme_n_plus_1()

            elif choix == "15":
                guide_alembic()

            elif choix == "0":
                print("Au revoir !")
                break

            else:
                print("Choix invalide.")


    # =============================================================
    # POINT D'ENTREE
    # =============================================================

    if __name__ == "__main__":
        inserer_donnees_test()
        menu()
