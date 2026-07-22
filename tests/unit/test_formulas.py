import random
from unittest.mock import patch

from app.game.formulas import *


class TestGetQuality:
    def test_sparkling_at_100(self):
        assert get_quality(100) == "Искрящийся"

    def test_sparkling_above_100(self):
        assert get_quality(120) == "Искрящийся"

    def test_juicy_at_80(self):
        assert get_quality(80) == "Сочный"

    def test_normal_at_60(self):
        assert get_quality(60) == "Обычный"

    def test_withered_below_50(self):
        assert get_quality(30) == "Увядший"

    def test_boundary_juicy_normal(self):
        assert get_quality(79) == "Обычный"
        assert get_quality(80) == "Сочный"


class TestGetHarvestMultiplier:
    def test_zenith(self):
        assert get_harvest_multiplier(95) == 3

    def test_bloom(self):
        assert get_harvest_multiplier(80) == 2

    def test_bud(self):
        assert get_harvest_multiplier(60) == 1


class TestGetStageName:
    def test_seed(self):
        assert get_stage_name(0) == "Семя"

    def test_sprout(self):
        assert get_stage_name(20) == "Росток"

    def test_stem(self):
        assert get_stage_name(40) == "Стебель"

    def test_bud(self):
        assert get_stage_name(60) == "Бутон"

    def test_bloom(self):
        assert get_stage_name(80) == "Цветение"

    def test_mature(self):
        assert get_stage_name(100) == "Зрелость"

class TestGetQualityMultiplier:
    def test_sparkling(self):
        assert get_quality_multiplier("Искрящийся") == 2.0

    def test_juicy(self):
        assert get_quality_multiplier("Сочный") == 1.5

    def test_normal(self):
        assert get_quality_multiplier("Обычный") == 1.0

    def test_withered(self):
        assert get_quality_multiplier("Увядший") == 0.5

    def test_unknown_defaults_to_one(self):
        assert get_quality_multiplier("Неизвестный") == 1.0


class TestCalculateNightEssenceDecay:
    def test_no_decay_if_watered(self):
        assert calculate_night_essence_decay(100, True) == 0

    def test_decay_if_not_watered(self):
        # 20% от 100 = 20
        assert calculate_night_essence_decay(100, False) == 20

    def test_decay_rounds_down(self):
        # 20% от 57 = 11.4 → int = 11
        assert calculate_night_essence_decay(57, False) == 11

    def test_decay_zero_essence(self):
        assert calculate_night_essence_decay(0, False) == 0


class TestCanLevelUp:
    def test_can_level_up_below_100(self):
        assert can_level_up(50) is True

    def test_cannot_level_up_at_100(self):
        assert can_level_up(100) is False

    def test_cannot_level_up_above_100(self):
        assert can_level_up(120) is False


class TestRollBonusDrops:
    def test_zero_essence(self):
        with patch('random.randint', return_value=0):
            assert roll_bonus_drops(0) == 0

    def test_low_essence(self):
        with patch('random.randint', return_value=0):
            assert roll_bonus_drops(25) == 1

    def test_high_essence(self):
        with patch('random.randint', return_value=2):
            assert roll_bonus_drops(100) == 6

    def test_dice_adds_variability(self):
        """Проверяем, что кубик реально добавляет значение."""
        results = set()
        for _ in range(20):
            results.add(roll_bonus_drops(100))
        assert len(results) >= 2


class TestRollRareDrop:
    def test_no_rare_with_zero_chance(self):
        with patch('random.random', return_value=0.99):
            assert roll_rare_drop(0, 0) is False

    def test_rare_with_low_random(self):
        with patch('random.random', return_value=0.005):
            assert roll_rare_drop(0, 0) is True

    def test_bonus_from_essence(self):
        with patch('random.random', return_value=0.015):
            assert roll_rare_drop(100, 0) is True

    def test_bonus_from_zenith(self):
        with patch('random.random', return_value=0.015):
            assert roll_rare_drop(0, 95) is True

    def test_perk_adds_10_percent(self):
        with patch('random.random', return_value=0.10):
            assert roll_rare_drop(0, 0, rare_luck_perk=True) is True
            