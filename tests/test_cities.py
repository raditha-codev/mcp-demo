import pytest

from world_time_mcp import cities


@pytest.mark.parametrize(
    ("query", "timezone", "country"),
    [
        ("Colombo", "Asia/Colombo", "LK"),
        ("london", "Europe/London", "GB"),
        ("New York", "America/New_York", "US"),
        ("Sao Paulo", "America/Sao_Paulo", "BR"),
        ("São Paulo", "America/Sao_Paulo", "BR"),
        ("Bombay", "Asia/Kolkata", "IN"),
    ],
)
def test_resolve_picks_largest_city(query, timezone, country):
    tz, city = cities.resolve(query)
    assert tz == timezone
    assert city is not None and city.country_code == country


@pytest.mark.parametrize(
    ("query", "timezone"),
    [
        ("London, Canada", "America/Toronto"),
        ("London, CA", "America/Toronto"),
        ("Paris, Texas", "America/Chicago"),
        ("Portland, OR", "America/Los_Angeles"),
        ("Colombo, Brazil", "America/Sao_Paulo"),
    ],
)
def test_resolve_with_qualifier(query, timezone):
    assert cities.resolve(query)[0] == timezone


def test_resolve_accepts_iana_zone():
    assert cities.resolve("asia/tokyo") == ("Asia/Tokyo", None)
    assert cities.resolve("UTC") == ("UTC", None)


@pytest.mark.parametrize("query", ["", "   ", "Notarealcityxyz"])
def test_resolve_rejects_unknown(query):
    with pytest.raises(ValueError):
        cities.resolve(query)


def test_find_cities_lists_ambiguous_matches():
    matches = cities.find_cities("Paris", limit=10)
    assert matches[0].country_code == "FR"
    assert any(c.country_code == "US" for c in matches)
