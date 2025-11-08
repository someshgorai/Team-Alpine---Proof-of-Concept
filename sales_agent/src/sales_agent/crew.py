from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.web_scraper_tool import WebScraperTool
from .tools.pdf_extractor_tool import PDFExtractorTool
from .tools.date_checker_tool import DateCheckerTool
from crewai_tools import SeleniumScrapingTool
from crewai_tools import ScrapeElementFromWebsiteTool
from .tools.playwright_scraper_tool import PlaywrightScraperTool

tool_playwright = PlaywrightScraperTool()
selenium_tool = SeleniumScrapingTool()
scrape_tool = ScrapeElementFromWebsiteTool()


@CrewBase
class RfpScraperCrew:
    """RFP Scraper crew for discovering and extracting RFP documents"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        self.web_scraper = WebScraperTool()
        self.pdf_extractor = PDFExtractorTool()
        self.date_checker = DateCheckerTool()

    @agent
    def rfp_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['rfp_finder'],
            tools=[tool_playwright],
            verbose=True
        )

    @agent
    def pdf_processor(self) -> Agent:
        return Agent(
            config=self.agents_config['pdf_processor'],
            tools=[self.pdf_extractor, self.date_checker],
            verbose=True
        )

    @agent
    def rfp_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['rfp_analyst'],
            verbose=True
        )

    @task
    def discover_rfp_links(self) -> Task:
        return Task(
            config=self.tasks_config['discover_rfp_links'],
            agent=self.rfp_finder()
        )

    @task
    def extract_pdf_content(self) -> Task:
        return Task(
            config=self.tasks_config['extract_pdf_content'],
            agent=self.pdf_processor()
        )

    @task
    def analyze_rfp_data(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_rfp_data'],
            agent=self.rfp_analyst(),
            output_file='data/processed/rfp_analysis.json'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the RFP Scraper crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )


