"""
AI-Powered Competitive Intelligence Analyzer
Parses DOM text and extracts key strategic changes using OpenAI/Claude.
"""

import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

COMPETITIVE_INTEL_PROMPT = """
You are a Lead Competitive Intelligence Analyst.
Analyze this extracted web page data and produce a JSON report:

Page URL: {url}
Title: {title}
Geo Region: {geo}
Raw Page Text:
{text}

Output valid JSON only with these keys:
- pricing_changes (array of strings)
- new_features (array of strings)
- hiring_signals (array of strings)
- threat_level ("LOW", "MODERATE", "HIGH")
- executive_summary (string)
"""


class CompetitiveIntelAnalyzer:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    async def analyze_page(self, page_data: dict) -> dict:
        if "error" in page_data:
            return {"error": page_data["error"], "url": page_data["url"]}

        prompt = COMPETITIVE_INTEL_PROMPT.format(
            url=page_data.get("url", ""),
            title=page_data.get("title", ""),
            geo=page_data.get("geo", "us-east"),
            text=page_data.get("text", "")[:6000]
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return strict JSON analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            analysis = json.loads(response.choices[0].message.content)
            analysis["source_url"] = page_data.get("url")
            return analysis
        except Exception as e:
            logger.error(f"Analysis failed for {page_data.get('url')}: {e}")
            return {"error": str(e), "url": page_data.get("url")}
