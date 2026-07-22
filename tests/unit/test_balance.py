
from app.core import balance


class TestQualityThresholds:
    def test_thresholds_are_in_order(self):
        assert 0 < balance.QUALITY_THRESHOLD_NORMAL
        assert balance.QUALITY_THRESHOLD_NORMAL < balance.QUALITY_THRESHOLD_JUICY
        assert balance.QUALITY_THRESHOLD_JUICY < balance.QUALITY_THRESHOLD_SPARKLING

    def test_quality_names_are_unique(self):
        names = [
            balance.QUALITY_WITHERED,
            balance.QUALITY_NORMAL,
            balance.QUALITY_JUICY,
            balance.QUALITY_SPARKLING,
        ]
        assert len(names) == len(set(names))


class TestStages:
    def test_stages_start_at_zero(self):
        assert balance.STAGES[0][0] == 0

    def test_stages_end_at_100(self):
        assert balance.STAGES[-1][0] == 100

    def test_stages_are_ordered(self):
        thresholds = [s[0] for s in balance.STAGES]
        assert thresholds == sorted(thresholds)

    def test_every_stage_has_name(self):
        for threshold, name in balance.STAGES:
            assert isinstance(name, str)
            assert len(name) > 0


class TestHarvestMultipliers:
    def test_multipliers_increase_with_stage(self):
        assert balance.HARVEST_MULTIPLIER_BUD < balance.HARVEST_MULTIPLIER_BLOOM
        assert balance.HARVEST_MULTIPLIER_BLOOM < balance.HARVEST_MULTIPLIER_ZENITH


class TestRareDrop:
    def test_base_chance_is_positive(self):
        assert balance.RARE_DROP_BASE_CHANCE > 0

    def test_total_chance_not_exceed_100_percent(self):
        total = balance.RARE_DROP_BASE_CHANCE + balance.RARE_DROP_ESSENCE_BONUS + balance.RARE_DROP_ZENITH_BONUS
        assert total < 1.0


class TestBonusWeights:
    def test_all_weights_are_positive(self):
        for rarity, weight in balance.BONUS_RARITY_WEIGHTS.items():
            assert weight > 0, f"Вес для {rarity} должен быть > 0"

    def test_common_is_most_likely(self):
        max_weight = max(balance.BONUS_RARITY_WEIGHTS.values())
        assert balance.BONUS_RARITY_WEIGHTS["common"] == max_weight


class TestPotionEffects:
    def test_all_potions_have_experience(self):
        for name, effect in balance.POTION_EFFECTS.items():
            assert "experience" in effect, f"{name} должно давать experience"
            assert effect["experience"] > 0, f"{name}: experience должен быть > 0"

    def test_potions_are_ordered_by_value(self):
        effects = list(balance.POTION_EFFECTS.values())
        for i in range(len(effects) - 1):
            assert effects[i]["experience"] > 0
            