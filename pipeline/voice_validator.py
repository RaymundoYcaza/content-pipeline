"""
voice_validator.py

Validador determinista de voz editorial para el pipeline de contenido.
Implementa las restricciones duras definidas en rules/shared/author_voice.md:
  - Frases prohibidas
  - Conteo máximo de emojis (1 por párrafo, 3 por publicación)
  - Presencia de más de una despedida final
  - Uso de "Nos vemos" en piezas marcadas como formales
  - Uso de frase de acción en piezas no-tutorial/no-guía
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# Constantes de voz editorial (espejo normativo de author_voice.md)
# ---------------------------------------------------------------------------

PROHIBITED_PHRASES: list[str] = [
    "hola amigos",
    "esto lo cambia todo",
    "te llevará al siguiente nivel",
    "llevará a tu",
    "al siguiente nivel",
    "mató a",  # en sentido de productos disruptivos
]

FAREWELL_PHRASES: list[str] = [
    "nos vemos",
    "hasta una próxima ocasión",
    "te veo en la siguiente",
]

FORMAL_FORBIDDEN_FAREWELL: str = "nos vemos"

ACTION_PHRASE: str = "recuerda: no esperes más, aplica hoy mismo lo que has aprendido"

TUTORIAL_CATEGORIES: set[str] = {"tutorial", "guia", "guía"}

EMOJI_PATTERN: re.Pattern = re.compile(
    "["
    "\U0001f600-\U0001f64f"
    "\U0001f300-\U0001f5ff"
    "\U0001f680-\U0001f9ff"
    "\U00002600-\U000027bf"
    "\U0001fa00-\U0001fa9f"
    "\U0000200d"
    "]+",
    flags=re.UNICODE,
)


# ---------------------------------------------------------------------------
# Dataclass de resultado
# ---------------------------------------------------------------------------


@dataclass
class VoiceValidationResult:
    valid: bool
    reasons: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------


def _normalize(text: str) -> str:
    """Convierte a minúsculas y elimina tildes para comparación robusta."""
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _count_emojis(text: str) -> int:
    return sum(len(m.group()) for m in EMOJI_PATTERN.finditer(text))


def _split_paragraphs(text: str) -> list[str]:
    """Divide el texto en párrafos por líneas en blanco."""
    return [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]


def _count_farewells(text: str) -> int:
    norm = _normalize(text)
    return sum(1 for phrase in FAREWELL_PHRASES if phrase in norm)


# ---------------------------------------------------------------------------
# Validador principal
# ---------------------------------------------------------------------------


def validate_voice(
    text: str,
    publication_type: str = "general",
    category: str = "general",
) -> VoiceValidationResult:
    """
    Valida el texto contra las restricciones duras de voz editorial.

    Parámetros:
        text: Contenido a validar.
        publication_type: Tipo de publicación según la taxonomía de author_voice.md.
                          Valores posibles: "tutorial", "guia", "post_educativo",
                          "analisis", "formal", "red", "general".
        category: Categoría de la nota (frontmatter["category"]).

    Retorna VoiceValidationResult con valid=True solo si supera todas las restricciones.
    """
    reasons: list[str] = []
    norm_text = _normalize(text)

    # --- Restricción 1: Frases prohibidas ---
    for phrase in PROHIBITED_PHRASES:
        if _normalize(phrase) in norm_text:
            reasons.append(f"Frase prohibida detectada: '{phrase}'.")

    # --- Restricción 2: Límite de emojis por publicación (máx 3) ---
    total_emojis = _count_emojis(text)
    if total_emojis > 3:
        reasons.append(
            f"Demasiados emojis: {total_emojis} (máximo permitido: 3)."
        )

    # --- Restricción 3: Límite de emojis por párrafo (máx 1) ---
    for idx, paragraph in enumerate(_split_paragraphs(text), start=1):
        count = _count_emojis(paragraph)
        if count > 1:
            reasons.append(
                f"Párrafo {idx} contiene {count} emojis (máximo permitido: 1 por párrafo)."
            )

    # --- Restricción 4: Solo una despedida por publicación ---
    farewell_count = _count_farewells(text)
    if farewell_count > 1:
        reasons.append(
            f"Se detectaron {farewell_count} despedidas (máximo permitido: 1)."
        )

    # --- Restricción 5: "Nos vemos" prohibido en piezas formales ---
    is_formal = publication_type in ("formal", "institucional")
    if is_formal and FORMAL_FORBIDDEN_FAREWELL in norm_text:
        reasons.append(
            f"La pieza es formal pero contiene '{FORMAL_FORBIDDEN_FAREWELL}', "
            "que está prohibido en piezas formales."
        )

    # --- Restricción 6: Frase de acción solo en tutorial o guía ---
    is_tutorial = (
        publication_type in TUTORIAL_CATEGORIES
        or _normalize(category) in TUTORIAL_CATEGORIES
    )
    norm_action = _normalize(ACTION_PHRASE)
    if norm_action in norm_text and not is_tutorial:
        reasons.append(
            f"La frase de acción ('{ACTION_PHRASE[:40]}...') "
            "solo puede usarse en piezas de tipo tutorial o guía."
        )

    return VoiceValidationResult(valid=len(reasons) == 0, reasons=reasons)
