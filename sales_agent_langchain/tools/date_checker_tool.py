from langchain.tools import BaseTool
from datetime import datetime
import re
from pydantic import BaseModel, Field


class DateCheckerInput(BaseModel):
    text_content: str
    reference_date: str | None = Field(default=None)
    days_threshold: int = Field(default=30)


def check_rfp_date(text_content: str, reference_date=None, days_threshold=30):
    if reference_date:
        ref_date = datetime.fromisoformat(reference_date)
    else:
        ref_date = datetime.now()

    date_patterns = [
        r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b',
        r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',
    ]
    found_dates = []
    for pattern in date_patterns:
        found_dates += re.findall(pattern, text_content)

    parsed_dates = []
    for ds in found_dates:
        for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y']:
            try:
                parsed_dates.append(datetime.strptime(ds, fmt))
                break
            except ValueError:
                continue

    if not parsed_dates:
        return {"is_new": False, "reason": "No valid dates found."}

    most_recent = max(parsed_dates)
    days_old = (ref_date - most_recent).days
    return {"is_new": days_old <= days_threshold, "most_recent_date": most_recent.isoformat()}


DateCheckerTool = BaseTool.from_function(
    func=check_rfp_date,
    name="RFPDateChecker",
    description="Check if a document is new based on dates in its content.",
    args_schema=DateCheckerInput,
)
