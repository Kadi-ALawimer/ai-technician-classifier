"""
Shared enums for request classification.

These are the single source of truth for the allowed category and priority
values. Both the database model and the API schemas import from here, so
there is no risk of the two drifting apart (e.g. frontend/backend agreeing
on "ac" in one place and "AC" in another).
"""
from enum import Enum


class Category(str, Enum):
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    CARPENTRY = "carpentry"
    AC = "ac"
    INSULATION = "insulation"
    FLOORING = "flooring"
    OTHER = "other"


class Priority(str, Enum):
    NORMAL = "normal"
    URGENT = "urgent"
