"""
=============================================================================
 TP 2 JOUR 2 - SOLUTION : API Bibliothèque complète
 Formation SQLAlchemy 2.0 - Jour 2

 Pour lancer :
   pip install fastapi uvicorn sqlalchemy
   python solution.py
   → Ouvrir http://127.0.0.1:8000/docs
=============================================================================
"""

from datetime import datetime, date
from typing import List, Optional, Generator
from decimal import Decimal

from sqlalchemy import (
    create_engine, String, Text, Integer, Boolean, Date, DateTime,
    ForeignKey, func, select
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column,
    relationship, Session, sessionmaker, selectinload
)
from pydantic import BaseModel, ConfigDict

# ============================================================================
# 1. BASE DE DONNÉES
# ============================================================================

engine = create_engine("sqlite:///./bibliotheque.db", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# ============================================================================
# 2. MODÈLES SQLALCHEMY
# ============================================================================

class Author(Base):
    """Auteur de livres"""
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    birth_year: Mapped[Optional[int]] = mapped_column(Integer)

    # Relation 1-N avec Book
    books: Mapped[List["Book"]] = relationship(back_populates="author")

    def __repr__(self) -> str:
        return f"Author(id={self.id}, name={self.name!r})"


class Book(Base):
    """Livre de la bibliothèque"""
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    isbn: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    published_year: Mapped[Optional[int]] = mapped_column(Integer)
    stock: Mapped[int] = mapped_column(Integer, default=1)

    # Clé étrangère vers Author
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship(back_populates="books")

    # Relation 1-N avec Loan
    loans: Mapped[List["Loan"]] = relationship(back_populates="book")

    def __repr__(self) -> str:
        return f"Book(id={self.id}, title={self.title!r}, stock={self.stock})"


class Member(Base):
    """Membre de la bibliothèque"""
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    membership_date: Mapped[date] = mapped_column(Date, server_default=func.current_date())

    # Relation 1-N avec Loan
    loans: Mapped[List["Loan"]] = relationship(back_populates="member")

    def __repr__(self) -> str:
        return f"Member(id={self.id}, name={self.name!r})"


class Loan(Base):
    """Emprunt de livre (Association Object)"""
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    loan_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    return_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    returned: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relations
    member: Mapped["Member"] = relationship(back_populates="loans")
    book: Mapped["Book"] = relationship(back_populates="loans")

    def __repr__(self) -> str:
        status = "retourné" if self.returned else "en cours"
        return f"Loan(id={self.id}, book={self.book_id}, member={self.member_id}, {status})"


# Créer les tables
Base.metadata.create_all(engine)

# ============================================================================
# 3. SCHÉMAS PYDANTIC
# ============================================================================

# --- Author ---
class AuthorCreate(BaseModel):
    name: str
    bio: str | None = None
    birth_year: int | None = None

class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    isbn: str
    published_year: int | None
    stock: int

class AuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    bio: str | None
    birth_year: int | None

class AuthorWithBooks(AuthorResponse):
    books: list[BookResponse] = []

# --- Book ---
class BookCreate(BaseModel):
    title: str
    isbn: str
    published_year: int | None = None
    stock: int = 1
    author_id: int

# --- Member ---
class MemberCreate(BaseModel):
    name: str
    email: str

class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    membership_date: date

# --- Loan ---
class LoanCreate(BaseModel):
    member_id: int
    book_id: int

class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    member_id: int
    book_id: int
    loan_date: datetime
    return_date: datetime | None
    returned: bool

# ============================================================================
# 4. DÉPENDANCE DE SESSION
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# 5. APPLICATION FASTAPI
# ============================================================================

try:
    from fastapi import FastAPI, Depends, HTTPException, status

    app = FastAPI(title="API Bibliothèque", description="Gestion de bibliothèque avec SQLAlchemy")

    # --- AUTEURS ---
    @app.post("/authors/", response_model=AuthorResponse, status_code=201)
    def create_author(data: AuthorCreate, db: Session = Depends(get_db)):
        """Créer un auteur"""
        author = Author(**data.model_dump())
        db.add(author)
        db.commit()
        db.refresh(author)
        return author

    @app.get("/authors/{author_id}", response_model=AuthorWithBooks)
    def get_author(author_id: int, db: Session = Depends(get_db)):
        """Récupérer un auteur avec ses livres"""
        stmt = (
            select(Author)
            .where(Author.id == author_id)
            .options(selectinload(Author.books))  # Eager loading !
        )
        author = db.execute(stmt).scalar_one_or_none()
        if not author:
            raise HTTPException(status_code=404, detail="Auteur non trouvé")
        return author

    # --- LIVRES ---
    @app.post("/books/", response_model=BookResponse, status_code=201)
    def create_book(data: BookCreate, db: Session = Depends(get_db)):
        """Créer un livre"""
        # Vérifier que l'auteur existe
        author = db.get(Author, data.author_id)
        if not author:
            raise HTTPException(status_code=400, detail="Auteur non trouvé")
        book = Book(**data.model_dump())
        db.add(book)
        db.commit()
        db.refresh(book)
        return book

    @app.get("/books/", response_model=list[BookResponse])
    def list_books(
        author_id: int | None = None,
        year: int | None = None,
        skip: int = 0,
        limit: int = 20,
        db: Session = Depends(get_db)
    ):
        """Lister les livres avec filtres optionnels"""
        stmt = select(Book)
        if author_id:
            stmt = stmt.where(Book.author_id == author_id)
        if year:
            stmt = stmt.where(Book.published_year == year)
        stmt = stmt.offset(skip).limit(limit)
        return db.execute(stmt).scalars().all()

    @app.get("/books/available", response_model=list[BookResponse])
    def list_available_books(db: Session = Depends(get_db)):
        """Livres disponibles (stock > 0)"""
        stmt = select(Book).where(Book.stock > 0)
        return db.execute(stmt).scalars().all()

    # --- MEMBRES ---
    @app.post("/members/", response_model=MemberResponse, status_code=201)
    def create_member(data: MemberCreate, db: Session = Depends(get_db)):
        """Créer un membre"""
        member = Member(**data.model_dump())
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @app.get("/members/{member_id}/loans", response_model=list[LoanResponse])
    def get_member_loans(member_id: int, db: Session = Depends(get_db)):
        """Emprunts d'un membre"""
        member = db.get(Member, member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Membre non trouvé")
        stmt = (
            select(Loan)
            .where(Loan.member_id == member_id)
            .order_by(Loan.loan_date.desc())
        )
        return db.execute(stmt).scalars().all()

    # --- EMPRUNTS ---
    @app.post("/loans/", response_model=LoanResponse, status_code=201)
    def create_loan(data: LoanCreate, db: Session = Depends(get_db)):
        """Emprunter un livre"""
        # Vérifier que le livre existe
        book = db.get(Book, data.book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Livre non trouvé")

        # Vérifier le stock
        if book.stock <= 0:
            raise HTTPException(status_code=400, detail="Livre non disponible (stock = 0)")

        # Vérifier pas de double emprunt actif
        existing = db.execute(
            select(Loan).where(
                Loan.member_id == data.member_id,
                Loan.book_id == data.book_id,
                Loan.returned == False
            )
        ).scalar_one_or_none()

        if existing:
            raise HTTPException(status_code=400, detail="Ce membre a déjà emprunté ce livre")

        # Créer l'emprunt et décrémenter le stock
        loan = Loan(member_id=data.member_id, book_id=data.book_id)
        book.stock -= 1
        db.add(loan)
        db.commit()
        db.refresh(loan)
        return loan

    @app.patch("/loans/{loan_id}/return", response_model=LoanResponse)
    def return_loan(loan_id: int, db: Session = Depends(get_db)):
        """Retourner un livre"""
        loan = db.get(Loan, loan_id)
        if not loan:
            raise HTTPException(status_code=404, detail="Emprunt non trouvé")

        if loan.returned:
            raise HTTPException(status_code=400, detail="Livre déjà retourné")

        # Marquer comme retourné et incrémenter le stock
        loan.returned = True
        loan.return_date = datetime.now()
        loan.book.stock += 1
        db.commit()
        db.refresh(loan)
        return loan

    print("  ✓ API Bibliothèque configurée")
    print("  → Lancer : python solution.py")
    print("  → Docs : http://127.0.0.1:8000/docs")

except ImportError:
    print("  ⚠ FastAPI non installé : pip install fastapi uvicorn")
    app = None

# ============================================================================
# LANCEMENT
# ============================================================================

if __name__ == "__main__":
    if app:
        # Insérer des données de test
        with SessionLocal() as session:
            if session.query(Author).count() == 0:
                a1 = Author(name="Victor Hugo", bio="Écrivain français", birth_year=1802)
                a2 = Author(name="Albert Camus", bio="Écrivain et philosophe", birth_year=1913)
                session.add_all([a1, a2])
                session.commit()

                b1 = Book(title="Les Misérables", isbn="978-0-1234-0001", published_year=1862, stock=3, author_id=a1.id)
                b2 = Book(title="Notre-Dame de Paris", isbn="978-0-1234-0002", published_year=1831, stock=2, author_id=a1.id)
                b3 = Book(title="L'Étranger", isbn="978-0-1234-0003", published_year=1942, stock=5, author_id=a2.id)
                session.add_all([b1, b2, b3])

                m1 = Member(name="Alice", email="alice@biblio.com")
                m2 = Member(name="Bob", email="bob@biblio.com")
                session.add_all([m1, m2])
                session.commit()
                print("  ✓ Données de test insérées")

        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8000)
    else:
        print("  Installez FastAPI : pip install fastapi uvicorn")
