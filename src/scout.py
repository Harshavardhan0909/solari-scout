"""
Solari Scout — CLI Interface
Main entry point for single scans, full briefings, and scheduled execution.
"""

import asyncio
import logging
import click
import yaml
from rich.console import Console
from .browser_manager import SolariBrowserManager
from .analyzer import CompetitiveIntelAnalyzer
from .report_generator import ReportGenerator

console = Console()
logging.basicConfig(level=logging.INFO)


async def execute_scan(url: str, geo: str):
    mgr = SolariBrowserManager()
    analyzer = CompetitiveIntelAnalyzer()
    try:
        session = await mgr.launch_browser(geo=geo)
        data = await mgr.navigate_and_extract(session, url)
        analysis = await analyzer.analyze_page(data)
        return analysis
    finally:
        await mgr.close_all()


async def execute_brief(config_path: str):
    with open(config_path) as f:
        config = yaml.safe_load(f)

    mgr = SolariBrowserManager()
    analyzer = CompetitiveIntelAnalyzer()
    reporter = ReportGenerator(config.get("report", {}).get("output_dir", "./reports"))

    for target in config.get("targets", []):
        name = target["name"]
        geo = target.get("geo", "us-east")
        console.print(f"[bold cyan]Scanning target: {name}...[/bold cyan]")
        
        session = await mgr.launch_browser(geo=geo)
        analyses = []
        for url in target.get("urls", []):
            page_data = await mgr.navigate_and_extract(session, url)
            analysis = await analyzer.analyze_page(page_data)
            analyses.append(analysis)
            
        await mgr.close_all()
        report_path = reporter.generate_markdown(name, analyses)
        console.print(f"[bold green]Report saved to: {report_path}[/bold green]")


@click.group()
def cli():
    """🔭 Solari Scout — AI-Powered Competitive Intelligence Agent"""
    pass


@cli.command()
@click.option("--url", required=True, help="Target URL to scan")
@click.option("--geo", default="us-east", help="Browser geolocation")
def scan(url: str, geo: str):
    """Run a single website scan."""
    result = asyncio.run(execute_scan(url, geo))
    console.print_json(data=result)


@cli.command()
@click.option("--config", required=True, help="Path to config file")
def brief(config: str):
    """Run full briefing across multiple targets."""
    asyncio.run(execute_brief(config))


if __name__ == "__main__":
    cli()
