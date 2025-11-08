"""
Date Checker Tool to identify new RFP documents based on publication date
"""
from crewai.tools import BaseTool
from typing import Type, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import re
import logging


class DateCheckerToolInput(BaseModel):
    """Input schema for DateCheckerTool"""
    text_content: str = Field(..., description="Text content to check for dates")
    reference_date: str = Field(
        default=None,
        description="Reference date in ISO format (YYYY-MM-DD). Defaults to today."
    )
    days_threshold: int = Field(
        default=30,
        description="Number of days to consider a document as 'new'"
    )


class DateCheckerTool(BaseTool):
    name: str = "RFP Date Checker"
    description: str = (
        "Checks if an RFP document is new based on dates found in its content. "
        "Searches for common date patterns and determines if the document was "
        "published within a specified timeframe."
    )
    args_schema: Type[BaseModel] = DateCheckerToolInput

    def _run(
            self,
            text_content: str,
            reference_date: str = None,
            days_threshold: int = 30
    ) -> Dict:
        """
        Check if document is new based on dates in content

        Args:
            text_content: The text content to analyze
            reference_date: Reference date to compare against (defaults to today)
            days_threshold: Number of days to consider document as new

        Returns:
            Dictionary with analysis results
        """
        try:
            # Set reference date
            if reference_date:
                ref_date = datetime.fromisoformat(reference_date)
            else:
                ref_date = datetime.now()

            # Common date patterns to search for
            date_patterns = [
                r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
                r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b',
                r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',
                r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',
            ]

            found_dates = []

            # Search for dates
            for pattern in date_patterns:
                matches = re.finditer(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    found_dates.append(match.group())

            # Parse and sort dates
            parsed_dates = []
            for date_str in found_dates:
                try:
                    # Try multiple parsing formats
                    for fmt in ['%B %d, %Y', '%B %d %Y', '%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%b %d, %Y']:
                        try:
                            parsed_date = datetime.strptime(date_str.strip(), fmt)
                            parsed_dates.append(parsed_date)
                            break
                        except ValueError:
                            continue
                except Exception:
                    continue

            if not parsed_dates:
                return {
                    'is_new': False,
                    'reason': 'No valid dates found in document',
                    'found_dates': found_dates,
                    'success': True
                }

            # Find most recent date
            most_recent = max(parsed_dates)
            days_old = (ref_date - most_recent).days

            is_new = days_old <= days_threshold

            return {
                'is_new': is_new,
                'most_recent_date': most_recent.isoformat(),
                'days_old': days_old,
                'threshold_days': days_threshold,
                'found_dates': found_dates,
                'parsed_dates': [d.isoformat() for d in parsed_dates],
                'success': True
            }

        except Exception as e:
            logging.error(f"Error checking dates: {str(e)}")
            return {
                'is_new': False,
                'error': str(e),
                'success': False
            }
