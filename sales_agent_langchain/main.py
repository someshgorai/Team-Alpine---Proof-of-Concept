from graph import rfp_graph

if __name__ == "__main__":
    inputs = {"target_url": "https://nitjsr.ac.in/Tender/All_Tenders"}
    result = rfp_graph.invoke(inputs)
    print("\n=== Final RFP Report ===\n")
    print(result["analyzed_report"])
