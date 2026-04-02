import json
import argparse
import os
import sys
import time
from google import genai
from dotenv import load_dotenv

# Load .env file explicitly from the project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

AGENT_TEAM_FILE = "/var/www/html/development-agent-team/agents/team.json"
TESTING_WORKSPACE = "/var/www/html/development-agent-team/testing"

def load_agents():
    if not os.path.exists(AGENT_TEAM_FILE):
        print(f"Error: Agent file not found at {AGENT_TEAM_FILE}")
        sys.exit(1)
    with open(AGENT_TEAM_FILE, 'r') as f:
        return json.load(f)

def setup_gemini():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        print("Please check your .env file in the root directory.")
        sys.exit(1)
    
    try:
        # Initialize the new Google GenAI client
        client = genai.Client(api_key=api_key)
        
        # Test model availability with 2026-era models
        models_to_try = [
            "gemini-2.0-flash", 
            "gemini-2.5-flash", 
            "gemini-3.0-flash",
            "gemini-3.1-flash-lite-preview",
            "gemini-3.1-pro-preview"
        ]
        for model_name in models_to_try:
            try:
                client.models.generate_content(model=model_name, contents="test")
                print(f"✅ Successfully initialized with model: {model_name}")
                return client, model_name
            except Exception:
                continue
                
        print("Error: Could not find any supported Gemini models (2.0-flash, 1.5-flash, or 1.5-pro).")
        sys.exit(1)
    except Exception as e:
        print(f"Error initializing Google GenAI client: {e}")
        sys.exit(1)

def call_llm(client, model_name, system_prompt, user_input, is_json=False):
    full_prompt = f"SYSTEM: {system_prompt}\n\nUSER: {user_input}"
    try:
        if is_json:
            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt,
                config={"response_mime_type": "application/json"}
            )
        else:
            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt
            )
        return response.text.strip()
    except Exception as e:
        return f"Error calling LLM: {e}"

def list_agents():
    agents = load_agents()
    print("Available AI Agents:")
    print("-" * 50)
    for agent_id, agent_data in agents.items():
        print(f"- {agent_id:25} | Name: {agent_data['name']}")

def show_agent(agent_id):
    agents = load_agents()
    if agent_id not in agents:
        print(f"Error: Agent ID '{agent_id}' not found.")
        sys.exit(1)
    
    agent = agents[agent_id]
    print(f"Agent ID: {agent['id']}")
    print(f"Name:     {agent['name']}")
    print(f"Role:     {agent['role']}")
    print("\nResponsibilities:")
    for res in agent['responsibilities']:
        print(f" - {res}")
    print("-" * 50)
    print("\nRole Prompt:")
    print(agent['prompt'])

def run_agent(agent_id, task):
    agents = load_agents()
    if agent_id not in agents:
        print(f"Error: Agent ID '{agent_id}' not found.")
        sys.exit(1)
    
    agent = agents[agent_id]
    print(f"### SYSTEM PROMPT for {agent['name']} ###\n")
    print(agent['prompt'])
    print("\n" + "=" * 50 + "\n")
    print(f"### USER TASK ###\n")
    print(f"Task: {task}")

def save_agent_files(content):
    import re
    # Look for [FILE: filename] ... [END_FILE] patterns
    pattern = r"\[FILE:\s*(.*?)\](.*?)\[END_FILE\]"
    matches = re.finditer(pattern, content, re.DOTALL)
    for match in matches:
        filename = match.group(1).strip()
        file_content = match.group(2).strip()
        
        # Ensure path is within testing workspace for safety
        if not filename.startswith("testing/"):
            filename = os.path.join("testing", filename)
            
        full_path = os.path.join("/var/www/html/development-agent-team", filename)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w") as f:
            f.write(file_content)
        print(f"💾 File created: {filename}")

def autonomous_team_relay(user_request, max_iterations=10):
    # Ensure testing directory exists
    if not os.path.exists(TESTING_WORKSPACE):
        os.makedirs(TESTING_WORKSPACE)
        
    agents = load_agents()
    client, model_name = setup_gemini()
    
    orchestrator = agents["orchestrator_agent"]
    history = []
    
    print(f"\n🚀 Starting autonomous team relay for: '{user_request}'\n")
    print(f"📁 Workspace: {TESTING_WORKSPACE}")
    print("=" * 60)

    for i in range(max_iterations):
        print(f"\n[Iteration {i+1}] Calling Orchestrator (Dhruv Patel)...")
        
        # Prepare context for orchestrator
        context = f"User Request: {user_request}\n\n"
        context += f"Your current workspace for all work products is: {TESTING_WORKSPACE}\n"
        context += "To CREATE or UPDATE a file, use: [FILE: filename] content [END_FILE]\n\n"
        
        if history:
            context += "History of actions taken so far:\n"
            for entry in history:
                context += f"- Agent: {entry['agent_id']}\n  Result: {entry['result']}\n"
        else:
            context += "This is the start of the mission."

        # Get orchestrator decision
        resp_json = call_llm(client, model_name, orchestrator["prompt"], context, is_json=True)
        try:
            decision = json.loads(resp_json)
        except Exception as e:
            print(f"Error parsing orchestrator response: {e}")
            print(f"Raw response: {resp_json}")
            break

        print(f"Thought: {decision.get('thought', 'No thought provided.')}")
        
        if decision.get("action") == "DONE":
            # Check for final file creation in summary
            save_agent_files(decision.get('final_summary', ''))
            print("\n✅ MISSION COMPLETE!")
            print(f"Final Summary: {decision.get('final_summary')}")
            break
        
        if decision.get("action") == "CALL":
            target_agent_id = decision.get("agent_id")
            task = decision.get("task")
            
            if target_agent_id not in agents:
                print(f"Error: Orchestrator tried to call unknown agent: {target_agent_id}")
                break
                
            target_agent = agents[target_agent_id]
            print(f"\n📢 Calling {target_agent['name']} ({target_agent_id}) for task:")
            print(f"Task: {task}")
            
            # Get target agent's response
            result = call_llm(client, model_name, target_agent["prompt"], task)
            print(f"\n📥 Received Response from {target_agent['name']}:")
            print(f"{result[:500]}{'...' if len(result) > 500 else ''}")
            
            # Save any files created by the agent
            save_agent_files(result)
            
            # Store in history
            history.append({
                "agent_id": target_agent_id,
                "task": task,
                "result": result
            })
            
            print("\n" + "-" * 40)
        else:
            print(f"Unknown action: {decision.get('action')}")
            break
    else:
        print("\n⚠️ Maximum iterations reached. Workflow ended prematurely.")

def main():
    parser = argparse.ArgumentParser(description="AI Agent Team CLI Helper")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List command
    subparsers.add_parser("list", help="List all available agents")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show details of a specific agent")
    show_parser.add_argument("agent_id", help="The ID of the agent to show")

    # Run command
    run_parser = subparsers.add_parser("run", help="Generate a prompt for an agent task (Manual)")
    run_parser.add_argument("agent_id", help="The ID of the agent")
    run_parser.add_argument("task", help="The task description")

    # Team command (Autonomous)
    team_parser = subparsers.add_parser("team", help="Run the autonomous team relay")
    team_parser.add_argument("request", help="The full user request/topic for the team to handle")
    team_parser.add_argument("--max", type=int, default=10, help="Maximum iterations (default 10)")

    args = parser.parse_args()

    if args.command == "list":
        list_agents()
    elif args.command == "show":
        show_agent(args.agent_id)
    elif args.command == "run":
        run_agent(args.agent_id, args.task)
    elif args.command == "team":
        autonomous_team_relay(args.request, args.max)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
