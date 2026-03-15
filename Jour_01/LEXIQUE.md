# LEXIQUE - Jour 1 : SQLAlchemy Core et ORM Fondamentaux

## Concepts fondamentaux

- **ORM (Object-Relational Mapping)** : Technique qui permet de manipuler une base de données relationnelle en utilisant des objets Python au lieu d'écrire du SQL. L'ORM traduit automatiquement les opérations Python en requêtes SQL.

- **SQLAlchemy** : La bibliothèque ORM la plus populaire en Python. Utilisée par Reddit, Dropbox, Yelp, Mozilla. Version actuelle : 2.0.

- **SQLAlchemy Core** : La couche bas niveau de SQLAlchemy, proche du SQL. Utilisée pour les requêtes complexes et les opérations bulk (10% des cas).

- **SQLAlchemy ORM** : La couche haut niveau de SQLAlchemy, basée sur les objets Python. Utilisée pour les opérations CRUD et les APIs (90% des cas).

## Configuration

- **Engine** : Le moteur de connexion à la base de données. C'est le premier objet à créer. Il gère le pool de connexions. Créé avec `create_engine("url")`.

- **Session** : L'objet qui gère les interactions avec la base. Elle accumule les modifications avant de les sauvegarder (pattern Unit of Work). Créée via `sessionmaker`.

- **sessionmaker** : Une "fabrique" de sessions. Crée des sessions pré-configurées avec les mêmes paramètres.

- **DeclarativeBase / Base** : La classe de base dont héritent tous vos modèles. Permet à SQLAlchemy de connaître la structure de vos tables.

- **Pool de connexions** : Un ensemble de connexions réutilisables vers la base de données. Évite de créer/fermer une connexion à chaque requête.

- **echo** : Option de l'Engine (`echo=True`) qui affiche les requêtes SQL générées dans la console. Très utile pour apprendre et débugger.

## Définition des modèles

- **Mapped** : Annotation de type qui indique qu'un attribut est une colonne de la table. `Mapped[int]` = colonne entière obligatoire, `Mapped[Optional[str]]` = colonne texte nullable.

- **mapped_column** : Fonction qui configure une colonne (type, contraintes, valeur par défaut).

- **__tablename__** : Attribut de classe qui définit le nom de la table dans la base de données. Convention : pluriel, minuscules, underscores.

- **primary_key** : Identifiant unique de chaque ligne. Auto-incrémenté par défaut. `mapped_column(primary_key=True)`.

- **unique** : Contrainte qui interdit les doublons dans une colonne. Ex: `unique=True` pour les emails.

- **index** : Structure qui accélère les recherches sur une colonne. `index=True` pour les colonnes souvent filtrées.

- **nullable** : Indique si une colonne peut contenir NULL. `Mapped[Optional[str]]` rend la colonne nullable automatiquement.

- **default** : Valeur par défaut côté Python. Appliquée AVANT l'envoi à la base.

- **server_default** : Valeur par défaut côté serveur (base de données). Appliquée PAR la base. Ex: `server_default=func.now()`.

- **onupdate** : Valeur automatiquement mise à jour à chaque modification. Ex: `onupdate=func.now()` pour updated_at.

## Types de colonnes

- **Integer** : Nombre entier (int). Pour les IDs, compteurs, quantités.
- **String(n)** : Texte limité à n caractères (VARCHAR). Pour les noms, emails.
- **Text** : Texte sans limite de longueur. Pour les descriptions, contenus.
- **Boolean** : Vrai ou Faux (True/False). Pour les flags, statuts.
- **Float** : Nombre décimal approximatif. Pour les mesures.
- **Numeric(p, s)** : Nombre décimal PRÉCIS. Pour les prix et montants. p=précision totale, s=décimales.
- **DateTime** : Date et heure. Pour les timestamps.
- **Date** : Date sans heure.
- **JSON** : Données semi-structurées (dictionnaires Python).
- **Enum** : Liste de valeurs prédéfinies. Ex: statut = PENDING, CONFIRMED, SHIPPED.

## Opérations CRUD

- **CRUD** : Create (créer), Read (lire), Update (modifier), Delete (supprimer). Les 4 opérations de base sur les données.

- **session.add(objet)** : Ajouter un objet à la session (préparer l'insertion).
- **session.add_all(liste)** : Ajouter plusieurs objets d'un coup.
- **session.commit()** : Sauvegarder toutes les modifications en base (valider la transaction).
- **session.rollback()** : Annuler toutes les modifications non sauvées.
- **session.refresh(objet)** : Recharger un objet depuis la base (pour obtenir les valeurs auto-générées).
- **session.get(Classe, id)** : Récupérer un objet par sa clé primaire. Retourne None si non trouvé.
- **session.delete(objet)** : Marquer un objet pour suppression.

## Requêtes

- **select(Classe)** : Créer une requête SELECT (style SQLAlchemy 2.0).
- **where()** : Ajouter une condition WHERE à la requête.
- **filter() / filter_by()** : Filtrer les résultats (style 1.x).
- **first()** : Retourner le premier résultat ou None.
- **one()** : Retourner exactement un résultat (erreur si 0 ou plus de 1).
- **all()** : Retourner tous les résultats (liste).
- **scalar_one_or_none()** : Retourner un seul objet ou None.
- **scalars()** : Convertir les résultats en objets (au lieu de Row/tuples).

## Filtres avancés

- **and_()** : Combiner des conditions avec ET.
- **or_()** : Combiner des conditions avec OU.
- **not_()** : Inverser une condition.
- **in_(liste)** : Vérifier si la valeur est dans une liste.
- **like("pattern")** : Recherche avec motif (sensible à la casse).
- **ilike("pattern")** : Recherche avec motif (insensible à la casse).
- **is_(None)** : Vérifier si la valeur est NULL.
- **is_not(None)** : Vérifier si la valeur n'est pas NULL.

## Tri et pagination

- **order_by()** : Trier les résultats.
- **asc()** : Tri ascendant (A→Z, 0→9).
- **desc()** : Tri descendant (Z→A, 9→0).
- **offset(n)** : Sauter les n premiers résultats.
- **limit(n)** : Limiter à n résultats.
- **Pagination** : Technique pour afficher les résultats par pages. Formule : `offset = (page - 1) * page_size`.

## Agrégations

- **func.count()** : Compter le nombre de lignes.
- **func.sum()** : Additionner les valeurs.
- **func.avg()** : Calculer la moyenne.
- **func.min()** : Trouver la valeur minimale.
- **func.max()** : Trouver la valeur maximale.
- **group_by()** : Regrouper les résultats par une colonne.
- **having()** : Filtrer les groupes (comme WHERE mais pour les groupes).
- **label("nom")** : Donner un nom à une colonne calculée.

## Patterns et bonnes pratiques

- **Repository Pattern** : Couche qui encapsule toutes les opérations de base de données pour une entité. Sépare la logique métier de l'accès aux données.

- **Unit of Work** : Pattern où les modifications sont accumulées puis envoyées en une fois. C'est ce que fait la Session SQLAlchemy.

- **Transaction** : Groupe d'opérations qui réussit en totalité ou échoue en totalité. COMMIT = sauvegarder, ROLLBACK = annuler.

- **Context Manager** : Le pattern `with` en Python qui garantit la fermeture automatique des ressources (sessions, fichiers).

- **Soft Delete** : Au lieu de supprimer physiquement une ligne, on marque une date de suppression (colonne `deleted_at`). Permet de conserver l'historique et de restaurer.
