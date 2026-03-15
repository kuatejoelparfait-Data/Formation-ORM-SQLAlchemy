"""
=============================================================================
 COURS 06 - ASSOCIATION OBJECT (Données sur la relation)
 Formation SQLAlchemy 2.0 - Jour 2
 Niveau : Débutant (zéro)
=============================================================================

 Ce fichier explique :
 - Quand une relation N-N a ses propres données
 - Le pattern Association Object
 - Exemple : Étudiant ↔ Cours avec note et date d'inscription

 Pour exécuter :
   python cours_06_association_object.py
=============================================================================
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, String, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

# ============================================================================
# QUAND UTILISER UN ASSOCIATION OBJECT ?
# ============================================================================
#
# Table d'association SIMPLE (cours 04) :
#   → Juste deux clés étrangères
#   → Pas de données supplémentaires
#   → Ex: article ↔ tag (juste "lié ou pas")
#
# Association OBJECT :
#   → La relation elle-même a des DONNÉES
#   → Ex: étudiant ↔ cours + note + date d'inscription
#   → Ex: utilisateur ↔ produit + quantité + date d'achat
#   → On crée une CLASSE Python pour la table intermédiaire

class Base(DeclarativeBase):
    pass

# ============================================================================
# L'ASSOCIATION OBJECT : Enrollment (Inscription)
# ============================================================================

class Enrollment(Base):
    """
    Un étudiant s'inscrit à un cours.
    Cette table a ses propres données : date d'inscription et note.

    C'est à la fois :
    - La table de jonction entre Student et Course
    - Un modèle avec ses propres attributs
    """
    __tablename__ = "enrollments"

    # Clés étrangères composites (les deux ensemble = clé primaire)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), primary_key=True
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id"), primary_key=True
    )

    # ---- DONNÉES PROPRES À L'INSCRIPTION ----
    # Ces données n'appartiennent ni à l'étudiant ni au cours
    # Elles appartiennent à la RELATION entre les deux
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    grade: Mapped[Optional[float]] = mapped_column(Float)  # Note (peut être NULL)

    # ---- RELATIONS ----
    student: Mapped["Student"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")

    def __repr__(self) -> str:
        grade_str = f", note={self.grade}" if self.grade else ""
        return f"Enrollment(student_id={self.student_id}, course_id={self.course_id}{grade_str})"


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    # Relation vers les inscriptions (pas directement vers Course)
    enrollments: Mapped[List["Enrollment"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Student(id={self.id}, name={self.name!r})"


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    enrollments: Mapped[List["Enrollment"]] = relationship(
        back_populates="course"
    )

    def __repr__(self) -> str:
        return f"Course(id={self.id}, name={self.name!r})"


# ============================================================================
# DÉMONSTRATION
# ============================================================================

def demo():
    print("=== DÉMONSTRATION : Association Object ===\n")

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Créer étudiants et cours
        alice = Student(name="Alice")
        bob = Student(name="Bob")
        python_course = Course(name="Python Avancé")
        web_course = Course(name="Développement Web")
        db_course = Course(name="Bases de Données")

        session.add_all([alice, bob, python_course, web_course, db_course])
        session.commit()

        # ---- Inscrire des étudiants avec des notes ----
        print("  1. Inscriptions :")
        enrollments = [
            Enrollment(student_id=alice.id, course_id=python_course.id, grade=16.5),
            Enrollment(student_id=alice.id, course_id=web_course.id, grade=14.0),
            Enrollment(student_id=alice.id, course_id=db_course.id),  # Pas de note encore
            Enrollment(student_id=bob.id, course_id=python_course.id, grade=12.0),
            Enrollment(student_id=bob.id, course_id=db_course.id, grade=18.0),
        ]
        session.add_all(enrollments)
        session.commit()
        print("    ✓ 5 inscriptions créées")

        # ---- Afficher les cours d'Alice avec ses notes ----
        print(f"\n  2. Cours de {alice.name} :")
        for enrollment in alice.enrollments:
            grade = f"{enrollment.grade}/20" if enrollment.grade else "pas encore noté"
            print(f"    - {enrollment.course.name} → {grade}")

        # ---- Afficher les étudiants du cours Python ----
        print(f"\n  3. Étudiants en '{python_course.name}' :")
        for enrollment in python_course.enrollments:
            grade = f"{enrollment.grade}/20" if enrollment.grade else "N/A"
            print(f"    - {enrollment.student.name} → {grade}")

        # ---- Mettre à jour une note ----
        print("\n  4. Mise à jour d'une note :")
        # Alice n'a pas de note en BDD → la mettre
        for enrollment in alice.enrollments:
            if enrollment.course_id == db_course.id:
                enrollment.grade = 17.0
                session.commit()
                print(f"    Alice en BDD : note mise à {enrollment.grade}/20")

        # ---- Calculer la moyenne d'Alice ----
        notes = [e.grade for e in alice.enrollments if e.grade is not None]
        moyenne = sum(notes) / len(notes) if notes else 0
        print(f"\n  5. Moyenne d'Alice : {moyenne:.1f}/20")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" DÉMONSTRATION : Association Object")
    print("=" * 60)

    demo()

    print("\n" + "=" * 60)
    print(" FIN DU COURS 06 (Jour 2)")
    print("=" * 60)
