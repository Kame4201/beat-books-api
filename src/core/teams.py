"""Canonical NFL team definitions."""

from enum import Enum


class NFLTeam(str, Enum):
    """All 32 NFL teams."""

    CARDINALS = "cardinals"
    FALCONS = "falcons"
    RAVENS = "ravens"
    BILLS = "bills"
    PANTHERS = "panthers"
    BEARS = "bears"
    BENGALS = "bengals"
    BROWNS = "browns"
    COWBOYS = "cowboys"
    BRONCOS = "broncos"
    LIONS = "lions"
    PACKERS = "packers"
    TEXANS = "texans"
    COLTS = "colts"
    JAGUARS = "jaguars"
    CHIEFS = "chiefs"
    RAIDERS = "raiders"
    CHARGERS = "chargers"
    RAMS = "rams"
    DOLPHINS = "dolphins"
    VIKINGS = "vikings"
    PATRIOTS = "patriots"
    SAINTS = "saints"
    GIANTS = "giants"
    JETS = "jets"
    EAGLES = "eagles"
    STEELERS = "steelers"
    NINERS = "49ers"
    SEAHAWKS = "seahawks"
    BUCCANEERS = "buccaneers"
    TITANS = "titans"
    COMMANDERS = "commanders"


VALID_NFL_TEAMS: frozenset[str] = frozenset(t.value for t in NFLTeam)
