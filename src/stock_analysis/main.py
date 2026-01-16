import sys
from crew import StockAnalysisCrew
from memory_listener import StockMemoryListener

def run():
    print("## Welcome to Stock Analysis Crew")
    print('-------------------------------')
    company = input("What is the company you want to analyze? ")
    
    inputs = {
        'query': f'Analyze {company} stock and provide investment recommendations',
        'company_stock': company,
    }
    
    st_crew = StockAnalysisCrew().crew()
    
    # Attach memory listener
    listener = StockMemoryListener()
    # Assuming the crew exposes the event bus via an attribute or we can attach to it.
    if hasattr(st_crew, 'event_bus'):
        listener.setup_listeners(st_crew.event_bus)
    
    # -- Continuous Monitoring Integration --
    monitor_choice = input("Do you want to enable continuous monitoring for news updates? (y/n): ").lower()
    
    if monitor_choice == 'y':
        from scout_monitor import ScoutMonitor
        import time
        from threading import Event
        
        stop_event = Event()
        
        def on_new_updates(ticker):
             print(f"\n[Monitor] Triggering analysis for {ticker} due to new updates...")
             # Re-run the crew. Note: kick() might block, so this callback is effectively synchronous if run in main thread,
             # but ScoutMonitor calls it from its thread.
             # We need to make sure we don't have overlapping executions if they take longer than poll interval.
             # For simplicity now, we just run it. A lock exists inside ScoutMonitor loop implicit by wait, 
             # but here we are in a callback.
             try:
                 new_inputs = inputs.copy()
                 new_inputs['query'] += f" (Updated analysis triggered at {time.strftime('%H:%M:%S')})"
                 result = st_crew.kickoff(inputs=new_inputs)
                 print("\n" + "#"*20)
                 print(f"## Updated Report for {ticker}")
                 print("#"*20 + "\n")
                 print(result)
             except Exception as e:
                 print(f"Error during continuous execution: {e}")

        monitor = ScoutMonitor(company, on_new_updates)
        monitor.start()
        
        print(f"\nMonitoring started for {company}. Press Ctrl+C to stop.")
        
        # Initial run
        print("\nRunning initial analysis...")
        initial_result = st_crew.kickoff(inputs=inputs)
        print("\n" + "#"*20)
        print("## Initial Report")
        print("#"*20 + "\n")
        print(initial_result)

        try:
             # Keep main thread alive
             while True:
                 time.sleep(1)
        except KeyboardInterrupt:
             print("\nStopping monitor...")
             monitor.stop()
             return "Monitoring stopped."
             
    else:
        return st_crew.kickoff(inputs=inputs)

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'query': 'What is last years revenue',
        'company_stock': 'AMZN',
    }
    try:
        StockAnalysisCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
    
if __name__ == "__main__":
    result = run()
    print("\n\n########################")
    print("## Here is the Report")
    print("########################\n")
    print(result)
