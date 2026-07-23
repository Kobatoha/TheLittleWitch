"""Единое исключение игры с кодами ошибок."""

from enum import Enum


class ErrorCode(str, Enum):
    """Коды ошибок. Ключ — machine-readable, значение — HTTP-статус."""

    # 404 — Не найдено
    PLAYER_NOT_FOUND = "PLAYER_NOT_FOUND"
    BED_NOT_FOUND = "BED_NOT_FOUND"
    PLANT_NOT_FOUND = "PLANT_NOT_FOUND"
    RECIPE_NOT_FOUND = "RECIPE_NOT_FOUND"
    ITEM_NOT_FOUND_IN_DB = "ITEM_NOT_FOUND_IN_DB"

    # 400 — Неверный запрос
    BED_EMPTY = "BED_EMPTY"
    PLANT_DEAD = "PLANT_DEAD"
    PLANT_RECOVERING = "PLANT_RECOVERING"
    PLANT_ALREADY_MATURE = "PLANT_ALREADY_MATURE"
    PLANT_NOT_READY = "PLANT_NOT_READY"
    MAX_BEDS_REACHED = "MAX_BEDS_REACHED"
    WATER_ALREADY_USED = "WATER_ALREADY_USED"
    CLEAN_ALREADY_USED = "CLEAN_ALREADY_USED"
    MOON_BATH_ALREADY_USED = "MOON_BATH_ALREADY_USED"
    MOON_TOO_WEAK = "MOON_TOO_WEAK"
    NO_GROWTH_SPARK = "NO_GROWTH_SPARK"
    NOT_ENOUGH_ITEMS = "NOT_ENOUGH_ITEMS"
    NOT_POTION = "NOT_POTION"
    MISSING_INGREDIENT = "MISSING_INGREDIENT"
    BREW_FAILED = "BREW_FAILED"
    INVENTORY_ITEM_NOT_FOUND = "INVENTORY_ITEM_NOT_FOUND"

    # 500 — Внутренняя ошибка
    SPARK_ITEM_NOT_FOUND = "SPARK_ITEM_NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"

    @property
    def http_status(self) -> int:
        """HTTP-статус по коду ошибки."""
        mapping = {
            404: ["PLAYER_NOT_FOUND", "BED_NOT_FOUND", "PLANT_NOT_FOUND",
                  "RECIPE_NOT_FOUND", "ITEM_NOT_FOUND_IN_DB"],
            400: ["BED_EMPTY", "PLANT_DEAD", "PLANT_RECOVERING", "PLANT_ALREADY_MATURE",
                  "PLANT_NOT_READY", "MAX_BEDS_REACHED", "WATER_ALREADY_USED",
                  "CLEAN_ALREADY_USED", "MOON_BATH_ALREADY_USED", "MOON_TOO_WEAK",
                  "NO_GROWTH_SPARK", "NOT_ENOUGH_ITEMS", "NOT_POTION",
                  "MISSING_INGREDIENT", "BREW_FAILED", "INVENTORY_ITEM_NOT_FOUND"],
            500: ["SPARK_ITEM_NOT_FOUND", "INTERNAL_ERROR"],
        }
        for status, codes in mapping.items():
            if self.value in codes:
                return status
        return 500


class GameError(Exception):
    """Единое исключение для всех игровых ошибок."""

    def __init__(
            self,
            code: ErrorCode,
            message: str = "",
            details: str = "",
    ):
        self.code = code
        self.message = message or code.value
        self.details = details
        self.http_status = code.http_status
        super().__init__(self.message)
