import ollama
import json
import re
from environment import AdvancedDevOpsEnvironment

def extract_json(text):
    # in case json is wrapped in ```json...```
    backticks = chr(96) * 3
    pattern = rf'{backticks}(?:json)?(.*?){backticks}'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, func):
        self.tools[func.__name__] = func
        return func

    def get_tool_schemas(self):
        return [{"name": name, "description": func.__doc__} for name, func in self.tools.items()]

    def execute(self, tool_name, kwargs):
        if tool_name not in self.tools:
            return f"Error: Tool {tool_name} not found."
        return self.tools[tool_name](**kwargs)

class StemAgent:
    def __init__(self, registry):
        self.registry = registry
        # The Memory System
        self.episodic_memory = [] 
        self.procedural_skills = [] #crystallized rules
        
        self.base_prompt = """
        You are an autonomous SRE Agent. Diagnose and resolve the user's alert.
        Available tools: {tools}
        
        If you have procedural skills listed below, prioritize them!
        ACQUIRED SKILLS: {skills}
        
        Output ONLY valid JSON: {"thought": "reasoning", "tool": "tool_name", "args": {"arg1": "val1"}}
        """

    def _get_system_prompt(self):
        return self.base_prompt.format(
            tools=json.dumps(self.registry.get_tool_schemas()),
            skills="\n".join(self.procedural_skills) if self.procedural_skills else "None"
        )

    def process_task(self, alert_text):
        print(f"\n[NEW ALERT] {alert_text}")
        messages = [
            {'role': 'system', 'content': self._get_system_prompt()},
            {'role': 'user', 'content': f"Resolve this alert: {alert_text}"}
        ]
        
        episode_steps = []
        is_resolved = False
        step_count = 0
        
        while not is_resolved and step_count < 8:
            step_count += 1
            response = ollama.chat(model='qwen2.5-coder:3b', messages=messages)
            assistant_reply = response['message']['content'].strip()
            messages.append({'role': 'assistant', 'content': assistant_reply})
            
            try:
                action = json.loads(extract_json(assistant_reply))
                tool_name = action.get('tool')
                args = action.get('args', {})
                
                print(f"THOUGHT: {action.get('thought')}")
                print(f"ACTION: {tool_name}({args})")
                
                episode_steps.append({"tool": tool_name, "args": args})
                
                # Execute tool
                observation = self.registry.execute(tool_name, args)
                print(f"SYSTEM: {observation}")
                
                if "TICKET CLOSED" in observation or "SUCCESS" in observation:
                    is_resolved = True
                elif "CRITICAL FAILURE" in observation:
                    print("APOTOSIS TRIGGERED: Bad action taken. Aborting task.")
                    break # Fails the task, triggers negative learning
                    
                messages.append({'role': 'user', 'content': f"Observation: {observation}. Next action?"})
                
            except Exception as e:
                print(f"FORMAT ERROR. Retrying...")
                messages.append({'role': 'user', 'content': "Invalid JSON. Output strictly JSON."})

        # Save to memory and attempt crystallization
        self.episodic_memory.append({
            "alert": alert_text, 
            "steps": episode_steps, 
            "success": is_resolved
        })
        self.try_crystallize()
        return is_resolved, step_count

    def try_crystallize(self):
        """Analyzes memory to find branching logic and create procedural rules."""
        successful_episodes = [ep for ep in self.episodic_memory if ep["success"]]
        
        # Need at least 3 successes to spot a pattern
        if len(successful_episodes) < 3:
            return
            
        print("[MEMORY CONSOLIDATION] Analyzing recent successes for patterns...")
        memory_dump = json.dumps([{"alert": ep["alert"], "path": ep["steps"]} for ep in successful_episodes[-3:]])
        
        meta_prompt = f"""
        Review these successful task resolutions:
        {memory_dump}
        
        Identify the optimal diagnostic path. Write a SINGLE sentence rule that tells the agent 
        what tool to use FIRST to determine the root cause, and what to do based on that result.
        If the cases are totally unrelated, reply "NO_PATTERN".
        """
        
        response = ollama.chat(model='qwen2.5-coder:3b', messages=[{'role': 'user', 'content': meta_prompt}])
        new_rule = response['message']['content'].strip()
        
        if "NO_PATTERN" not in new_rule.upper() and new_rule not in self.procedural_skills:
            print(f"NEW EMERGENT SKILL DISCOVERED: {new_rule}")
            self.procedural_skills.append(f"RULE: {new_rule}")
            # Clear episodic memory to start looking for the next distinct pattern
            self.episodic_memory = []