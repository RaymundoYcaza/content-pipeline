from pathlib import Path

from pipeline.core.config import AppConfig
from pipeline.core.frontmatter_manager import FrontmatterManager
from pipeline.core.prompts import PromptLoader
from pipeline.core.provider_router import ProviderRouter
from pipeline.core.validators import validate_draft_against_outline
from pipeline.editorial_config import load_editorial_config
from pipeline.editorial_prompt_context import build_editorial_context
from pipeline.editorial_validator import validate_editorial_output


class DavidProcessor:
    stage_name = "en_redaccion"

    def __init__(self, config: AppConfig):
        self.config = config
        self.fm = FrontmatterManager()
        self.prompts = PromptLoader()
        self.router = ProviderRouter(config)

    def _content_root(self) -> Path:
        return Path(self.config.project.content_root)

    def _pending_notes(self) -> list[Path]:
        folder = self._content_root() / "en_redaccion"
        return sorted(folder.glob("*.md"))

    def run(self) -> list[dict]:

        base_system_prompt = self.prompts.load("david/system.md")

        editorial_config = load_editorial_config()
        editorial_context = build_editorial_context(editorial_config)

        system_prompt = (
            base_system_prompt
            + "\n\n"
            + editorial_context
        )

        input_template = self.prompts.load("david/input.md")
        output_schema = self.prompts.load("david/output_schema.md")
        draft_style = self.prompts.load("shared/draft_style.md")
        client = self.router.text_client()
        results = []

        for note_path in self._pending_notes():
            post = self.fm.load(note_path)
            title = str(post.metadata.get("title", "")).strip()
            category = str(post.metadata.get("category", "general")).strip() or "general"
            outline = str(post.content or "").strip()
            if not title or not outline:
                continue

            editorial_config = load_editorial_config()
            editorial_context = build_editorial_context(editorial_config)

            rendered_input = self.prompts.render(
                input_template,
                {
                    "title": title,
                    "category": category,
                    "outline": outline,
                    "output_schema": output_schema,
                    "draft_style": draft_style,
                },
            )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": rendered_input},
            ]
            draft = client.chat(messages).strip()

            editorial_result = validate_editorial_output(
                draft,
                editorial_config
            )

            if not editorial_result.valid:
                post.metadata["stage"] = "en_redaccion"
                post.metadata["stage_status"] = "rejected"
                post.metadata["rejection_reason"] = "; ".join(
                    editorial_result.reasons
                )

                self.fm.save(post)

                results.append({
                    "title": title,
                    "category": category,
                    "decision": "rejected",
                    "path": str(note_path),
                })

                continue

            is_valid, issues = validate_draft_against_outline(
                outline,
                draft
            )

            post.metadata["agent"] = "david"
            if not is_valid:
                post.metadata["stage"] = "en_redaccion"
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

            post.content = draft
            post.metadata["stage"] = "en_edicion"
            post.metadata["stage_status"] = "approved"
            post.metadata["rejection_reason"] = ""
            self.fm.save(post)
            new_path = self.fm.move(post, self._content_root() / "en_edicion")
            results.append({
                "title": title,
                "category": category,
                "decision": "approved",
                "path": str(new_path),
            })
        return results
