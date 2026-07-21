from sqlalchemy.orm import Session

from app.models.care_log import CareLog


def log_action(
    db: Session, 
    player_id: int, 
    bed_id: int, 
    action: str, 
    action_name: str, 
    effect: str, 
    mood: str = "neutral", 
    details: str = None
    ) -> None:
    """Записывает действие в лог ухода."""
    log = CareLog(
        garden_bed_id=bed_id,
        player_id=player_id,
        action=action,
        action_name=action_name,
        effect=effect,
        mood=mood,
        details=details
    )
    db.add(log)
    db.commit()
