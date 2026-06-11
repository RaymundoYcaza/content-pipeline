from pathlib import Path
from datetime import datetime, timezone
import shutil
import frontmatter


class FrontmatterManager:
    def load(self, path: Path):
        post = frontmatter.load(path)
        post.metadata.setdefault("source_path", str(path))
        return post

    def save(self, post, path: Path | None = None) -> Path:
        target = Path(path or post.metadata.get("source_path"))
        post.metadata["updated"] = datetime.now(timezone.utc).isoformat()
        target.write_text(frontmatter.dumps(post), encoding="utf-8")
        post.metadata["source_path"] = str(target)
        return target

    def move(self, post, target_dir: Path) -> Path:
        current = Path(post.metadata["source_path"])
        target_dir.mkdir(parents=True, exist_ok=True)
        new_path = target_dir / current.name
        shutil.move(str(current), str(new_path))
        post.metadata["source_path"] = str(new_path)
        self.save(post, new_path)
        return new_path
