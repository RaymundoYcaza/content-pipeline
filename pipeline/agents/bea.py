from pathlib import Path

from pipeline.core.config import AppConfig
from pipeline.core.corpus import load_published_titles
from pipeline.core.embeddings import EmbeddingService
from pipeline.core.frontmatter_manager import FrontmatterManager
from pipeline.core.similarity_engine import SimilarityEngine


class BeaProcessor:
    stage_name = "propuestas"

    def __init__(self, config: AppConfig):
        self.config = config
        self.fm = FrontmatterManager()
        self.embedding_service = EmbeddingService(config)
        self.similarity = SimilarityEngine()

    def _content_root(self) -> Path:
        return Path(self.config.project.content_root)

    def _pending_notes(self) -> list[Path]:
        folder = self._content_root() / "propuestas"
        return sorted(folder.glob("*.md"))

    def run(self) -> list[dict]:
        published_titles = load_published_titles(Path("data/published_titles.json"))
        published_embeddings = self.embedding_service.embed(published_titles) if published_titles else []
        results = []
        for note_path in self._pending_notes():
            post = self.fm.load(note_path)
            title = str(post.metadata.get("title", "")).strip()
            if not title:
                continue
            query_embedding = self.embedding_service.embed([title])[0]
            score = self.similarity.max_similarity(query_embedding, published_embeddings)
            decision = self.similarity.classify(
                score,
                review_threshold=self.config.similarity.review_threshold,
                reject_threshold=self.config.similarity.reject_threshold,
            )
            post.metadata["agent"] = "bea"
            post.metadata["similarity_score"] = round(score, 6)
            if decision == "approve":
                post.metadata["stage"] = "temas"
                post.metadata["stage_status"] = "approved"
                post.metadata["rejection_reason"] = ""
                self.fm.save(post)
                new_path = self.fm.move(post, self._content_root() / "temas")
            elif decision == "review":
                post.metadata["stage"] = "propuestas"
                post.metadata["stage_status"] = "review"
                post.metadata["rejection_reason"] = "High similarity; manual review required"
                new_path = self.fm.save(post)
            else:
                post.metadata["stage"] = "descartados"
                post.metadata["stage_status"] = "rejected"
                post.metadata["rejection_reason"] = "Similarity above reject threshold"
                self.fm.save(post)
                new_path = self.fm.move(post, self._content_root() / "descartados")
            results.append({
                "title": title,
                "score": round(score, 6),
                "decision": decision,
                "path": str(new_path),
            })
        return results
