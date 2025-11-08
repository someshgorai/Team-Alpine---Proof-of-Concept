from crewai.tools import BaseTool
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Type, List
from pydantic import BaseModel, Field
import logging


class WebScraperToolInput(BaseModel):
    url: str = Field(..., description="URL to scrape for PDF links")


class WebScraperTool(BaseTool):
    name: str = "RFP Website Scraper"
    description: str = "Scrapes websites to find PDF links for RFP documents"
    args_schema: Type[BaseModel] = WebScraperToolInput

    def _run(self, url: str) -> List[str]:
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/118.0.0.0 Safari/537.36"
                )
            }

            # Fetch the webpage
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            pdf_links = set()  # use set to avoid duplicates

            # Extract all anchor tags
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if href.lower().endswith(".pdf"):
                    absolute_url = urljoin(url, href)
                    pdf_links.add(absolute_url)

            logging.info(f"Found {len(pdf_links)} PDF links on {url}")

            return list(pdf_links)

        except requests.exceptions.RequestException as e:
            logging.error(f"Network error while scraping {url}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error while scraping {url}: {e}")

        return []

