"""
=============================================================================
 TP 2 JOUR 2 - API BIBLIOTHÈQUE COMPLÈTE (1h30)
 Formation SQLAlchemy 2.0 - Jour 2
=============================================================================

 OBJECTIF :
   Créer une API REST complète de gestion de bibliothèque avec FastAPI.

 MODÈLES :
   - Author : id, name, bio, birth_year
   - Book   : id, title, isbn (unique), published_year, stock
              Relation N-1 avec Author
   - Member : id, name, email (unique), membership_date
   - Loan   : Association Object
              member_id, book_id, loan_date, return_date, returned (bool)

 ENDPOINTS :
   POST   /authors/             → Créer auteur
   GET    /authors/{id}         → Auteur avec ses livres
   POST   /books/               → Créer livre (avec author_id)
   GET    /books/               → Lister (filtre par auteur, année)
   GET    /books/available      → Livres disponibles (stock > 0)
   POST   /loans/               → Emprunter (décrémenter stock)
   PATCH  /loans/{id}/return    → Retourner (incrémenter stock)
   GET    /members/{id}/loans   → Emprunts d'un membre

 CONTRAINTES :
   - Pas d'emprunt si stock = 0
   - Un membre ne peut pas emprunter 2 fois le même livre non retourné
   - Utiliser eager loading pour éviter N+1

 INDICATIONS :
   - selectinload(Author.books) pour charger les livres
   - Vérifier stock avant emprunt
   - pip install fastapi uvicorn sqlalchemy
=============================================================================
"""

# TODO : Implémenter les modèles, schémas, et endpoints
# Voir la solution pour l'implémentation complète

print("TP 2 Jour 2 : API Bibliothèque")
print("Consultez le fichier solution.py pour l'implémentation complète")
print("Essayez d'abord de le faire vous-même !")
