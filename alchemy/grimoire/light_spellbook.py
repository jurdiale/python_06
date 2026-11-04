def light_spell_allowed_ingredients() -> list[str]:
    return ["earth", "air", "fire", "water"]


def light_spell_record(spell_name: str, ingredients: str) -> str:
    # Late import: the validator is only loaded when the function is called,
    # when light_spellbook is already fully initialised (no circular import).
    from .light_validator import validate_ingredients

    result = validate_ingredients(ingredients)
    if result.endswith("INVALID"):
        return f"Spell rejected: {spell_name} ({result})"
    return f"Spell recorded: {spell_name} ({result})"
