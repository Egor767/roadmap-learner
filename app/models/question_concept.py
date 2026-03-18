from .base import Base
from .mixins import ConceptRelationMixin, QuestionRelationMixin


class QuestionConcept(Base, QuestionRelationMixin, ConceptRelationMixin):
    __tablename__ = "question_concept"

    _question_id_primary_key = True
    _concept_id_primary_key = True

    def __str__(self):
        return f"{self.__class__.__name__}(question={self.question_id}, concept={self.concept_id})"

    def __repr__(self):
        return str(self)
