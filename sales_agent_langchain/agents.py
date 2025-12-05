from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from langchain.tools import BaseTool

from tools.playwright_scraper_tool import PlaywrightScraperTool
from tools.pdf_extractor_tool import PDFExtractorTool
from tools.date_checker_tool import DateCheckerTool

# Initialize Gemini model
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

web_scraper_prompt = SystemMessage(
    Role =  "RFP Document Discovery Specialist",
    Goal =  "Find and identify new RFP (Request for Proposal) PDF documents from specified websites",
    Backstory =  """ You are an expert at navigating government and corporate procurement websites. \n
    You have years of experience finding tender documents and RFPs across various platforms. \n
    You know how to identify legitimate RFP documents and filter out irrelevant PDFs. \n
    You're meticulous about tracking which documents are new versus already processed.""",
    Instructions =  """ Scan the website {target_url} to find all PDF links.
    Focus on RFPs, tenders, or procurement notices."""
)

web_scraper_agent = model.bind_tools(
    [PlaywrightScraperTool()]
)

response = web_scraper_agent.invoke(web_scraper_prompt)
