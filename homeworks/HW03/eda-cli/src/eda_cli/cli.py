from pathlib import Path

import click
import pandas as pd

from .core import compute_quality_flags
from .viz import plot_histograms


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("csv_path", type=click.Path(exists=True))
def overview(csv_path: str) -> None:
    df = pd.read_csv(csv_path)
    flags = compute_quality_flags(df)

    click.echo(f"rows={flags['n_rows']}, cols={flags['n_cols']}")
    click.echo(f"quality_score={flags['quality_score']:.2f}")
    if flags["has_constant_columns"]:
        click.echo(f"constant: {', '.join(flags['constant_columns'])}")
    if flags["has_high_cardinality_categoricals"]:
        click.echo(f"high_card: {', '.join(flags['high_cardinality_columns'])}")


@cli.command()
@click.argument("csv_path", type=click.Path(exists=True))
@click.option("--out-dir", default="reports", show_default=True)
@click.option("--max-hist-columns", default=5, show_default=True, type=int)
@click.option("--top-k-categories", default=10, show_default=True, type=int)
@click.option("--title", default="EDA report", show_default=True)
@click.option(
    "--min-missing-share",
    default=0.3,
    show_default=True,
    type=float,
    help="Колонка считается проблемной, если доля пропусков выше порога",
)
def report(
    csv_path: str,
    out_dir: str,
    max_hist_columns: int,
    top_k_categories: int,
    title: str,
    min_missing_share: float,
) -> None:
    df = pd.read_csv(csv_path)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    flags = compute_quality_flags(df)

    report_path = out_path / "report.md"
    with report_path.open("w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"Источник: `{csv_path}`\n\n")
        f.write("## Общая информация\n\n")
        f.write(f"- Строк: {flags['n_rows']}\n")
        f.write(f"- Колонок: {flags['n_cols']}\n")
        f.write(f"- quality_score: {flags['quality_score']:.2f}\n\n")

        f.write("## Пропуски\n\n")
        missing = flags["missing_share"]
        bad_missing = {
            c: v for c, v in missing.items() if v is not None and v > min_missing_share
        }
        if bad_missing:
            f.write(
                f"Колонки с пропусками > {min_missing_share:.0%} "
                f"({len(bad_missing)} шт.):\n"
            )
            for col, share in bad_missing.items():
                f.write(f"- {col}: {share:.1%}\n")
            f.write("\n")
        else:
            f.write("Сильных проблем с пропусками не найдено.\n\n")

        f.write("## Эвристики качества\n\n")
        if flags["has_constant_columns"]:
            f.write(
                "Константные колонки: "
                + ", ".join(flags["constant_columns"])
                + "\n\n"
            )
        if flags["has_high_cardinality_categoricals"]:
            f.write(
                "Категории с высокой кардинальностью: "
                + ", ".join(flags["high_cardinality_columns"])
                + "\n\n"
            )
        if flags["has_many_zero_values"]:
            f.write("Колонки с большим числом нулей:\n")
            for col
