"""
=============================================================================
 COURS 12 - EXEMPLE DE FICHIER DE MIGRATION
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier montre :
 - La structure d'un fichier de migration Alembic
 - Les fonctions upgrade() et downgrade()
 - Les opérations courantes : create_table, drop_table, add_column, etc.
=============================================================================
"""

# ============================================================================
# EXEMPLE 1 : Créer une table
# ============================================================================

MIGRATION_CREATE_TABLE = '''
"""Créer la table users

Revision ID: 001abc
Revises: (aucune - première migration)
Create Date: 2024-01-15 10:30:00
"""
from alembic import op
import sqlalchemy as sa

# Identifiants de la révision
revision = '001abc'          # ID unique de cette migration
down_revision = None          # ID de la migration précédente (None = première)
branch_labels = None
depends_on = None


def upgrade():
    """Appliquer la migration (avancer)"""

    # Créer la table users
    op.create_table(
        'users',                                              # Nom de la table
        sa.Column('id', sa.Integer(), nullable=False),        # Colonne id
        sa.Column('username', sa.String(50), nullable=False), # Colonne username
        sa.Column('email', sa.String(255), nullable=False),   # Colonne email
        sa.Column('created_at', sa.DateTime(),                # Colonne created_at
                  server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),                        # Clé primaire
        sa.UniqueConstraint('username'),                      # Contrainte unique
        sa.UniqueConstraint('email'),                         # Contrainte unique
    )

    # Créer un index pour accélérer les recherches par email
    op.create_index('ix_users_email', 'users', ['email'])


def downgrade():
    """Annuler la migration (revenir en arrière)"""

    # Supprimer dans l'ordre INVERSE de la création
    op.drop_index('ix_users_email', 'users')
    op.drop_table('users')
'''

# ============================================================================
# EXEMPLE 2 : Ajouter une colonne
# ============================================================================

MIGRATION_ADD_COLUMN = '''
"""Ajouter la colonne bio à users

Revision ID: 002def
Revises: 001abc
Create Date: 2024-01-16 14:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = '002def'
down_revision = '001abc'    # Pointe vers la migration précédente


def upgrade():
    """Ajouter la colonne bio"""
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(),
                                      server_default=sa.text('true'),
                                      nullable=False))


def downgrade():
    """Retirer la colonne bio"""
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'bio')
'''

# ============================================================================
# EXEMPLE 3 : Opérations courantes
# ============================================================================

OPERATIONS_COURANTES = """
=== OPÉRATIONS COURANTES DANS LES MIGRATIONS ===

  TABLES :
    op.create_table('nom', ...)      → Créer une table
    op.drop_table('nom')             → Supprimer une table
    op.rename_table('ancien', 'nouveau')  → Renommer

  COLONNES :
    op.add_column('table', Column('nom', Type()))  → Ajouter
    op.drop_column('table', 'nom')                  → Supprimer
    op.alter_column('table', 'nom', ...)            → Modifier

  INDEX :
    op.create_index('ix_nom', 'table', ['col'])  → Créer
    op.drop_index('ix_nom', 'table')             → Supprimer

  CLÉS ÉTRANGÈRES :
    op.create_foreign_key('fk_nom', 'source', 'cible', ['col'], ['id'])
    op.drop_constraint('fk_nom', 'table')

  DONNÉES :
    op.execute("UPDATE users SET is_active = true")  → SQL brut
"""

# ============================================================================
# AFFICHAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" COURS : Exemples de fichiers de migration Alembic")
    print("=" * 60)

    print("\n--- Exemple 1 : Créer une table ---")
    print(MIGRATION_CREATE_TABLE)

    print("\n--- Exemple 2 : Ajouter une colonne ---")
    print(MIGRATION_ADD_COLUMN)

    print(OPERATIONS_COURANTES)

    print("=" * 60)
    print(" FIN DU COURS 12 (Jour 2)")
    print("=" * 60)
