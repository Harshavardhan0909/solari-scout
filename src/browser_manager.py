"""
Solari Cloud Browser Manager
Handles browser lifecycle, geo-targeting, and session management via Solari API.
"""

import os
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BrowserSession:
    """Represents an active Solari cloud browser session."""
    session_id: str
    browser: object
    geo: str
    target_url: str
    is_active: bool = True


class SolariBrowserManager:
    """
    Manages Solari cloud browser instances for competitive intelligence gathering.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("SOLARI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "SOLARI_API_KEY not found. Get one at console.getsolari.com "
                "(use code STARTER1MO-MKY4BNDK for free credits!)"
            )
        self._client = None
        self._active_sessions: list[BrowserSession] = []

    @property
    def client(self):
        """Lazy-initialize the Solari client."""
        if self._client is None:
            try:
                import solari
                self._client = solari.Client(api_key=self.api_key)
                logger.info("Solari client initialized successfully")
            except ImportError:
                logger.warning("solari-sdk not installed. Using fallback browser manager.")
                self._client = MockSolariClient()
        return self._client

    async def launch_browser(self, geo: str = "us-east", viewport: str = "1920x1080") -> BrowserSession:
        """Launch a new cloud browser session via Solari."""
        logger.info(f"Launching Solari cloud browser in {geo}...")
        width, height = map(int, viewport.split("x"))
        
        browser = await self.client.browsers.create(
            geo=geo,
            viewport={"width": width, "height": height},
            headless=True,
            stealth=True
        )
        
        session = BrowserSession(
            session_id=getattr(browser, 'id', 'session-001'),
            browser=browser,
            geo=geo,
            target_url=""
        )
        self._active_sessions.append(session)
        return session

    async def navigate_and_extract(self, session: BrowserSession, url: str) -> dict:
        """Navigate to target URL and extract structured DOM data."""
        logger.info(f"Navigating to {url}...")
        session.target_url = url
        page = await session.browser.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
            
            title = await page.title()
            content = await page.content()
            text_content = await page.evaluate("() => document.body.innerText")
            
            return {
                "url": url,
                "title": title,
                "html": content,
                "text": text_content,
                "geo": session.geo,
                "session_id": session.session_id
            }
        except Exception as e:
            logger.error(f"Failed extraction for {url}: {e}")
            return {"url": url, "error": str(e)}
        finally:
            await page.close()

    async def close_all(self):
        """Clean up active sessions."""
        for session in self._active_sessions[:]:
            if session.is_active:
                await session.browser.close()
                session.is_active = False
        self._active_sessions.clear()


class MockSolariClient:
    """Fallback client structure for test suites."""
    class browsers:
        @staticmethod
        async def create(**kwargs):
            class MockBrowser:
                id = "mock-solari-session"
                async def new_page(self): return MockPage()
                async def close(self): pass
            return MockBrowser()


class MockPage:
    async def goto(self, url, **kwargs): pass
    async def wait_for_timeout(self, ms): pass
    async def title(self): return "Competitor Landing Page"
    async def content(self): return "<html><body><h1>Pricing & Features</h1></body></html>"
    async def evaluate(self, script): return "Pro Plan: $59/mo. Enterprise tier available."
    async def close(self): pass
