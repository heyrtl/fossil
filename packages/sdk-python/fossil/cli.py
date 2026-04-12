from __future__ import annotations
import json
import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TQDM_DISABLE"] = "1"
import sys
from pathlib import Path
from typing import Optional

try:
    import click
except ImportError:
    sys.exit("click is required: pip install openfossil[cli]")

from .client import Fossil
from .remote import RemoteStore
from .schema import FailureType, ResolutionType, Severity, TaskDomain
from .utils import format_summary

DEFAULT_API_URL = os.environ.get("FOSSIL_API_URL", "")
DEFAULT_DB = Path.home() / ".fossil" / "fossil.db"


def get_fossil(api_url: Optional[str], db: Optional[str]) -> Fossil:
    url = api_url or DEFAULT_API_URL
    if url:
        return Fossil(store=RemoteStore(url))
    return Fossil(db_path=db or DEFAULT_DB)


@click.group()
@click.version_option(package_name="openfossil")
def cli() -> None:
    """FOSSIL — semantic failure memory for AI agents."""


@cli.command()
@click.option("--api-url", envvar="FOSSIL_API_URL", default=None, help="FOSSIL API URL")
@click.option("--db", default=None, help="Path to local SQLite DB")
@click.option("--situation", "-s", default=None, help="What was the agent attempting?")
@click.option("--failure", "-f", default=None, help="What went wrong?")
@click.option("--resolution", "-r", default=None, help="What fixed it?")
@click.option("--framework", default=None, help="Agent framework e.g. langchain, custom")
@click.option("--model", default=None, help="Model used e.g. llama-3.3-70b-versatile")
@click.option("--shared", is_flag=True, default=False, help="Contribute to community pool")
def record(
    api_url: Optional[str],
    db: Optional[str],
    situation: Optional[str],
    failure: Optional[str],
    resolution: Optional[str],
    framework: Optional[str],
    model: Optional[str],
    shared: bool,
) -> None:
    """Record a reasoning failure and its resolution."""
    click.echo("Recording a fossil.\n")

    situation = situation or click.prompt("Situation — what was the agent attempting")
    failure = failure or click.prompt("Failure   — what went wrong")

    click.echo("\nFailure type:")
    for i, ft in enumerate(FailureType, 1):
        click.echo(f"  {i:2}. {ft.value}")
    ft_idx = click.prompt("Choose", type=click.IntRange(1, len(FailureType)))
    failure_type = list(FailureType)[ft_idx - 1]

    click.echo("\nSeverity:")
    for i, s in enumerate(Severity, 1):
        click.echo(f"  {i}. {s.value}")
    sev_idx = click.prompt("Choose", type=click.IntRange(1, len(Severity)))
    severity = list(Severity)[sev_idx - 1]

    resolution = resolution or click.prompt("\nResolution — what fixed it")

    click.echo("\nResolution type:")
    for i, rt in enumerate(ResolutionType, 1):
        click.echo(f"  {i:2}. {rt.value}")
    rt_idx = click.prompt("Choose", type=click.IntRange(1, len(ResolutionType)))
    resolution_type = list(ResolutionType)[rt_idx - 1]

    click.echo("\nTask domain:")
    for i, td in enumerate(TaskDomain, 1):
        click.echo(f"  {i:2}. {td.value}")
    td_idx = click.prompt("Choose", type=click.IntRange(1, len(TaskDomain)))
    domain = list(TaskDomain)[td_idx - 1]

    framework = framework or click.prompt("\nFramework (e.g. langchain, crewai, custom)")
    model = model or click.prompt("Model     (e.g. llama-3.3-70b-versatile)")

    verified = click.confirm("\nWas the resolution verified to work?", default=True)

    fossil = get_fossil(api_url, db)
    rec = fossil.record(
        situation=situation,
        failure_type=failure_type,
        failure=failure,
        severity=severity,
        resolution_type=resolution_type,
        resolution=resolution,
        framework=framework,
        model=model,
        domain=domain,
        verified=verified,
        shared=shared,
    )
    fossil.close()

    click.echo(f"\n✓ Fossil recorded: {rec.id}")


@cli.command()
@click.argument("query")
@click.option("--api-url", envvar="FOSSIL_API_URL", default=None)
@click.option("--db", default=None)
@click.option("--top-k", default=5, show_default=True, help="Max results")
@click.option("--min-score", default=0.5, show_default=True, help="Min similarity score")
@click.option("--domain", default=None, help="Filter by task domain")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON")
def search(
    query: str,
    api_url: Optional[str],
    db: Optional[str],
    top_k: int,
    min_score: float,
    domain: Optional[str],
    as_json: bool,
) -> None:
    """Search for similar past failures."""
    fossil = get_fossil(api_url, db)
    domain_enum = TaskDomain(domain) if domain else None
    results = fossil.search(query, top_k=top_k, min_score=min_score, domain=domain_enum)
    fossil.close()

    if not results:
        click.echo("No fossils found above similarity threshold.")
        return

    if as_json:
        click.echo(json.dumps([
            {"score": score, "record": rec.to_dict()}
            for rec, score in results
        ], indent=2))
        return

    for rec, score in results:
        click.echo(f"\n[score: {score:.4f}]")
        click.echo(format_summary(rec))


@cli.command("list")
@click.option("--api-url", envvar="FOSSIL_API_URL", default=None)
@click.option("--db", default=None)
@click.option("--limit", default=20, show_default=True)
@click.option("--offset", default=0, show_default=True)
@click.option("--json", "as_json", is_flag=True, default=False)
def list_cmd(
    api_url: Optional[str],
    db: Optional[str],
    limit: int,
    offset: int,
    as_json: bool,
) -> None:
    """List recent fossils."""
    fossil = get_fossil(api_url, db)
    records = fossil.list(limit=limit, offset=offset)
    total = fossil.count()
    fossil.close()

    if not records:
        click.echo("No fossils recorded yet.")
        return

    if as_json:
        click.echo(json.dumps([r.to_dict() for r in records], indent=2))
        return

    click.echo(f"Showing {len(records)} of {total} fossils\n")
    for rec in records:
        click.echo(format_summary(rec))
        click.echo()


@cli.command()
@click.option("--api-url", envvar="FOSSIL_API_URL", default=None)
@click.option("--db", default=None)
def ping(api_url: Optional[str], db: Optional[str]) -> None:
    """Check connection to FOSSIL store."""
    fossil = get_fossil(api_url, db)
    try:
        count = fossil.count()
        fossil.close()
        url = api_url or DEFAULT_API_URL
        store_type = f"remote ({url})" if url else f"local ({DEFAULT_DB})"
        click.echo(f"✓ Connected to {store_type}")
        click.echo(f"  {count} fossil{'s' if count != 1 else ''} in store")
    except Exception as e:
        click.echo(f"✗ Connection failed: {e}", err=True)
        sys.exit(1)