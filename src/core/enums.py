"""Enums for API validation."""

from enum import Enum


class Position(str, Enum):
    """NFL player positions."""

    QB = "QB"
    RB = "RB"
    WR = "WR"
    TE = "TE"
    K = "K"
    DEF = "DEF"
