from pathlib import Path

from pipeline.core.config import AppConfig
from pipeline.core.frontmatter_manager import FrontmatterManager
from pipeline.core.prompts import PromptLoader
from pipeline.core.provider_router import ProviderRouter
from pipeline.core.validators import validate_edited_draft


class BasilioProcessor:
    stage_name = "en_edicion"

    def __init__(self, config: AppConfig):
        self.config = config
        self.fm = FrontmatterManager()
        self.prompts = PromptLoader()
        self.router = ProviderRouter(config)

    def _content_root(self) -> Path:
        return Path(self.config.project.content_root)

    def _pending_notes(self) -> list[Path]:
        folder = self._content_root() / "en_edicion"
        return sorted(folder.glob("*.md"))

    def run(self) -> list[dict]:
        system_prompt = self.prompts.load("basilio/system.md")
        input_template = self.prompts.load("basilio/input.md")
        output_schema = self.prompts.load("basilio/output_schema.md")
        editing_style = self.prompts.load("shared/editing_style.md")
        client = self.router.text_client()
        results = []

        for note_path in self._pending_notes():
            post = self.fm.load(note_path)
            title = str(post.metadata.get("title", "")).strip()
            category = str(post.metadata.get("category", "general")).strip() or "general"
            draft = str(post.content or "").strip()
            if not title or not draft:
                continue

            rendered_input = self.prompts.render(
                input_template,
                {
                    "title": title,
                    "category": category,
                    "draft": draft,
                    "editing_style": editing_style,
                    "output_schema": output_schema,
                },
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": rendered_input},
            ]

            edited = client.chat(messages).strip()
            is_valid, issues = validate_edited_draft(draft, edited)

            post.metadata["agent"] = "basilio"
            if not is_valid:
                post.metadata["stage"] = "en_edicion"
                post.metadata["stage_status"] = "review"
                post.metadata["revision_notes"] = issues
                post.metadata["rejection_reason"] = "; ".join(issues)
                self.fm.save(post)
                results.append(
                    {
                        "title": title,
                        "category": category,
                        "decision": "review",
                        "path": str(note_path),
                    }
                )
                continue

            post.content = edited
            post.metadata["stage"] = "revision_humana"
            post.metadata["stage_status"] = "approved"
            post.metadata["revision_notes"] = []
            post.metadata["rejection_reason"] = ""
            self.fm.save(post)
            new_path = self.fm.move(post, self._content_root() / "revision_humana")
            results.append(
                {
                    "title": title,
                    "category": category,
                    "decision": "approved",
                    "path": str(new_path),
                }
            )

        return results