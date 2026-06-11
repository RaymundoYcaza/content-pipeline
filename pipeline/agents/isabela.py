from pathlib import Path

from pipeline.core.config import AppConfig
from pipeline.core.frontmatter_manager import FrontmatterManager
from pipeline.core.prompts import PromptLoader
from pipeline.core.provider_router import ProviderRouter
from pipeline.core.validators import validate_outline


class IsabelaProcessor:
    stage_name = "temas"

    def __init__(self, config: AppConfig):
        self.config = config
        self.fm = FrontmatterManager()
        self.prompts = PromptLoader()
        self.router = ProviderRouter(config)

    def _content_root(self) -> Path:
        return Path(self.config.project.content_root)

    def _pending_notes(self) -> list[Path]:
        folder = self._content_root() / "temas"
        return sorted(folder.glob("*.md"))

    def _infer_category(self, title: str) -> str:
        lowered = title.lower()
        if any(token in lowered for token in ["cómo", "guía", "paso a paso"]):
            return "guia"
        if any(token in lowered for token in ["comparativa", "vs", "mejor"]):
            return "comparativa"
        return "general"

    def run(self) -> list[dict]:
        system_prompt = self.prompts.load("isabela/system.md")
        input_template = self.prompts.load("isabela/input.md")
        output_schema = self.prompts.load("isabela/output_schema.md")
        style_rules = self.prompts.load("shared/style.md")
        client = self.router.text_client()
        results = []

        for note_path in self._pending_notes():
            post = self.fm.load(note_path)
            title = str(post.metadata.get("title", "")).strip()
            if not title:
                continue
            category = str(post.metadata.get("category") or self._infer_category(title))
            rendered_input = self.prompts.render(
                input_template,
                {
                    "title": title,
                    "category": category,
                    "body": str(post.content or "").strip(),
                    "output_schema": output_schema,
                    "style_rules": style_rules,
                },
            )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": rendered_input},
            ]
            outline = client.chat(messages).strip()
            is_valid, issues = validate_outline(outline)
            post.metadata["agent"] = "isabela"
            post.metadata["category"] = category
            if not is_valid:
                post.metadata["stage"] = "temas"
                post.metadata["stage_status"] = "review"
                post.metadata["rejection_reason"] = "; ".join(issues)
                self.fm.save(post)
                results.append({
                    "title": title,
                    "category": category,
                    "decision": "review",
                    "path": str(note_path),
                })
                continue
            post.content = outline
            post.metadata["stage"] = "en_redaccion"
            post.metadata["stage_status"] = "approved"
            post.metadata["rejection_reason"] = ""
            self.fm.save(post)
            new_path = self.fm.move(post, self._content_root() / "en_redaccion")
            results.append({
                "title": title,
                "category": category,
                "decision": "approved",
                "path": str(new_path),
            })
        return results
