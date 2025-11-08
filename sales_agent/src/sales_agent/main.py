import os
from sales_agent.crew import RfpScraperCrew
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/rfp_scraper.log'),
        logging.StreamHandler()
    ]
)


def run_rfp_scraper(target_url: str, days_threshold: int = 30):
    logger = logging.getLogger(__name__)
    logger.info(f"Starting RFP scraper for: {target_url}")

    try:
        os.makedirs('data/raw', exist_ok=True)
        os.makedirs('data/processed', exist_ok=True)
        os.makedirs('data/logs', exist_ok=True)

        rfp_crew = RfpScraperCrew()

        inputs = {
            'target_url': target_url,
            'days_threshold': days_threshold
        }

        result = rfp_crew.crew().kickoff(inputs=inputs)
        logger.info("Scraping completed successfully")
        return result

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

def run():
    TARGET_URL = "https://nitjsr.ac.in/Tender/All_Tenders"  # You can replace this dynamically
    return run_rfp_scraper(TARGET_URL, days_threshold=30)

if __name__ == '__main__':
    run()


