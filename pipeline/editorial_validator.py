from dataclasses import dataclass
from typing import List, Optional
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
    return sum(1 for line in text.splitlines() if line.strip().startswith("## "))


def has_examples(text: str) -> bool:
    keywords = ["por ejemplo", "ejemplo:", "como en el caso de", "imagina que", "supón que"]
    lower = text.lower()
    return any(k in lower for k in keywords)


def has_actionable_steps(text: str) -> bool:
    """Detecta pasos accionables por listas numeradas o encabezados tipo 'Paso N'."""
    lines = text.splitlines()
    numbered = sum(1 for l in lines if l.strip() and l.strip()[0].isdigit() and l.strip()[1:3] in (". ", ") "))
    return numbered >= 2


def get_first_sentence(text: str) -> str:
    stripped = text.strip()
    # Ignorar el título H1 si lo hay
    lines = [l.strip() for l in stripped.splitlines() if l.strip() and not l.strip().startswith("# ")]
    if not lines:
        return ""
    first_line = lines[0]
    # Tomar hasta el primer punto final
    return first_line.split(".")[0]


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

    # Hook ausente (heurística: segunda persona o fricción en las primeras 3 líneas)
    if vp.reject_if_hook_missing and config.opening_policy.first_paragraph_must_hook:
        opening_block = " ".join(
            l.strip() for l in text.strip().splitlines()[:6]
            if l.strip() and not l.strip().startswith("#")
        ).lower()
        hook_signals = [
            "seguramente", "imagina", "si estás", "te pasa", "¿alguna vez",
            "cuando ", "ya te has", "el problema", "suele ocurrir", "a diario",
        ]
        if not any(sig in opening_block for sig in hook_signals):
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