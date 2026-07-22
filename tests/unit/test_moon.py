from datetime import date
from unittest.mock import patch

from app.game.moon import _days_to_full_moon, get_moon_phase, get_essence_bonus_for_night


class TestDaysToFullMoon:
    def test_full_moon_returns_zero(self):
        assert _days_to_full_moon(0.5) == 0

    def test_new_moon_returns_about_15(self):
        assert 14 <= _days_to_full_moon(0.0) <= 15

    def test_first_quarter_returns_about_7(self):
        assert 6 <= _days_to_full_moon(0.25) <= 7

    def test_after_full_moon_returns_about_22(self):
        assert 21 <= _days_to_full_moon(0.75) <= 22

    def test_almost_full_moon_returns_about_0(self):
        assert 0 <= _days_to_full_moon(0.49) <= 1

    
class TestGetMoonPhase:
    def test_new_moon_on_known_date(self):
        fake_now = date(2000, 1, 6)
        with patch('app.game.moon.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.date.return_value = fake_now
            result = get_moon_phase()

        assert result["name"] == "Новолуние"
        assert result["essence_bonus"] == 0
        assert result["emoji"] == "🌑"

    def test_full_moon_15_days_later(self):
        fake_now = date(2000, 1, 21)
        
        with patch('app.game.moon.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.date.return_value = fake_now
            result = get_moon_phase()

        assert result["essence_bonus"] >= 12
        assert result["name"] in ["Прибывающая", "Полнолуние"]

    def test_phase_has_all_required_keys(self):
        fake_now = date(2000, 1, 6)
        
        with patch('app.game.moon.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.date.return_value = fake_now
            result = get_moon_phase()

        assert "index" in result
        assert "name" in result
        assert "emoji" in result
        assert "essence_bonus" in result
        assert "cycle_position" in result
        assert "days_to_full_moon" in result

class TestGetEssenceBonusForNight:
    def test_new_moon_bonus_is_zero(self):
        assert get_essence_bonus_for_night(date(2000, 1, 6)) == 0

    def test_bonus_is_never_negative(self):
        for d in [
            date(2000, 1, 6),
            date(2000, 1, 10),
            date(2000, 1, 21),
        ]:
            assert get_essence_bonus_for_night(d) >= 0

    def test_bonus_max_is_18(self):
        assert get_essence_bonus_for_night(date(2000, 1, 21)) <= 18
        