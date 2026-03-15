"""
=============================================================================
 COURS 11 - COMMANDES ALEMBIC ESSENTIELLES
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier est un AIDE-MÉMOIRE de toutes les commandes Alembic.
 À garder sous la main quand vous travaillez avec les migrations !
=============================================================================
"""

# ============================================================================
# COMMANDES ALEMBIC - AIDE-MÉMOIRE
# ============================================================================

COMMANDES = """
╔══════════════════════════════════════════════════════════════════════╗
║                    COMMANDES ALEMBIC                                ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  INITIALISATION                                                      ║
║  ─────────────                                                       ║
║  alembic init alembic                                                ║
║    → Créer la structure Alembic dans le projet                       ║
║                                                                      ║
║  CRÉER UNE MIGRATION                                                 ║
║  ───────────────────                                                 ║
║  alembic revision --autogenerate -m "description"                    ║
║    → Détecte automatiquement les changements dans vos modèles        ║
║    → Génère un fichier de migration avec upgrade() et downgrade()    ║
║    → TOUJOURS vérifier le fichier généré !                           ║
║                                                                      ║
║  alembic revision -m "migration manuelle"                            ║
║    → Créer une migration VIDE (à remplir soi-même)                   ║
║    → Utile pour les opérations que l'auto-détection ne gère pas      ║
║                                                                      ║
║  APPLIQUER LES MIGRATIONS                                            ║
║  ────────────────────────                                            ║
║  alembic upgrade head                                                ║
║    → Appliquer TOUTES les migrations en attente                      ║
║    → "head" = la dernière migration disponible                       ║
║                                                                      ║
║  alembic upgrade +1                                                  ║
║    → Appliquer UNE SEULE migration (la prochaine)                    ║
║                                                                      ║
║  alembic upgrade abc123                                              ║
║    → Appliquer jusqu'à une révision spécifique                       ║
║                                                                      ║
║  REVENIR EN ARRIÈRE                                                  ║
║  ──────────────────                                                  ║
║  alembic downgrade -1                                                ║
║    → Annuler la DERNIÈRE migration                                   ║
║                                                                      ║
║  alembic downgrade abc123                                            ║
║    → Revenir à une révision spécifique                               ║
║                                                                      ║
║  alembic downgrade base                                              ║
║    → Annuler TOUTES les migrations (retour à zéro)                   ║
║                                                                      ║
║  INFORMATIONS                                                        ║
║  ────────────                                                        ║
║  alembic current                                                     ║
║    → Voir la migration actuellement appliquée                        ║
║                                                                      ║
║  alembic history                                                     ║
║    → Voir l'historique de toutes les migrations                      ║
║                                                                      ║
║  alembic heads                                                       ║
║    → Voir les migrations en attente (pas encore appliquées)          ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  BONNES PRATIQUES                                                    ║
║  ────────────────                                                    ║
║  1. TOUJOURS tester le downgrade avant de pusher                     ║
║  2. Petites migrations : 1 changement = 1 migration                  ║
║  3. Ne JAMAIS modifier une migration déjà en production              ║
║  4. TOUJOURS relire les migrations auto-générées                     ║
║  5. Nommer les migrations de façon descriptive                       ║
║     → "add_users_table" plutôt que "update_1"                        ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

# ============================================================================
# WORKFLOW TYPIQUE
# ============================================================================

WORKFLOW = """
=== WORKFLOW TYPIQUE ===

  1. Modifier vos modèles Python (ajouter/modifier une colonne, etc.)

  2. Générer la migration :
     alembic revision --autogenerate -m "add bio column to users"

  3. Vérifier le fichier généré dans alembic/versions/
     → L'auto-détection n'est pas parfaite !
     → Vérifiez que upgrade() et downgrade() sont corrects

  4. Appliquer la migration :
     alembic upgrade head

  5. Tester que tout fonctionne

  6. Commiter dans Git :
     git add alembic/versions/xxx_add_bio_column.py
     git commit -m "migration: add bio column to users"
"""

if __name__ == "__main__":
    print(COMMANDES)
    print(WORKFLOW)
    print("=" * 60)
    print(" FIN DU COURS 11 (Jour 2)")
    print("=" * 60)
