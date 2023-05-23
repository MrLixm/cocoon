__all__ = ("ColorspaceCategory",)

import enum


class ColorspaceCategory(enum.Enum):
    """
    A colorspace can belong to multiple of those category. And a categoryc oudl be a child
    of another category, but this is defined at the editor level.
    """

    aces = "ACES"
    camera = "Camera"
    p3 = "P3 Family"
    common = "Common"
    working_space = "Working Space"
    special = "Special"
