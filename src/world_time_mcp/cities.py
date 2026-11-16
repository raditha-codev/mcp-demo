"""Offline lookup from city names to IANA time zones, backed by GeoNames data."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from zoneinfo import ZoneInfo, available_timezones

import geonamescache


@dataclass(frozen=True)
class City:
    name: str
    country_code: str
    country: str
    region_code: str
    timezone: str
    population: int
    latitude: float
    longitude: float

    @property
    def label(self) -> str:
        if self.country_code == "US":
            return f"{self.name}, {self.region_code}, {self.country}"
        return f"{self.name}, {self.country}"


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return " ".join(stripped.casefold().replace("-", " ").split())


@lru_cache(maxsize=1)
def _data() -> tuple[dict[str, list[City]], dict[str, str], dict[str, str]]:
    gc = geonamescache.GeonamesCache()
    countries = gc.get_countries()
    country_names = {code: info["name"] for code, info in countries.items()}

    index: dict[str, list[City]] = {}
    for raw in gc.get_cities().values():
        city = City(
            name=raw["name"],
            country_code=raw["countrycode"],
            country=country_names.get(raw["countrycode"], raw["countrycode"]),
            region_code=raw["admin1code"],
            timezone=raw["timezone"],
            population=raw["population"],
            latitude=raw["latitude"],
            longitude=raw["longitude"],
        )
        keys = {_normalize(raw["name"])} | {_normalize(a) for a in raw["alternatenames"]}
        for key in keys:
            if key:
                index.setdefault(key, []).append(city)

    for matches in index.values():
        matches.sort(key=lambda c: c.population, reverse=True)

    country_aliases = {_normalize(name): code for code, name in country_names.items()}
    country_aliases.update({code.casefold(): code for code in countries})
    country_aliases.update({info["iso3"].casefold(): code for code, info in countries.items()})
    country_aliases.update({"usa": "US", "uk": "GB", "united states of america": "US"})

    us_states = {code.casefold(): code for code in gc.get_us_states()}
    us_states.update({_normalize(s["name"]): code for code, s in gc.get_us_states().items()})
    return index, country_aliases, us_states


@lru_cache(maxsize=1)
def _timezones() -> dict[str, str]:
    return {tz.casefold(): tz for tz in available_timezones()}


def timezone_from_name(query: str) -> str | None:
    """Return the canonical IANA zone name if `query` already is one (e.g. "Asia/Colombo", "UTC")."""
    return _timezones().get(query.strip().casefold())


def find_cities(query: str, limit: int = 5) -> list[City]:
    """Find cities matching `query`, largest first.

    `query` may include a qualifier after a comma, e.g. "Paris, US", "Paris, Texas",
    "London, Canada" or "Portland, OR".
    """
    index, country_aliases, us_states = _data()
    name, _, qualifier = query.partition(",")
    matches = index.get(_normalize(name), [])

    qualifier = _normalize(qualifier)
    if qualifier:
        country = country_aliases.get(qualifier)
        state = us_states.get(qualifier)
        matches = [
            c
            for c in matches
            if c.country_code == country or (c.country_code == "US" and c.region_code == state)
        ]
    return matches[:limit]


def resolve(query: str) -> tuple[str, City | None]:
    """Resolve a city name or IANA zone name to `(timezone, city)`.

    Raises `ValueError` when nothing matches.
    """
    if not query or not query.strip():
        raise ValueError("Please provide a city name, e.g. 'Colombo' or 'Paris, France'.")

    tz = timezone_from_name(query)
    if tz:
        return tz, None

    matches = find_cities(query, limit=1)
    if not matches:
        raise ValueError(
            f"Unknown city {query!r}. Try adding a country (e.g. 'Springfield, US'), "
            "use a larger nearby city, or pass an IANA time zone like 'Europe/Paris'."
        )
    city = matches[0]
    ZoneInfo(city.timezone)
    return city.timezone, city
