#!/usr/bin/env python3
"""
JamesOS v0.2 - The Fabulous Local Project Command Centre.
A local, money-focused, momentum-driven personal OS for project tracking.
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

REQUIRED_PROJECT_FIELDS = [
    "name",
    "code_name",
    "repo_url",
    "purpose",
    "status",
    "completion_percent",
    "momentum_score",
    "fun_score",
    "revenue_score",
    "current_blocker",
    "next_task",
    "next_milestone",
    "fastest_route_to_revenue",
    "time_to_first_sale",
    "time_to_100",
    "time_to_1000",
    "risk_level",
    "last_updated",
]


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
    if not filename:
        print(f"Unknown project: {key}")
        sys.exit(1)
    path = PROJECTS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


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


def load_all_projects():
    return {key: load_project(key) for key in PROJECT_FILES}


def pick_best_project(projects):
    return max(
        projects.items(),
        key=lambda item: item[1].get("momentum_score", 0) + item[1].get("revenue_score", 0),
    )


def cmd_status():
    print_header("JAMESOS STATUS - Portfolio Overview")
    projects = load_all_projects()

    print("\nPORTFOLIO SNAPSHOT")
    for p in projects.values():
        print(
            f"  - {p['name']} ({p['code_name']}) - "
            f"{p['completion_percent']}% | Momentum: {p['momentum_score']}/100 | "
            f"Fun: {p['fun_score']}/100 | Revenue: {p['revenue_score']}/100"
        )

    best_key, best = pick_best_project(projects)

    print_section("CURRENT PRIORITY", f"{best['name']} - {best['next_task']}")
    print_section("BIGGEST OVERALL BLOCKER", best["current_blocker"])

    print("\nMONEY FIRST VIEW")
    for p in projects.values():
        print(
            f"  {p['name']}: time to first sale: {p.get('time_to_first_sale', 'TBD')} | "
            f"Fastest revenue: {p['fastest_route_to_revenue'][:70]}..."
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
        print("Only codex prompts are supported in v0.2")
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
- README and setup documentation
- Tests or build configuration

TESTS TO RUN:
Create or run the smallest possible test that proves the core flow works.

EXPECTED OUTPUT:
A working {project['next_milestone']}

COMMIT INSTRUCTIONS:
Make small, focused commits.
Suggested commit message: "feat: move {project['name']} toward first paying user"
Do not over-engineer. Do not rebuild from scratch.

REPORT FORMAT:
After you are done, tell me:
- Files changed
- What was completed
- What is now possible that was not before
- Tests run
- Next smallest step
- Any blockers or risks

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
        print(f"  {p['name']}: {p['momentum_score']}/100 - {p['next_task'][:70]}...")

    best = max(projects, key=lambda x: x["momentum_score"] + x["revenue_score"])
    print(f"\nHIGHEST MOMENTUM + REVENUE: {best['name']}")
    print(f"   Action: {best['next_task']}")


def cmd_doctor():
    print_header("JAMESOS DOCTOR - System Health Check")
    issues = []
    score = 100

    required_folders = [
        STATE_DIR,
        PROJECTS_DIR,
        LOGS_DIR.parent,
        BASE_DIR / "memory",
        BASE_DIR / "prompts",
        BASE_DIR / "prompts" / "codex",
        BASE_DIR / ".vscode",
    ]

    for folder in required_folders:
        if not folder.exists():
            issues.append(f"Missing folder: {folder}")
            score -= 10

    required_files = [
        BASE_DIR / "README.md",
        BASE_DIR / "james.py",
        BASE_DIR / ".vscode" / "tasks.json",
    ]

    for file_path in required_files:
        if not file_path.exists():
            issues.append(f"Missing file: {file_path}")
            score -= 10

    for filename in PROJECT_FILES.values():
        path = PROJECTS_DIR / filename
        if not path.exists():
            issues.append(f"Missing project file: {filename}")
            score -= 15
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            issues.append(f"Broken JSON: {filename}")
            score -= 20
            continue

        for field in REQUIRED_PROJECT_FIELDS:
            if field not in data:
                issues.append(f"{filename} missing field: {field}")
                score -= 3

    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        test_path = LOGS_DIR / ".write-test"
        test_path.write_text("ok", encoding="utf-8")
        test_path.unlink()
    except OSError:
        issues.append("Logs folder is not writable")
        score -= 15

    score = max(0, min(100, score))
    print(f"\nSYSTEM HEALTH SCORE: {score}/100")

    if issues:
        print("\nISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nFix the listed items, then run: python james.py doctor")
    else:
        print("Everything looks healthy. You're good to go, darling.")

    append_to_daily_log(f"**Doctor run.** Health score: {score}/100")


def cmd_update(project_key, field, value):
    project = load_project(project_key)
    old_value = project.get(field, "N/A")

    if value.isdigit():
        parsed_value = int(value)
    else:
        try:
            parsed_value = float(value)
        except ValueError:
            parsed_value = value

    if field not in project:
        print(f"Field '{field}' was not found in {project['name']}. Adding it anyway.")

    project[field] = parsed_value
    project["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    save_project(project_key, project)

    print(f"Updated {project['name']}")
    print(f"   {field}: {old_value} -> {parsed_value}")
    append_to_daily_log(f"**Updated** {project['name']} - {field}: {old_value} -> {parsed_value}")


def cmd_win(description):
    wins_path = BASE_DIR / "memory" / "wins.md"
    wins_path.parent.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H:%M")

    if not wins_path.exists():
        wins_path.write_text("# JamesOS Wins\n\n", encoding="utf-8")

    with open(wins_path, "a", encoding="utf-8") as f:
        f.write(f"- **{today} {timestamp}** - {description}\n")

    append_to_daily_log(f"**WIN:** {description}")

    print("WIN RECORDED")
    print("Momentum increased. Keep going, you fabulous thing.")


def cmd_review():
    print_header("JAMESOS WEEKLY EXECUTIVE REPORT")
    projects = load_all_projects()

    to_push = []
    to_pause = []
    to_kill = []

    for p in projects.values():
        combined = p.get("momentum_score", 0) + p.get("revenue_score", 0)
        if combined >= 90:
            to_push.append(p["name"])
        elif p.get("momentum_score", 0) < 25:
            to_pause.append(p["name"])
        elif p.get("revenue_score", 0) < 30 and p.get("completion_percent", 0) < 15:
            to_kill.append(p["name"])

    print("\nPROJECTS TO PUSH")
    for name in to_push or ["None right now"]:
        print(f"  - {name}")

    print("\nPROJECTS TO PAUSE")
    for name in to_pause or ["None"]:
        print(f"  - {name}")

    print("\nPROJECTS TO KILL")
    for name in to_kill or ["None"]:
        print(f"  - {name}")

    best_revenue = max(projects.values(), key=lambda x: x.get("revenue_score", 0))

    print("\nFASTEST ROUTE TO REVENUE")
    print(f"  {best_revenue['name']}: {best_revenue['fastest_route_to_revenue']}")

    print("\nBIGGEST RISK")
    print(f"  {best_revenue['current_blocker']}")

    print("\nRECOMMENDED NEXT 10 HOURS")
    print(f"  Focus on {best_revenue['name']} -> {best_revenue['next_task']}")

    print("\nRECOMMENDED NEXT 20 HOURS")
    print(f"  Complete the current milestone on {best_revenue['name']} and review progress.")

    append_to_daily_log("**Weekly executive review generated.**")


def cmd_money():
    print_header("JAMESOS MONEY MODE - Revenue Focus")
    projects = [load_project(k) for k in PROJECT_FILES]
    best = max(projects, key=lambda x: x.get("revenue_score", 0))

    print("\nFastest route to GBP 100")
    print(f"  {best['name']}: {best['fastest_route_to_revenue']}")
    print(f"  Estimated time: {best.get('time_to_first_sale', 'TBD')}")

    print("\nFastest route to GBP 1,000")
    print(f"  Continue scaling {best['name']} after the first sales.")

    print("\nFastest route to GBP 10,000")
    print(f"  Expand {best['name']} and launch one more high-revenue project.")

    print("\nMOST VALUABLE NEXT STEP")
    print(f"  {best['next_task']}")

    append_to_daily_log("**Money mode run.** Focused on revenue paths.")


def main():
    if len(sys.argv) < 2:
        print("JamesOS v0.2 - Your Fabulous Local Command Centre")
        print("\nUsage:")
        print("  python james.py status")
        print("  python james.py next")
        print("  python james.py doctor")
        print("  python james.py review")
        print("  python james.py money")
        print("  python james.py project [chipos|doorin5|evidence|inventory]")
        print("  python james.py update [project] [field] [value]")
        print("  python james.py win \"description of win\"")
        print("  python james.py prompt codex [chipos|doorin5|evidence|inventory]")
        print("  python james.py log \"what you did\"")
        print("  python james.py momentum")
        return

    cmd = sys.argv[1].lower()

    if cmd == "status":
        cmd_status()
    elif cmd == "next":
        cmd_next()
    elif cmd == "doctor":
        cmd_doctor()
    elif cmd == "review":
        cmd_review()
    elif cmd == "money":
        cmd_money()
    elif cmd == "project":
        if len(sys.argv) < 3:
            print("Please specify a project: chipos, doorin5, evidence, inventory")
            return
        cmd_project(sys.argv[2].lower())
    elif cmd == "update":
        if len(sys.argv) < 5:
            print("Usage: python james.py update [project] [field] [value]")
            print("Example: python james.py update doorin5 momentum_score 45")
            return
        cmd_update(sys.argv[2].lower(), sys.argv[3], " ".join(sys.argv[4:]))
    elif cmd == "win":
        if len(sys.argv) < 3:
            print("Usage: python james.py win \"description\"")
            return
        cmd_win(" ".join(sys.argv[2:]))
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
