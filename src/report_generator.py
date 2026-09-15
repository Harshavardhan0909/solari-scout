"""
Report Generator
Formats raw intelligence analyses into clean Markdown/Executive Briefings.
"""

import os
from pathlib import Path
from datetime import datetime


class ReportGenerator:
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_markdown(self, competitor_name: str, analyses: list[dict]) -> str:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        
        md_content = f"# 📊 COMPETITIVE INTELLIGENCE BRIEF — {date_str}\n"
        md_content += f"**TARGET:** {competitor_name}\n"
        md_content += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        for a in analyses:
            if "error" in a:
                continue
            md_content += f"### Source: {a.get('source_url')}\n"
            md_content += f"**Threat Level:** {a.get('threat_level', 'N/A')}\n\n"
            
            md_content += "📌 **PRICING CHANGES**\n"
            for p in a.get("pricing_changes", []):
                md_content += f"• {p}\n"
            
            md_content += "\n📌 **NEW FEATURES**\n"
            for f in a.get("new_features", []):
                md_content += f"• {f}\n"

            md_content += "\n📌 **HIRING SIGNALS**\n"
            for h in a.get("hiring_signals", []):
                md_content += f"• {h}\n"
                
            md_content += f"\n**Executive Summary:** {a.get('executive_summary', 'N/A')}\n"
            md_content += "\n---\n"

        md_content += "\n*Generated automatically by Solari Scout*"
        
        filename = f"{competitor_name.lower().replace(' ', '_')}_{date_str}.md"
        filepath = self.output_dir / filename
        filepath.write_text(md_content)
        return str(filepath)
