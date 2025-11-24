from app.schemas.session import SessionInDB


def calculate_session_stats(session: SessionInDB) -> dict:
    total_answers = (
        session.correct_answers + session.incorrect_answers + session.review_answers
    )
    accuracy_percentage = (
        (session.correct_answers / total_answers * 100) if total_answers > 0 else 0.0
    )

    return {
        "total_cards": len(session.card_queue) if session.card_queue else 0,
        "accuracy_percentage": round(accuracy_percentage, 2),
    }
