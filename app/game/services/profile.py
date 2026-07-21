import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core import config
from app.core import balance

from app.game import formulas
from app.game.utils import format_dt
from app.game.moon import get_essence_bonus_for_night, get_moon_phase

from app.models.garden_bed import GardenBed
from app.models.inventory import Inventory
from app.models.item import Item
from app.models.plant import Plant
from app.models.player import Player

from app.models.recipe import Recipe
from app.models.level_reward import LevelReward
from app.models.perk import Perk

def get_player_profile(db: Session, player_id: int) -> dict:
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise ValueError("Игрок не найден")

    # Ближайшая награда
    next_reward = db.query(LevelReward).filter(
        LevelReward.level > player.level
    ).order_by(LevelReward.level.asc()).first()

    # Полученные перки
    perks = db.query(Perk).filter(Perk.player_id == player_id).all()

    return {
        "nickname": player.nickname,
        "level": player.level,
        "experience": player.experience,
        "experience_to_next": player.experience_to_next,
        "xp_progress": player.xp_progress_percent,
        "title": player.title_display,
        "coins": player.coins,
        "total_harvests": player.total_harvests,
        "total_potions_brewed": player.total_potions_brewed,
        "total_coins_earned": player.total_coins_earned,
        "total_moon_baths": player.total_moon_baths,
        "days_in_game": player.days_in_game,
        "next_reward_level": next_reward.level if next_reward else None,
        "next_reward_name": next_reward.reward_name if next_reward else "Максимальный уровень!",
        "perks": [{"name": p.perk_name, "description": p.description} for p in perks],
    }


def use_potion(db: Session, player_id: int, inventory_id: int) -> dict:
    """Использовать зелье из инвентаря."""
    inv = db.query(Inventory).filter(
        Inventory.id == inventory_id,
        Inventory.player_id == player_id,
        Inventory.quantity > 0
    ).first()
    if not inv:
        raise ValueError("Предмет не найден")
    if inv.item.item_type != "potion":
        raise ValueError("Это не зелье!")

    potion_name = inv.item.name
    effects = balance.POTION_EFFECTS.get(potion_name, {"experience": 30})

    # Тратим зелье
    inv.quantity -= 1
    if inv.quantity <= 0:
        db.delete(inv)

    # Начисляем опыт
    experience_gained = effects["experience"]
    player = db.query(Player).filter(Player.id == player_id).first()
    player.experience += experience_gained
    player.total_potions_brewed += 1

    # Проверяем левел-ап
    leveled_up = False
    while player.experience >= player.experience_to_next:
        player.experience -= player.experience_to_next
        player.level += 1
        player.experience_to_next = int(player.experience_to_next * 1.2)
        leveled_up = True

        # Выдаём награду
        reward = db.query(LevelReward).filter(LevelReward.level == player.level).first()
        if reward:
            if reward.reward_type == "coins":
                player.coins += reward.reward_value
            elif reward.reward_type == "perk":
                existing = db.query(Perk).filter(
                    Perk.player_id == player_id, Perk.perk_code == reward.reward_code
                ).first()
                if not existing:
                    perk = Perk(player_id=player_id, perk_code=reward.reward_code,
                                perk_name=reward.reward_name, description=reward.description)
                    db.add(perk)
            elif reward.reward_type == "title":
                player.title = reward.reward_name

    db.commit()
    return {
        "potion_name": potion_name,
        "experience_gained": experience_gained,
        "new_experience": player.experience,
        "experience_to_next": player.experience_to_next,
        "level": player.level,
        "leveled_up": leveled_up
    }


def has_perk(db: Session, player_id: int, perk_code: str) -> bool:    
   """Проверяет, есть ли у игрока активный перк."""
    perk = db.query(Perk).filter(
        Perk.player_id == player_id,
        Perk.perk_code == perk_code,
        Perk.is_active == True
    ).first()
    return perk is not None

def get_max_beds(db: Session, player_id: int) -> int:
    base = balance.MAX_BEDS_PER_PLAYER
    if has_perk(db, player_id, "extra_bed"):
        base += 1
    return base

def add_experience(db: Session, player_id: int, amount: int, reason: str = "") -> Player:
    """Начисляет experience игроку, проверяет левел-ап."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        return None

    player.experience += amount

    # Проверяем левел-ап
    leveled_up = False
    while player.experience >= player.experience_to_next:
        player.experience -= player.experience_to_next
        player.level += 1
        player.experience = int(player.experience_to_next * 1.2)  # +20% XP за каждый уровень
        leveled_up = True

        # Выдаём награду за уровень
        reward = db.query(LevelReward).filter(LevelReward.level == player.level).first()
        if reward:
            if reward.reward_type == "coins":
                player.coins += reward.reward_value
            elif reward.reward_type == "perk":
                # Проверяем, есть ли уже такой перк
                existing = db.query(Perk).filter(
                    Perk.player_id == player_id,
                    Perk.perk_code == reward.reward_code
                ).first()
                if not existing:
                    perk = Perk(player_id=player_id, perk_code=reward.reward_code,
                                perk_name=reward.reward_name, description=reward.description)
                    db.add(perk)
            elif reward.reward_type == "title":
                player.title = reward.reward_name
            elif reward.reward_type == "unlock_recipe":
                pass  # Рецепты уже открыты всем, просто нотификация

    db.commit()
    return player
    