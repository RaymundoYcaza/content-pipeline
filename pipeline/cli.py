from pathlib import Path
import os
import typer
from rich.console import Console
from rich.table import Table

from pipeline.agents.bea import BeaProcessor
from pipeline.agents.isabela import IsabelaProcessor
from pipeline.agents.david import DavidProcessor
from pipeline.agents.basilio import BasilioProcessor
from pipeline.core.config import load_config
from pipeline.core.corpus import load_published_titles
from pipeline.core.embeddings import EmbeddingService
from pipeline.core.env import load_dotenv
from pipeline.core.frontmatter_manager import FrontmatterManager
from pipeline.core.provider_router import ProviderRouter
from pipeline.core.similarity_engine import SimilarityEngine
from pipeline.core.state import collect_state

app = typer.Typer(help="Deterministic AI-assisted content pipeline")
console = Console()


def _load_runtime(config_path: Path):
    load_dotenv()
    return load_config(config_path)


@app.command()
def doctor(config: Path = typer.Option(Path("config/pipeline.yaml"), exists=True)):
    cfg = _load_runtime(config)
    router = ProviderRouter(cfg)
    console.print("[bold green]Pipeline doctor[/bold green]")
    console.print(f"Brand: {cfg.project.brand}")
    console.print(f"Text provider: {cfg.providers.active_text}")
    console.print(f"Embeddings provider: {cfg.providers.active_embeddings}")
    console.print(f"Resolved text endpoint: {router.describe_text_endpoint()}")
    console.print(f"Resolved embeddings endpoint: {router.describe_embeddings_endpoint()}")
    console.print(f"OLLAMA_API_KEY set: {'yes' if os.getenv('OLLAMA_API_KEY') else 'no'}")
    console.print(f"OPENROUTER_API_KEY set: {'yes' if os.getenv('OPENROUTER_API_KEY') else 'no'}")


@app.command()
def state(config: Path = typer.Option(Path("config/pipeline.yaml"), exists=True)):
    cfg = _load_runtime(config)
    summary = collect_state(Path(cfg.project.content_root))
    table = Table(title="Pipeline state")
    table.add_column("Stage")
    table.add_column("Count", justify="right")
    for stage, count in summary.items():
        table.add_row(stage, str(count))
    console.print(table)


@app.command("similarity-check")
def similarity_check(note: Path, config: Path = typer.Option(Path("config/pipeline.yaml"), exists=True)):
    cfg = _load_runtime(config)
    fm = FrontmatterManager()
    post = fm.load(note)
    title = str(post.metadata.get("title", "")).strip()
    if not title:
        raise typer.BadParameter("The note must define a title in frontmatter")
    titles = load_published_titles(Path("data/published_titles.json"))
    if not titles:
        console.print("No published titles found in data/published_titles.json")
        raise typer.Exit(code=1)
    embeddings = EmbeddingService(cfg)
    similarity = SimilarityEngine()
    query_embedding = embeddings.embed([title])[0]
    corpus_embeddings = embeddings.embed(titles)
    scored = []
    for existing_title, emb in zip(titles, corpus_embeddings):
        score = similarity.cosine_similarity(query_embedding, emb)
        scored.append((existing_title, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    max_score = scored[0][1]
    decision = similarity.classify(max_score, cfg.similarity.review_threshold, cfg.similarity.reject_threshold)

    table = Table(title=f"Similarity report: {title}")
    table.add_column("Published title")
    table.add_column("Score", justify="right")
    for existing_title, score in scored[:5]:
        table.add_row(existing_title, f"{score:.6f}")
    console.print(table)
    console.print(f"Max score: [bold]{max_score:.6f}[/bold]")
    console.print(f"Decision: [bold]{decision}[/bold]")


@app.command()
def run(agent: str = typer.Option("all", help="bea | isabela | david | basilio | all"), config: Path = typer.Option(Path("config/pipeline.yaml"), exists=True)):
    cfg = _load_runtime(config)
    if agent not in {"bea", "all", "isabela", "david", "basilio"}:
        raise typer.BadParameter("agent must be one of: bea, isabela, david, basilio, all")
    if agent in {"bea", "all"}:
        results = BeaProcessor(cfg).run()
        table = Table(title="Bea results")
        table.add_column("Title")
        table.add_column("Score", justify="right")
        table.add_column("Decision")
        table.add_column("Path")
        for item in results:
            table.add_row(item["title"], f"{item['score']:.6f}", item["decision"], item["path"])
        console.print(table)
        if agent == "bea":
            return
    if agent in {"isabela", "all"}:
        results = IsabelaProcessor(cfg).run()
        table = Table(title="Isabela results")
        table.add_column("Title")
        table.add_column("Category")
        table.add_column("Decision")
        table.add_column("Path")
        for item in results:
            table.add_row(item["title"], item["category"], item["decision"], item["path"])
        console.print(table)
        if agent == "isabela":
            return
    if agent in {"david", "all"}:
        results = DavidProcessor(cfg).run()
        table = Table(title="David results")
        table.add_column("Title")
        table.add_column("Category")
        table.add_column("Decision")
        table.add_column("Path")
        for item in results:
            table.add_row(item["title"], item["category"], item["decision"], item["path"])
        console.print(table)
        if agent == "david":
            return
    if agent in {"basilio", "all"}:
        results = BasilioProcessor(cfg).run()
        table = Table(title="Basilio results")
        table.add_column("Title")
        table.add_column("Category")
        table.add_column("Decision")
        table.add_column("Path")
        for item in results:
            table.add_row(item["title"], item["category"], item["decision"], item["path"])
        console.print(table)
        if agent == "basilio":
            return
    console.print("Other agents are not implemented yet.")


@app.command()
def config_show(config: Path = typer.Option(Path("config/pipeline.yaml"), exists=True)):
    cfg = _load_runtime(config)
    console.print(cfg.model_dump())


if __name__ == "__main__":
    app()