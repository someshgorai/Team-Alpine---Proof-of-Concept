from crewai.tools import BaseTool
from playwright.sync_api import sync_playwright

class PlaywrightScraperTool(BaseTool):
    name: str = "Playwright PDF Scraper"
    description: str = "Scrapes dynamically rendered websites and extracts all PDF links."

    def _run(self, url: str) -> str:
        """Launches a headless browser and extracts PDF links."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")

            pdf_links = page.eval_on_selector_all(
                "a[href$='.pdf']", "elements => elements.map(el => el.href)"
            )

            browser.close()
            if not pdf_links:
                return "No PDF links found."
            return "\n".join(pdf_links)

