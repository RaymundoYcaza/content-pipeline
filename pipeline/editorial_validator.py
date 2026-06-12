from dataclasses import dataclass
from typing import List, Optional
import re
from pipeline.editorial_config import EditorialConfig


@dataclass
class ValidationResult:
    valid: bool
    reasons: List[str]

    def __bool__(self):
        return self.valid


def count_words(text: str) -> int:
    return len(text.split())


def count_sections(text: str) -> int:
    """Cuenta secciones de nivel H2 y H3 para evaluar profundidad estructural."""
    return sum(
        1 for line in text.splitlines()
        if line.strip().startswith("## ") or line.strip().startswith("### ")
    )


def has_examples(text: str) -> bool:
    keywords = ["por ejemplo", "ejemplo:", "como en el caso de", "imagina que", "supón que"]
    lower = text.lower()
    return any(k in lower for k in keywords)


def has_actionable_steps(text: str) -> bool:
    """Detecta pasos accionables por listas numeradas (N. o N)) o encabezados tipo 'Paso N'."""
    pattern = re.compile(r"^\s*\d+[.)]\s+\S")
    lines = text.splitlines()
    numbered = sum(1 for line in lines if pattern.match(line))
    return numbered >= 2


def get_first_sentence(text: str) -> str:
    """Retorna la primera línea de contenido real, ignorando todos los encabezados Markdown."""
    stripped = text.strip()
    heading_pattern = re.compile(r"^#{1,6}\s")
    lines = [
        l.strip()
        for l in stripped.splitlines()
        if l.strip() and not heading_pattern.match(l.strip())
    ]
    if not lines:
        return ""
    return lines[0].split(".")[0]


def validate_editorial_output(
    text: str,
    config: EditorialConfig,
    depth_profile_override: Optional[str] = None,
) -> ValidationResult:
    """
    Valida el texto generado contra la configuración editorial.
    Retorna ValidationResult con valid=True si pasa todas las reglas activas.
    """
    reasons = []
    dp = config.depth_policy
    vp = config.validator

    profile = depth_profile_override or dp.profile

    # Longitud
    if vp.reject_if_out_of_length_range:
        word_count = count_words(text)
        if word_count < dp.target_words_min:
            reasons.append(
                f"Texto demasiado corto: {word_count} palabras "
                f"(mínimo {dp.target_words_min})."
            )
        elif word_count > dp.target_words_max:
            reasons.append(
                f"Texto demasiado largo: {word_count} palabras "
                f"(máximo {dp.target_words_max})."
            )

    # Secciones (profundidad estructural)
    if vp.reject_if_too_shallow:
        section_count = count_sections(text)
        if section_count < dp.min_sections:
            reasons.append(
                f"Estructura insuficiente: {section_count} secciones "
                f"(mínimo {dp.min_sections})."
            )
        elif section_count > dp.max_sections:
            reasons.append(
                f"Estructura excesiva: {section_count} secciones "
                f"(máximo {dp.max_sections})."
            )

    # Apertura genérica
    if vp.reject_if_opening_generic and config.opening_policy.required:
        first = get_first_sentence(text).lower()
        for banned in config.opening_blacklist:
            if first.startswith(banned.lower()):
                reasons.append(
                    f"Apertura genérica detectada: empieza con '{banned}'."
                )
                break

    # Hook ausente: usar señales del config si existen, o fallback a lista interna
    if vp.reject_if_hook_missing and config.opening_policy.first_paragraph_must_hook:
        opening_block = " ".join(
            l.strip() for l in text.strip().splitlines()[:6]
            if l.strip() and not l.strip().startswith("#")
        ).lower()
        # Señales base (hardcoded como fallback)
        _DEFAULT_HOOK_SIGNALS = [
            "seguramente", "imagina", "si estás", "te pasa", "¿alguna vez",
            "cuando ", "ya te has", "el problema", "suele ocurrir", "a diario",
        ]
        # Mapa semántico: nombre de requirement → señales textuales
        _REQUIREMENT_SIGNALS: dict[str, list[str]] = {
            "problem_situated_context": ["el problema", "suele ocurrir", "falla cuando", "ocurre cuando"],
            "audience_specific_scene": ["imagina que", "si estás", "cuando trabajas", "cuando tratas"],
            "second_person_context": ["seguramente", "ya te has", "te pasa", "¿alguna vez"],
            "practical_tension": ["a diario", "cada vez que", "sin darte cuenta", "tarde o temprano"],
        }
        if config.hook_requirements:
            effective_signals: list[str] = []
            for req in config.hook_requirements:
                effective_signals.extend(_REQUIREMENT_SIGNALS.get(req, []))
            if not effective_signals:
                effective_signals = _DEFAULT_HOOK_SIGNALS
        else:
            effective_signals = _DEFAULT_HOOK_SIGNALS
        if not any(sig in opening_block for sig in effective_signals):
            reasons.append(
                "El primer bloque no contiene un gancho contextual reconocible."
            )

    # Ejemplos
    if vp.reject_if_missing_examples_when_required and dp.must_include_examples:
        if not has_examples(text):
            reasons.append("La pieza no incluye ningún ejemplo.")

    # Pasos accionables
    if vp.reject_if_missing_actionable_steps_when_required and dp.must_include_actionable_steps:
        if not has_actionable_steps(text):
            reasons.append("La pieza no incluye pasos accionables.")

    return ValidationResult(valid=len(reasons) == 0, reasons=reasons)