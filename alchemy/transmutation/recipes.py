import alchemy
from elements import create_fire
from ..potions import strength_potion


def lead_to_gold() -> str:
    return (f"Recipe transmuting Lead to Gold: brew '{alchemy.create_air()}' "
            f"and '{strength_potion()}' mixed with '{create_fire()}'")
