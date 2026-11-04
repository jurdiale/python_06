# python_06 — The Codex: Python's Import Mysteries

## 1. Qué hace el programa

No hay lógica compleja: todas las funciones devuelven strings. Lo que se evalúa es **cómo se importa**. Cada script `ft_*.py` prueba una forma distinta de llegar al mismo código.

Estructura:

```
.
|-- elements.py                  create_fire, create_water
|-- alchemy/
|   |-- __init__.py              qué expone el paquete
|   |-- elements.py              create_earth, create_air
|   |-- potions.py               healing_potion, strength_potion
|   |-- transmutation/
|   |   |-- __init__.py
|   |   `-- recipes.py           lead_to_gold
|   `-- grimoire/
|       |-- __init__.py
|       |-- light_spellbook.py / light_validator.py   (sin ciclo)
|       `-- dark_spellbook.py  / dark_validator.py    (ciclo: explota)
`-- ft_alembic_0..5, ft_distillation_0..1, ft_transmutation_0..2, ft_kaboom_0..1
```

| Parte | Scripts | Qué demuestra |
|---|---|---|
| I Alembic | `ft_alembic_0..5` | `import x` vs `from x import y`; fichero suelto vs paquete; `__init__.py` que expone solo `create_air` |
| II Distillation | `ft_distillation_0..1` | Un módulo que importa de otros; alias en el paquete (`heal`) |
| III Transmutation | `ft_transmutation_0..2` | Import absoluto y relativo en `recipes.py`; subpaquetes |
| IV Kaboom | `ft_kaboom_0..1` | Import circular: cómo evitarlo (light) y cómo explota (dark) |

### Qué hace cada script
- **alembic_0/1:** `elements.py` de la raíz, con `import elements` y con `from elements import create_water`.
- **alembic_2/3:** `alchemy/elements.py`, con `import alchemy.elements` y con `from alchemy.elements import create_air`.
- **alembic_4:** `import alchemy`. `create_air` existe porque `__init__.py` la importa; `create_earth` **no**, así que lanza `AttributeError` (y mypy da un error a propósito).
- **alembic_5:** `from alchemy import create_air`.
- **distillation_0:** `from alchemy import potions`. **distillation_1:** `alchemy.strength_potion()` y `alchemy.heal()`, que es `healing_potion as heal` en el `__init__.py`.
- **transmutation_0/1/2:** `lead_to_gold()` accedido por `alchemy.transmutation.recipes`, por `alchemy.transmutation` y por `alchemy`.
- **kaboom_0:** `import alchemy.grimoire` y graba un hechizo de luz (funciona).
- **kaboom_1:** importa `dark_spellbook` y falla con `ImportError ... most likely due to a circular import` (a propósito).

## 2. Conceptos que hay que saber

1. **Módulo y paquete:** un módulo es un `.py`; un paquete es una carpeta con `__init__.py`. Ese fichero se ejecuta la primera vez que se importa el paquete.
2. **`import x` vs `from x import y`:** el primero trae el módulo (se usa `x.y()`); el segundo trae el nombre directo (`y()`).
3. **`__init__.py` como fachada:** lo que importa ahí es lo que se ve con `import alchemy`. Por eso `create_air` se ve y `create_earth` no. `__all__` declara la API pública (y evita el aviso de flake8 por imports sin usar).
4. **Alias:** `from alchemy.potions import healing_potion as heal`.
5. **`sys.path` y de dónde se importa:** Python busca primero en la carpeta del script que se ejecuta. Por eso `import elements` funciona desde la raíz. Está prohibido tocar `sys.path`.
6. **Import absoluto vs relativo:**
   - Absoluto: `from alchemy.elements import create_air` — claro, funciona desde cualquier fichero, no cambia si mueves el fichero de sitio.
   - Relativo: `from ..potions import strength_potion` (`.` = este paquete, `..` = el paquete padre) — no depende del nombre del paquete raíz, sirve para ficheros de un mismo paquete. Solo funciona dentro de un paquete, no ejecutando el fichero como script.
7. **Import circular:** A importa B y B importa A. Al importar A, Python lo registra "a medias" (*partially initialized module*); B intenta coger un nombre de A que aún no está definido → `ImportError`.
8. **Cómo se rompe un ciclo** (te pueden preguntar las alternativas):
   - **Import tardío** (el que uso): importar dentro de la función que lo necesita.
   - Mover lo compartido a un tercer módulo que no importe a ninguno de los dos.
   - Pasar el dato como parámetro en vez de importarlo.
   - Importar el módulo (`import a`) en vez del nombre (`from a import f`): el nombre se busca al llamar, no al importar.
9. **Cacheo:** un módulo se ejecuta una sola vez y queda en `sys.modules`.

## 3. Cómo evito el ciclo en "light" (y por qué "dark" explota)

- `light_spellbook.light_spell_allowed_ingredients` no necesita importar nada.
- `light_spellbook.light_spell_record` hace `from .light_validator import validate_ingredients` **dentro de la función**. Cuando se ejecuta, `light_spellbook` ya está completo. El validador sí importa al spellbook arriba del todo, pero ya no hay vuelta.
- En **dark** los dos ficheros se importan entre sí al principio: `dark_spellbook` → `dark_validator` → `dark_spellbook` (a medias, sin `dark_spell_allowed_ingredients` definida todavía) → `ImportError`.
- `grimoire/__init__.py` solo importa la parte light. Si importara también la dark, `import alchemy.grimoire` explotaría y `ft_kaboom_0` no funcionaría.

## 4. Cambios aplicados respecto a lo que había en el repo

- **Faltaba la parte IV completa:** `alchemy/grimoire/` (cinco ficheros), `ft_kaboom_0.py` y `ft_kaboom_1.py`.
- `ft_alembic_5.py` imprimía `=== Alembic 3 ===`; ahora `=== Alembic 5 ===`.
- `alchemy/transmutation/__init__.py` no terminaba en salto de línea (flake8 W292).
- Con esto: flake8 limpio y mypy con un único error, el intencionado de `ft_alembic_4.py`.

## 5. Defensa

### Explicación en 1 minuto
"Es una práctica de imports. Tengo un paquete `alchemy` con elementos, pociones, un subpaquete `transmutation` y un subpaquete `grimoire`. Los `ft_*` prueban cada forma de importar: `import` y `from import`, fichero suelto y paquete, absoluto y relativo. El `__init__.py` decide qué se ve al hacer `import alchemy`. En la parte IV muestro un import circular: en light lo evito con un import dentro de la función; en dark lo dejo a propósito y falla con `ImportError`."

### Preguntas probables
- **¿Para qué sirve `__init__.py`?** Convierte la carpeta en paquete y define qué expone.
- **¿Por qué `alchemy.create_earth()` falla?** El `__init__.py` solo importa `create_air`.
- **¿Qué hace `__all__`?** Lista lo público; con `from alchemy import *` solo entra eso, y evita que flake8 marque los imports como sin usar.
- **¿Cuándo absoluto y cuándo relativo?** Absoluto: claridad y robustez. Relativo: ficheros del mismo paquete, para que no dependa del nombre del paquete raíz.
- **¿Por qué funciona `from elements import create_water` dentro de `alchemy/potions.py`?** `elements.py` está en la raíz y los scripts se lanzan desde ahí, así que la raíz está en `sys.path`.
- **¿Qué es un import circular y cómo lo arreglas?** Ver los apartados 2 y 3 (cuatro alternativas).
- **¿Por qué no importar `dark` en `grimoire/__init__.py`?** Porque `import alchemy.grimoire` ejecutaría el ciclo y rompería también la parte light.
- **¿Se puede ejecutar `recipes.py` directamente?** No: `from ..potions import ...` falla fuera de un paquete. Se prueba a través de `ft_transmutation_*`.
- **Modificación típica:** añadir un elemento nuevo (por ejemplo `create_metal`) y exponerlo en `__init__.py`, o añadir una poción nueva con su alias.

### Puntos débiles que conviene conocer
- `recipes.py` hace `import alchemy` dentro del propio paquete `alchemy` (a propósito, para tener un import absoluto): es circular pero inofensivo, porque `alchemy.create_air` se busca al llamar a la función, no al importar.
- Los ficheros solo funcionan lanzados desde la raíz del repo (por `from elements import ...`).
- En `ft_kaboom_1.py` el import va después de los `print` (para que se vea la cabecera antes de la excepción), por eso no está al principio del fichero.

## 6. Comprobaciones antes de entregar
```bash
flake8 .
mypy .                      # 1 error a propósito: ft_alembic_4.py create_earth
for f in ft_*.py; do python3 $f; done   # alembic_4 y kaboom_1 terminan con excepción a propósito
```
