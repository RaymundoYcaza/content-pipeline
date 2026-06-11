from pathlib import Path


class PromptLoader:
    def __init__(self, root: Path = Path("rules")):
        self.root = root

    def load(self, relative_path: str) -> str:
        path = self.root / relative_path
        return path.read_text(encoding="utf-8").strip()

    def render(self, template: str, variables: dict[str, str]) -> str:
        output = template
        for key, value in variables.items():
            output = output.replace("{{ " + key + " }}", value)
            output = output.replace("{{" + key + "}}", value)
        return output