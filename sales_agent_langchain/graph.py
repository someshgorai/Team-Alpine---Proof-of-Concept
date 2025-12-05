from langgraph.graph import StateGraph, END

from agents import rfp_analyst_agent, pdf_processor_agent, rfp_finder_agent


# State holds intermediate results
class RFPState(dict):
    target_url: str
    pdf_links: list
    extracted_data: list
    analyzed_report: dict

graph = StateGraph(RFPState)

def discover_links(state: RFPState):
    result = rfp_finder_agent.invoke({"input": f"Find RFP PDF links from {state['target_url']}"})
    return {"pdf_links": result["output"].split("\n")}

def extract_and_check(state: RFPState):
    extracted = []
    for link in state["pdf_links"]:
        pdf_data = pdf_processor_agent.invoke({"input": f"Download and extract data from {link}"})
        extracted.append(pdf_data["output"])
    return {"extracted_data": extracted}

def analyze_rfps(state: RFPState):
    data_summary = rfp_analyst_agent.invoke({
        "input": f"Analyze the following RFP data and summarize key deadlines and requirements: {state['extracted_data']}"
    })
    return {"analyzed_report": data_summary["output"]}

graph.add_node("discover_links", discover_links)
graph.add_node("extract_and_check", extract_and_check)
graph.add_node("analyze_rfps", analyze_rfps)

graph.add_edge("discover_links", "extract_and_check")
graph.add_edge("extract_and_check", "analyze_rfps")
graph.add_edge("analyze_rfps", END)

graph.set_entry_point("discover_links")
rfp_graph = graph.compile()
