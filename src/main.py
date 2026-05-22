from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()  # must be before importing graph/agents
from tracing import init_langsmith_tracing
init_langsmith_tracing()  # must be before importing graph/agents
from graph import build_graph


if __name__ == "__main__":
 
    app = build_graph()

    state = {
        "pdf_path": "data/SeeWeeS Specialty Dispatch Playbook.pdf",
        "csv_path": "data/Incoming_shipment_03_06.csv",
    }

    config = {"configurable": {"thread_id": "1"}}
    
    print("Running multi-agent graph...")
    # Initial run
    for event in app.stream(state, config, stream_mode="values"):
        pass
        
    current_state = app.get_state(config)
    
    # Check if we were interrupted before 'human_review'
    if current_state.next and current_state.next[0] == "human_review":
        print("\n" + "="*50)
        print("!!! HIGH RISK WEATHER DETECTED !!!")
        print("The system has paused execution for Manager Review.")
        print("="*50 + "\n")
        
        manager_input = input("Manager, please type 'Approve' to proceed or provide feedback: ")
        
        # Inject the feedback and resume
        app.update_state(config, {"manager_feedback": manager_input})
        
        print("\nResuming execution...")
        for event in app.stream(None, config, stream_mode="values"):
            pass

    final = app.get_state(config).values

    report_html = final.get("report_html", "")
    
    with open("report.html", "w", encoding="utf-8") as f:
        f.write(report_html)
        
    print("\n=== REPORT SAVED TO report.html ===\n")
