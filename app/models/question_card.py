from .base import Base
from .mixins import CardRelationMixin, QuestionRelationMixin


class QuestionCard(Base, QuestionRelationMixin, CardRelationMixin):
    __tablename__ = "question_card"

    _question_id_primary_key = True
    _card_id_primary_key = True

    def __str__(self):
        return f"{self.__class__.__name__}(question={self.question_id}, card={self.card_id})"

    def __repr__(self):
        return str(self)
