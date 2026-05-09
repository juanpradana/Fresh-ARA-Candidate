from app.backend.services.screening.service import passes_fresh_filter


def test_fresh_filter_requires_min_five_days_since_last_ara():
    assert passes_fresh_filter(4) is False
    assert passes_fresh_filter(5) is True
    assert passes_fresh_filter(999) is True
