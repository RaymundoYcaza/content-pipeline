from pipeline.editorial_config import EditorialConfig

DEPTH_DESCRIPTIONS = {
    "shallow": (
        "Escribe una pieza breve y directa centrada en una sola idea. "
        "Sin desarrollo extenso ni subsecciones innecesarias."
    ),
    "medium": (
        "Equilibra contexto, explicación y ejemplo. "
        "Desarrolla cada sección con suficiente profundidad para ser útil, "
        "sin alargar innecesariamente."
    ),
    "deep": (
        "Desarrolla la pieza con matices, implicaciones, ejemplos concretos "
        "y consecuencias prácticas. Permite más secciones y mayor extensión."
    ),
}


def build_editorial_context(config: EditorialConfig, depth_override: str = None) -> str:
    """
    Genera el bloque de instrucciones editoriales para inyectar en el prompt.
    Se llama justo antes de enviar el prompt al modelo.
    """
    dp = config.depth_policy
    profile = depth_override or dp.profile
    description = DEPTH_DESCRIPTIONS.get(profile, DEPTH_DESCRIPTIONS["medium"])

    blacklist_formatted = "\n".join(f'  - "{b}"' for b in config.opening_blacklist)

    examples_instruction = (
        "- Debes incluir al menos un ejemplo concreto."
        if dp.must_include_examples else ""
    )
    steps_instruction = (
        "- Debes incluir pasos accionables numerados."
        if dp.must_include_actionable_steps else ""
    )

    return f"""
## Instrucciones editoriales

### Profundidad
Perfil: `{profile}` ({dp.target_words_min}–{dp.target_words_max} palabras, {dp.min_sections}–{dp.max_sections} secciones).
{description}

### Apertura
La primera frase debe abrir con un gancho contextual que conecte con una situación real, problema o tensión de la audiencia.
No uses introducciones genéricas como:
{blacklist_formatted}

### Contenido obligatorio
{examples_instruction}
{steps_instruction}
""".strip()