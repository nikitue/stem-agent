from environment import AdvancedDevOpsEnvironment
from agent import ToolRegistry, StemAgent

def run_simulation():
    print("Initializing STEM Agent Evaluation...")
    
    # Instantiate a new environment for each task so the root cause randomizes,
    # but we keep the same agent so it retains its memory and skills.
    
    # Setup the initial registry to pass to the agent
    dummy_env = AdvancedDevOpsEnvironment()
    registry = ToolRegistry()
    registry.register(dummy_env.trace_dependencies)
    registry.register(dummy_env.query_metrics)
    registry.register(dummy_env.check_recent_deployments)
    registry.register(dummy_env.search_runbooks)
    registry.register(dummy_env.rollback_deployment)
    registry.register(dummy_env.scale_up_cache)
    registry.register(dummy_env.resolve_ticket)
    
    agent = StemAgent(registry=registry)
    metrics = {
        "Progenitor": {"episodes": 0, "successes": 0, "steps": [], "runbook_reads": 0, "errors": 0},
        "Specialist": {"episodes": 0, "successes": 0, "steps": [], "runbook_reads": 0, "errors": 0}
    }

    # Run 6 simulated alerts
    for i in range(1, 7):
        print(f"\n EPISODE {i}\n")
        
        # Fresh environment (randomizes the root cause)
        env = AdvancedDevOpsEnvironment()
        
        # Re-bind the registry to the new environment instance for this episode
        registry.tools.clear()
        registry.register(env.trace_dependencies)
        registry.register(env.query_metrics)
        registry.register(env.check_recent_deployments)
        registry.register(env.search_runbooks)
        registry.register(env.rollback_deployment)
        registry.register(env.scale_up_cache)

        alert = env.active_alerts[0]
        
        # Check agent state before task
        state = "Specialist" if len(agent.procedural_skills) > 0 else "Progenitor"

        # Track initial memory to see what happens in this episode
        initial_memory_length = len(agent.episodic_memory)
        is_resolved, steps = agent.process_task(alert)

        # Gather episode stats
        runbook_reads = 0
        if len(agent.episodic_memory) > initial_memory_length:
            latest_episode = agent.episodic_memory[-1]
            runbook_reads = sum(1 for step in latest_episode["steps"] if step.get("tool") == "search_runbooks")
    
        # Record Metrics
        metrics[state]["episodes"] += 1
        metrics[state]["steps"].append(steps)
        metrics[state]["runbook_reads"] += runbook_reads
        if is_resolved:
            metrics[state]["successes"] += 1
        else:
            metrics[state]["errors"] += 1
    
    # --- Print Evaluation Report ---
    print("\n--- EVALUATION REPORT ---")
    for state in ["Progenitor", "Specialist"]:
        data = metrics[state]
        if data["episodes"] > 0:
            success_rate = (data["successes"] / data["episodes"]) * 100
            avg_steps = sum(data["steps"]) / data["episodes"]
            avg_runbook = data["runbook_reads"] / data["episodes"]
            
            print(f"\n[{state.upper()} PHASE]")
            print(f"  Total Episodes:     {data['episodes']}")
            print(f"  Success Rate:       {success_rate:.1f}%")
            print(f"  Avg Steps/Task:     {avg_steps:.1f}")
            print(f"  Runbook Reliance:   {avg_runbook:.1f} reads/task")
            print(f"  Critical Failures:  {data['errors']}")

if __name__ == "__main__":
    run_simulation()