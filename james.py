#!/usr/bin/env python3
"""
JamesOS v0.1 - The Fabulous Local Project Command Centre.
A local, momentum-driven personal OS for project tracking.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
STATE_DIR = BASE_DIR / "state"
PROJECTS_DIR = STATE_DIR / "projects"
LOGS_DIR = BASE_DIR / "logs" / "daily"
PROMPTS_DIR = BASE_DIR / "prompts" / "codex"

PROJECT_FILES = {
    "chipos": "chipos-mark-ii.json",
    "doorin5": "doorin5.json",
    "evidence": "evidence-transcript-core.json",
    "inventory": "inventory-application.json",
}


def load_project(key):
    filename = PROJECT_FILES.get(key)
    if not filename:
        print(f"Unknown project: {key}")
        sys.exit(1)
    path = PROJECTS_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_project(key, data):
    filename = PROJECT_FILES.get(key)
    path = PROJECTS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_today_log_path():
    today = datetime.now().strftime("%Y-%m-%d")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return LOGS_DIR / f"{today}.md"


def append_to_daily_log(text):
    path = get_today_log_path()
    with open(path, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%H:%M")
        f.write(f"\n### {timestamp}\n{text}\n")


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_section(title, content):
    print(f"\n{title}")
    print("-" * len(title))
    print(content)


def cmd_status():
    print_header("JAMESOS STATUS - Portfolio Overview")

    projects = {key: load_project(key) for key in PROJECT_FILES}

    print("\nPORTFOLIO SNAPSHOT")
    for p in projects.values():
        print(
            f"  • {p['name']} ({p['code_name']}) - "
            f"{p['completion_percent']}% | Momentum: {p['momentum_score']}/100 | "
            f"Revenue: {p['revenue_score']}/100"
        )

    best_key, best = max(
        projects.items(), key=lambda item: item[1]["momentum_score"] + item[1]["revenue_score"]
    )

    print_section("CURRENT PRIORITY", f"{best['name']} - {best['next_task']}")
    print_section("BIGGEST OVERALL BLOCKER", best["current_blocker"])

    print("\nMONEY FIRST VIEW")
    for p in projects.values():
        print(
            f"  {p['name']}: time to first sale: {p.get('time_to_first_sale', 'TBD')} | "
            f"Fastest revenue: {p['fastest_route_to_revenue'][:60]}..."
        )

    print_section(
        "RECOMMENDED NEXT ACTION",
        f"Focus on {best['name']}. Run: python james.py project {best_key}",
    )

    append_to_daily_log(f"**Status check performed.** Current focus: {best['name']}")


def cmd_next():
    print_header("JAMESOS - NEXT ACTION MODE")

    project = load_project("doorin5")

    print(f"\nCURRENT PRIORITY\n   {project['name']} ({project['code_name']})")
    print(f"\nNEXT TASK\n   {project['next_task']}")
    print("\nESTIMATED TIME\n   2-4 hours to make meaningful progress on the minimum delivery flow")
    print("\nMOMENTUM GAIN\n   High - moving toward real user feedback")
    print("\nWHAT TO IGNORE\n   New feature ideas, architecture cleanup, and scope expansion")
    print("\nNEXT WIN\n   One real person successfully completes a delivery and pays")
    print(f"\nFASTEST ROUTE TO MONEY\n   {project['fastest_route_to_revenue']}")

    append_to_daily_log("**Next action requested.** Focused on Door in 5 minimum delivery flow.")


def cmd_project(key):
    project = load_project(key)
    print_header(f"JAMESOS - {project['name'].upper()}")

    print(f"\nCode Name: {project['code_name']}")
    print(f"Repo: {project['repo_url']}")
    print(f"Purpose: {project['purpose']}")

    print("\nSCORES")
    print(f"  Completion: {project['completion_percent']}%")
    print(f"  Momentum:   {project['momentum_score']}/100")
    print(f"  Fun:        {project['fun_score']}/100")
    print(f"  Revenue:    {project['revenue_score']}/100")
    print(f"  Risk:       {project['risk_level']}")

    print(f"\nCURRENT BLOCKER\n   {project['current_blocker']}")
    print(f"\nNEXT TASK\n   {project['next_task']}")
    print(f"\nNEXT MILESTONE\n   {project['next_milestone']}")
    print(f"\nFASTEST ROUTE TO REVENUE\n   {project['fastest_route_to_revenue']}")
    print(f"   Time to first sale: {project['time_to_first_sale']}")

    append_to_daily_log(f"**Project review:** {project['name']}")


def cmd_prompt(tool, project_key):
    if tool != "codex":
        print("Only codex prompts are supported in v0.1")
        return

    project = load_project(project_key)

    prompt = f"""You are an expert developer helping build {project['name']} ({project['code_name']}).

REPOSITORY: {project['repo_url']}

CURRENT OBJECTIVE:
{project['purpose']}

KNOWN BLOCKER:
{project['current_blocker']}

REQUIRED ACTION:
{project['next_task']}

FILES TO INSPECT:
- Main application entry points
- Current user flow implementation
- Any existing payment or delivery logic

TESTS TO RUN:
Create the smallest possible test that proves the core flow works.

EXPECTED OUTPUT:
A working {project['next_milestone']}

COMMIT INSTRUCTIONS:
Make small, focused commits. Message format: "feat: [what was done] - progress toward first paying user"

REPORT FORMAT:
After you are done, tell me:
- What was completed
- What is now possible that was not before
- Next smallest step
- Any blockers you hit

MONEY-MAKING ANGLE:
{project['fastest_route_to_revenue']}

NEXT LAUNCH MILESTONE:
{project['next_milestone']}

Stay practical. Ship fast. Make it fabulous.
"""

    print(prompt)
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{project_key}-{datetime.now().strftime('%Y%m%d-%H%M')}.txt"
    with open(PROMPTS_DIR / filename, "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"\nPrompt also saved to: prompts/codex/{filename}")


def cmd_log(message):
    append_to_daily_log(message)
    print(f"Logged: {message}")
    print(f"Saved to: {get_today_log_path()}")


def cmd_momentum():
    print_header("JAMESOS MOMENTUM REPORT")
    projects = [load_project(k) for k in PROJECT_FILES]
    print("\nCurrent Momentum Scores:")
    for p in sorted(projects, key=lambda x: -x["momentum_score"]):
        print(f"  {p['name']}: {p['momentum_score']}/100 - {p['next_task'][:50]}...")

    best = max(projects, key=lambda x: x["momentum_score"] + x["revenue_score"])
    print(f"\nHIGHEST MOMENTUM + REVENUE: {best['name']}")
    print(f"   Action: {best['next_task']}")


def main():
    if len(sys.argv) < 2:
        print("JamesOS v0.1 - Your Fabulous Local Command Centre")
        print("\nUsage:")
        print("  python james.py status")
        print("  python james.py next")
        print("  python james.py project [chipos|doorin5|evidence|inventory]")
        print("  python james.py prompt codex [chipos|doorin5|evidence|inventory]")
        print("  python james.py log \"what you did\"")
        print("  python james.py momentum")
        return

    cmd = sys.argv[1].lower()

    if cmd == "status":
        cmd_status()
    elif cmd == "next":
        cmd_next()
    elif cmd == "project":
        if len(sys.argv) < 3:
            print("Please specify a project: chipos, doorin5, evidence, inventory")
            return
        cmd_project(sys.argv[2].lower())
    elif cmd == "prompt":
        if len(sys.argv) < 4:
            print("Usage: python james.py prompt codex [project]")
            return
        cmd_prompt(sys.argv[2].lower(), sys.argv[3].lower())
    elif cmd == "log":
        if len(sys.argv) < 3:
            print("Usage: python james.py log \"message\"")
            return
        cmd_log(" ".join(sys.argv[2:]))
    elif cmd == "momentum":
        cmd_momentum()
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
