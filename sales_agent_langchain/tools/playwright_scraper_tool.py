from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from playwright.sync_api import sync_playwright

class PlaywrightInput(BaseModel):
    url: str = Field(..., description="Website URL to scrape PDF links from given URL")

def playwright_scraper(url: str) -> str:
    """Launch a headless browser and extract PDF links from the webpage."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        pdf_links = page.eval_on_selector_all(
            "a[href$='.pdf']", "els => els.map(el => el.href)"
        )
        browser.close()
    return "\n".join(pdf_links) if pdf_links else "No PDF links found."

PlaywrightScraperTool = BaseTool.from_function(
    func=playwright_scraper,
    name="PlaywrightPDFScraper",
    description="Scrapes a dynamically rendered website and extracts all PDF links.",
    args_schema=PlaywrightInput,
)
