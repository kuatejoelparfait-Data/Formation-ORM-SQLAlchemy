# LEXIQUE - Jour 2 : Relations et Optimisations

## Relations entre tables

- **Relation One-to-Many (1-N)** : Un parent a plusieurs enfants. Ex: 1 User → N Articles. L'enfant a la clé étrangère (`author_id`).

- **Relation Many-to-One (N-1)** : L'inverse de 1-N, vu du côté de l'enfant. Ex: 1 Article → 1 User (auteur).

- **Relation Many-to-Many (N-N)** : Plusieurs objets liés à plusieurs autres. Ex: Articles ↔ Tags. Nécessite une table d'association.

- **relationship()** : Fonction SQLAlchemy qui crée un lien navigable entre deux classes Python. Permet d'accéder aux objets liés comme des attributs.

- **back_populates** : Paramètre qui crée une relation bidirectionnelle. Si User a `articles` avec `back_populates="author"`, alors Article a `author` avec `back_populates="articles"`.

- **backref** : Alternative plus ancienne à `back_populates`. Crée automatiquement la relation inverse. Moins explicite, donc moins recommandé.

- **ForeignKey** : Clé étrangère. Colonne qui référence la clé primaire d'une autre table. `ForeignKey("users.id")` pointe vers la table users.

## Cascade

- **cascade** : Paramètre qui définit ce qui arrive aux enfants quand on agit sur le parent.

- **save-update** : Quand on ajoute le parent à la session, les enfants sont aussi ajoutés automatiquement. Inclus par défaut.

- **delete** : Quand on supprime le parent, les enfants sont aussi supprimés.

- **delete-orphan** : Quand un enfant est retiré de la liste du parent (détaché), il est supprimé.

- **all** : Raccourci pour `save-update + merge + delete`.

- **"all, delete-orphan"** : La cascade COMPLÈTE recommandée pour les relations 1-N fortes (ex: User → Articles). Supprime tout en cascade + les orphelins.

## Relations N-N

- **Table d'association** : Table intermédiaire pour les relations N-N. Contient deux clés étrangères formant une clé primaire composite. Créée avec `Table()`.

- **secondary** : Paramètre de `relationship()` qui indique quelle table d'association utiliser pour une relation N-N.

- **Association Object** : Quand la relation N-N a ses propres données (ex: note, date d'inscription). On crée une classe Python pour la table intermédiaire au lieu d'un simple `Table`.

## Problème N+1 et Loading

- **Problème N+1** : Le piège #1 des ORM. Quand l'accès aux relations dans une boucle génère une requête SQL par élément. 100 users = 101 requêtes au lieu de 2.

- **Lazy Loading** : Comportement par défaut. Les relations sont chargées à la demande (quand on y accède). Cause le N+1 si utilisé dans une boucle.

- **Eager Loading** : Charger les relations EN MÊME TEMPS que l'objet principal, en une ou deux requêtes. La solution au N+1.

- **joinedload** : Stratégie d'eager loading qui fait un JOIN SQL. 1 seule requête. Bien pour les relations 1-1 et les petites collections.

- **selectinload** : Stratégie d'eager loading qui fait 2 requêtes (SELECT + WHERE IN). RECOMMANDÉ pour les collections 1-N. Pas de duplication de données.

- **subqueryload** : Stratégie d'eager loading qui fait 2 requêtes avec sous-requête. Bien pour les requêtes paginées.

- **.options()** : Méthode pour ajouter des options de chargement à une requête. Ex: `select(User).options(selectinload(User.articles))`.

- **.unique()** : Méthode nécessaire avec `joinedload` pour dédupliquer les résultats causés par le JOIN.

## Migrations avec Alembic

- **Migration** : Fichier qui décrit un changement de schéma de base de données (ajouter une table, une colonne, etc.). Permet de versionner le schéma.

- **Alembic** : Outil officiel de migration pour SQLAlchemy. Gère l'historique des changements de schéma.

- **alembic init** : Commande pour initialiser Alembic dans un projet. Crée le dossier `alembic/` avec `env.py` et `versions/`.

- **alembic revision** : Créer un nouveau fichier de migration. Avec `--autogenerate` pour détecter automatiquement les changements.

- **alembic upgrade** : Appliquer les migrations. `upgrade head` = appliquer toutes. `upgrade +1` = une seule.

- **alembic downgrade** : Revenir en arrière. `downgrade -1` = annuler la dernière. `downgrade base` = tout annuler.

- **alembic current** : Voir quelle migration est actuellement appliquée.

- **alembic history** : Voir l'historique de toutes les migrations.

- **--autogenerate** : Option qui détecte automatiquement les différences entre vos modèles Python et la base de données.

- **op.create_table / op.drop_table** : Opérations Alembic pour créer/supprimer une table.

- **op.add_column / op.drop_column** : Opérations pour ajouter/supprimer une colonne.

- **op.create_index / op.drop_index** : Opérations pour créer/supprimer un index.

- **revision / down_revision** : Identifiants dans un fichier de migration. `revision` = ID de cette migration. `down_revision` = ID de la migration précédente.

- **upgrade()** : Fonction dans un fichier de migration qui APPLIQUE le changement (avancer).

- **downgrade()** : Fonction qui ANNULE le changement (reculer).

## Intégration FastAPI

- **FastAPI** : Framework Python moderne pour créer des APIs REST. Très rapide, avec validation automatique et documentation interactive.

- **Pydantic** : Bibliothèque de validation de données utilisée par FastAPI. Vérifie automatiquement les types et formats.

- **BaseModel** : Classe de base Pydantic pour définir des schémas de données.

- **ConfigDict(from_attributes=True)** : Configuration Pydantic qui permet de convertir un objet SQLAlchemy en schéma Pydantic automatiquement.

- **Depends** : Système d'injection de dépendances de FastAPI. `Depends(get_db)` injecte une session de base de données dans chaque endpoint.

- **APIRouter** : Objet FastAPI pour organiser les endpoints par thème (users, articles, etc.).

- **HTTPException** : Exception FastAPI pour retourner des erreurs HTTP avec un code de statut et un message.

- **Codes HTTP courants** :
  - `200 OK` : Requête réussie
  - `201 Created` : Ressource créée
  - `204 No Content` : Suppression réussie
  - `400 Bad Request` : Données invalides
  - `404 Not Found` : Ressource non trouvée

- **response_model** : Paramètre des endpoints qui définit le schéma de réponse. FastAPI filtre automatiquement les champs.

- **model_dump(exclude_unset=True)** : Méthode Pydantic qui retourne un dictionnaire avec SEULEMENT les champs fournis par le client (pour les mises à jour partielles).

- **get_db** : Fonction de dépendance qui fournit une session de base de données à chaque requête HTTP. Utilise le pattern `yield` pour garantir la fermeture.

- **Schéma de création** : Schéma Pydantic pour les données d'entrée (POST). Ex: `UserCreate` avec username, email, password.

- **Schéma de réponse** : Schéma Pydantic pour les données de sortie. Ex: `UserResponse` SANS le mot de passe.

- **Schéma de mise à jour** : Schéma Pydantic avec tous les champs optionnels. Ex: `UserUpdate` où chaque champ a `| None = None`.
