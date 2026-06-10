#!/usr/bin/env python3
"""
JamesOS v0.4 - local project command centre and money-sniffer assistant.

Safe design: JamesOS can think, plan, score opportunities, write local files,
generate prompts, and run harmless git status checks. It does not spend, trade,
move funds, contact people, or run destructive commands.
"""

import html
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
STATE_DIR = BASE_DIR / "state"
PROJECTS_DIR = STATE_DIR / "projects"
LOGS_DIR = BASE_DIR / "logs" / "daily"
PROMPTS_DIR = BASE_DIR / "prompts" / "codex"
MEMORY_DIR = BASE_DIR / "memory"
AGENT_FILE = STATE_DIR / "agent.json"
URGENT_FILE = MEMORY_DIR / "urgent_actions.md"
DASHBOARD_FILE = BASE_DIR / "dashboard.html"

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

DEFAULT_AGENT = {
    "agent_name": "JamesOS Agent",
    "version": "0.4",
    "current_mode": "advisor",
    "current_money_target": "£100",
    "current_primary_project": "doorin5",
    "current_secondary_project": "evidence",
    "today_mission": None,
    "last_mission_date": None,
    "last_focus_action": None,
    "autonomy_level": "advisor",
    "machine_id": "local-machine",
    "machine_name": "JamesOS Local Node",
    "machine_role": "builder",
    "network_mode": "local_only",
    "commander_machine": "manual",
    "last_check_in": None,
    "assigned_projects": ["doorin5"],
    "allowed_actions": [
        "read local project state",
        "write local logs",
        "generate prompts",
        "generate dashboard",
        "suggest actions",
        "run safe git status checks",
        "queue approval-required actions",
    ],
    "blocked_actions": [
        "spending",
        "trading",
        "fund transfers",
        "customer contact without approval",
        "account access",
        "destructive git commands",
        "file deletion without approval",
    ],
}


def ensure_dirs():
    for path in [STATE_DIR, PROJECTS_DIR, LOGS_DIR, PROMPTS_DIR, MEMORY_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def load_json(path, default):
    if not path.exists():
        save_json(path, default)
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def load_agent():
    return load_json(AGENT_FILE, DEFAULT_AGENT)


def save_agent(agent):
    agent["last_check_in"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_json(AGENT_FILE, agent)


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
    save_json(PROJECTS_DIR / filename, data)


def load_all_projects():
    return {key: load_project(key) for key in PROJECT_FILES}


def pick_best_project(projects):
    return max(
        projects.items(),
        key=lambda item: item[1].get("momentum_score", 0) + item[1].get("revenue_score", 0),
    )


def today_log_path():
    ensure_dirs()
    return LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"


def append_log(text):
    path = today_log_path()
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n### {datetime.now().strftime('%H:%M')}\n{text}\n")


def header(text):
    print("\n" + "=" * 64)
    print(f"  {text}")
    print("=" * 64)


def section(title, body):
    print(f"\n{title}")
    print("-" * len(title))
    print(body)


def safe_git(args):
    allowed = {
        ("branch", "--show-current"),
        ("status", "--short"),
        ("log", "--oneline", "-1"),
    }
    tup = tuple(args)
    if tup not in allowed:
        return "Blocked: unsafe git command"
    try:
        return subprocess.check_output(["git", *args], cwd=BASE_DIR, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"Git check failed: {exc}"


def cmd_status():
    header("JAMESOS STATUS - Portfolio Overview")
    projects = load_all_projects()
    print("\nPORTFOLIO SNAPSHOT")
    for p in projects.values():
        print(
            f"  - {p['name']} ({p['code_name']}) - {p['completion_percent']}% | "
            f"Momentum: {p['momentum_score']}/100 | Fun: {p['fun_score']}/100 | "
            f"Revenue: {p['revenue_score']}/100"
        )
    best_key, best = pick_best_project(projects)
    section("CURRENT PRIORITY", f"{best['name']} - {best['next_task']}")
    section("BIGGEST OVERALL BLOCKER", best["current_blocker"])
    print("\nMONEY FIRST VIEW")
    for p in projects.values():
        print(f"  {p['name']}: {p.get('time_to_first_sale', 'TBD')} | {p['fastest_route_to_revenue']}")
    section("RECOMMENDED NEXT ACTION", f"Run: python james.py project {best_key}")
    append_log(f"**Status check performed.** Current focus: {best['name']}")


def cmd_next():
    header("JAMESOS - NEXT ACTION MODE")
    projects = load_all_projects()
    _, p = pick_best_project(projects)
    print(f"\nCURRENT PRIORITY\n   {p['name']} ({p['code_name']})")
    print(f"\nNEXT TASK\n   {p['next_task']}")
    print("\nESTIMATED TIME\n   30-120 minutes for a visible step")
    print("\nMOMENTUM GAIN\n   High if it moves toward users, launch, or revenue")
    print("\nWHAT TO IGNORE\n   Extra features, dashboards, and new project ideas")
    print(f"\nNEXT WIN\n   {p['next_milestone']}")
    print(f"\nFASTEST ROUTE TO MONEY\n   {p['fastest_route_to_revenue']}")
    append_log(f"**Next action requested.** Focused on {p['name']}.")


def cmd_project(key):
    p = load_project(key)
    header(f"JAMESOS - {p['name'].upper()}")
    print(f"\nCode Name: {p['code_name']}")
    print(f"Repo: {p['repo_url']}")
    print(f"Purpose: {p['purpose']}")
    print("\nSCORES")
    print(f"  Completion: {p['completion_percent']}%")
    print(f"  Momentum:   {p['momentum_score']}/100")
    print(f"  Fun:        {p['fun_score']}/100")
    print(f"  Revenue:    {p['revenue_score']}/100")
    print(f"  Risk:       {p['risk_level']}")
    print(f"\nCURRENT BLOCKER\n   {p['current_blocker']}")
    print(f"\nNEXT TASK\n   {p['next_task']}")
    print(f"\nNEXT MILESTONE\n   {p['next_milestone']}")
    print(f"\nFASTEST ROUTE TO REVENUE\n   {p['fastest_route_to_revenue']}")
    append_log(f"**Project review:** {p['name']}")


def codex_prompt_for_project(project_key):
    if project_key == "agent":
        return """You are improving JamesOS itself.

Current target: ship one useful improvement without over-engineering.

Inspect:
- james.py
- README.md
- CHANGELOG.md
- state/agent.json

Rules:
- keep dependency-free
- keep local-first
- no fake income promises
- no wallet or bank control
- no destructive commands
- ship one useful improvement

Report:
- files changed
- tests run
- next risk
- next smallest improvement
"""
    p = load_project(project_key)
    return f"""You are an expert developer helping build {p['name']} ({p['code_name']}).

REPOSITORY: {p['repo_url']}

CURRENT OBJECTIVE:
{p['purpose']}

KNOWN BLOCKER:
{p['current_blocker']}

REQUIRED ACTION:
{p['next_task']}

FILES TO INSPECT:
- main application entry points
- current user flow implementation
- README and setup documentation
- tests or build configuration

TESTS TO RUN:
Run or create the smallest test that proves the core flow works.

EXPECTED OUTPUT:
{p['next_milestone']}

COMMIT INSTRUCTIONS:
Make small, focused commits. Do not rebuild from scratch.

REPORT FORMAT:
- files changed
- what was completed
- tests run
- next smallest step
- blockers or risks

MONEY ANGLE:
{p['fastest_route_to_revenue']}
"""


def cmd_prompt(tool, project_key):
    if tool != "codex":
        print("Only codex prompts are supported in this version")
        return
    prompt = codex_prompt_for_project(project_key)
    print(prompt)
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{project_key}-{datetime.now().strftime('%Y%m%d-%H%M')}.txt"
    (PROMPTS_DIR / filename).write_text(prompt, encoding="utf-8")
    print(f"\nPrompt saved to: prompts/codex/{filename}")


def cmd_log(message):
    append_log(message)
    print(f"Logged: {message}")


def cmd_win(description):
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    wins = MEMORY_DIR / "wins.md"
    if not wins.exists():
        wins.write_text("# JamesOS Wins\n\n", encoding="utf-8")
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(wins, "a", encoding="utf-8") as f:
        f.write(f"- **{stamp}** - {description}\n")
    append_log(f"**WIN:** {description}")
    print("WIN RECORDED")
    print("Momentum increased. Keep going, you fabulous thing.")


def cmd_momentum():
    header("JAMESOS MOMENTUM REPORT")
    projects = [load_project(k) for k in PROJECT_FILES]
    for p in sorted(projects, key=lambda x: -x["momentum_score"]):
        print(f"  {p['name']}: {p['momentum_score']}/100 - {p['next_task'][:70]}...")
    best = max(projects, key=lambda x: x["momentum_score"] + x["revenue_score"])
    print(f"\nHIGHEST MOMENTUM + REVENUE: {best['name']}")


def cmd_doctor():
    header("JAMESOS DOCTOR - System Health Check")
    issues = []
    score = 100
    for folder in [STATE_DIR, PROJECTS_DIR, MEMORY_DIR, LOGS_DIR.parent, PROMPTS_DIR.parent, BASE_DIR / ".vscode"]:
        if not folder.exists():
            issues.append(f"Missing folder: {folder}")
            score -= 10
    for file_path in [BASE_DIR / "README.md", BASE_DIR / "james.py", BASE_DIR / ".vscode" / "tasks.json", AGENT_FILE]:
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
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            issues.append(f"Broken JSON: {filename}")
            score -= 20
            continue
        for field in REQUIRED_PROJECT_FIELDS:
            if field not in data:
                issues.append(f"{filename} missing field: {field}")
                score -= 2
    score = max(0, min(100, score))
    print(f"\nSYSTEM HEALTH SCORE: {score}/100")
    if issues:
        print("\nISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Everything looks healthy. You're good to go, darling.")
    append_log(f"**Doctor run.** Health score: {score}/100")


def cmd_update(project_key, field, value):
    p = load_project(project_key)
    old = p.get(field, "N/A")
    if value.isdigit():
        new_value = int(value)
    else:
        try:
            new_value = float(value)
        except ValueError:
            new_value = value
    p[field] = new_value
    p["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    save_project(project_key, p)
    print(f"Updated {p['name']}")
    print(f"   {field}: {old} -> {new_value}")
    append_log(f"**Updated** {p['name']} - {field}: {old} -> {new_value}")


def cmd_review():
    header("JAMESOS WEEKLY EXECUTIVE REPORT")
    projects = load_all_projects()
    ranked = sorted(projects.values(), key=lambda p: p["momentum_score"] + p["revenue_score"], reverse=True)
    print("\nPROJECTS TO PUSH")
    for p in ranked[:2]:
        print(f"  - {p['name']}")
    print("\nPROJECTS TO PAUSE")
    for p in ranked[2:]:
        print(f"  - {p['name']}")
    best = max(projects.values(), key=lambda p: p["revenue_score"])
    print(f"\nFASTEST ROUTE TO REVENUE\n   {best['name']}: {best['fastest_route_to_revenue']}")
    print(f"\nRECOMMENDED NEXT 10 HOURS\n   {best['next_task']}")
    append_log("**Weekly Review** generated")


def cmd_money():
    header("JAMESOS MONEY MODE - Revenue Focus")
    projects = sorted(load_all_projects().values(), key=lambda p: p["revenue_score"], reverse=True)
    for idx, p in enumerate(projects, start=1):
        print(f"\n{idx}. {p['name']}")
        print(f"   Revenue score: {p['revenue_score']}/100")
        print(f"   Fastest route: {p['fastest_route_to_revenue']}")
        print(f"   First sale estimate: {p.get('time_to_first_sale', 'TBD')}")
    append_log("**Money Mode** run")


def make_mission():
    projects = load_all_projects()
    key, p = pick_best_project(projects)
    mission = {
        "project_key": key,
        "project": p["name"],
        "mission": p["next_task"],
        "why": "This is the strongest current path toward launch, users, or revenue.",
        "time": "30-120 minutes",
        "money_angle": p["fastest_route_to_revenue"],
        "completion": p["next_milestone"],
        "ignore": "New ideas, extra dashboards, cosmetic work, and refactors that do not unblock users.",
        "next_command": f"python james.py project {key}",
    }
    return mission


def cmd_mission():
    header("JAMESOS DAILY MISSION")
    mission = make_mission()
    print(f"\nPROJECT:\n   {mission['project']}")
    print(f"\nMISSION:\n   {mission['mission']}")
    print(f"\nWHY THIS MATTERS:\n   {mission['why']}")
    print(f"\nESTIMATED TIME:\n   {mission['time']}")
    print(f"\nMONEY ANGLE:\n   {mission['money_angle']}")
    print(f"\nCOMPLETION CONDITION:\n   {mission['completion']}")
    print(f"\nWHAT TO IGNORE:\n   {mission['ignore']}")
    print(f"\nNEXT COMMAND:\n   {mission['next_command']}")
    agent = load_agent()
    agent["today_mission"] = mission
    agent["last_mission_date"] = datetime.now().strftime("%Y-%m-%d")
    save_agent(agent)
    append_log(f"**MISSION** - {mission['project']}: {mission['mission']}")


def cmd_focus():
    projects = load_all_projects()
    _, p = pick_best_project(projects)
    print("\nDO THIS NOW:")
    print(p["next_task"])
    print("\nTIME:")
    print("30-60 minutes")
    print("\nWHY:")
    print("This moves the highest momentum/revenue project closer to a real user or payment.")
    print("\nDO NOT DO:")
    print("Do not start a new feature, new app, or new dashboard right now.")
    print("\nWIN CONDITION:")
    print(p["next_milestone"])
    agent = load_agent()
    agent["last_focus_action"] = p["next_task"]
    save_agent(agent)
    append_log(f"**FOCUS** - {p['next_task']}")


def cmd_gitcheck():
    header("JAMESOS GIT CHECK")
    print(f"Current branch: {safe_git(['branch', '--show-current'])}")
    status = safe_git(["status", "--short"])
    print("\nStatus summary:")
    print(status or "Clean working tree")
    print(f"\nLast commit: {safe_git(['log', '--oneline', '-1'])}")
    if status:
        print("\nLocal changes detected. Review, commit, and push manually when ready.")
    append_log("**Gitcheck** run")


def cmd_dashboard():
    projects = load_all_projects()
    agent = load_agent()
    cards = []
    for p in projects.values():
        cards.append(
            f"""
            <div class='card'>
              <h2>{html.escape(p['name'])}</h2>
              <p><b>{html.escape(p['code_name'])}</b></p>
              <p>Momentum: {p['momentum_score']} | Revenue: {p['revenue_score']} | Fun: {p['fun_score']}</p>
              <p><b>Blocker:</b> {html.escape(p['current_blocker'])}</p>
              <p><b>Next task:</b> {html.escape(p['next_task'])}</p>
              <p><b>Money angle:</b> {html.escape(p['fastest_route_to_revenue'])}</p>
            </div>
            """
        )
    mission = agent.get("today_mission") or make_mission()
    dashboard = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>JamesOS Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; background:#111; color:#f4f4f4; margin:40px; }}
.card {{ background:#1f1f1f; border:1px solid #333; border-radius:12px; padding:18px; margin:14px 0; }}
.money {{ color:#93ff93; }}
</style></head><body>
<h1>JamesOS Dashboard</h1>
<p>Build things. Finish things. Launch things. Make money. Stay fabulous. Repeat.</p>
<div class='card'><h2>Today's Mission</h2><p>{html.escape(mission['project'])}: {html.escape(mission['mission'])}</p><p class='money'>{html.escape(mission['money_angle'])}</p></div>
{''.join(cards)}
</body></html>"""
    DASHBOARD_FILE.write_text(dashboard, encoding="utf-8")
    print(f"Dashboard written to: {DASHBOARD_FILE}")
    append_log("**Dashboard** generated")


def cmd_agent():
    header("JAMESOS AGENT ONLINE")
    projects = load_all_projects()
    key, p = pick_best_project(projects)
    mission = load_agent().get("today_mission") or make_mission()
    print(f"Current priority: {p['name']}")
    print(f"Today's mission: {mission['mission']}")
    print(f"Fastest route to money: {p['fastest_route_to_revenue']}")
    print(f"Biggest blocker: {p['current_blocker']}")
    print(f"Suggested next command: python james.py project {key}")
    print(f"Codex prompt suggestion: python james.py prompt codex {key}")
    while True:
        print("\nWhat do you want to do?")
        print("1. Generate Codex prompt")
        print("2. Log a win")
        print("3. Update project status")
        print("4. Run money mode")
        print("5. Run review mode")
        print("6. Create today's mission")
        print("7. Exit")
        choice = input("> ").strip()
        if choice == "1":
            cmd_prompt("codex", key)
        elif choice == "2":
            cmd_win(input("Win description: ").strip())
        elif choice == "3":
            print("Use: python james.py update PROJECT FIELD VALUE")
        elif choice == "4":
            cmd_money()
        elif choice == "5":
            cmd_review()
        elif choice == "6":
            cmd_mission()
        elif choice == "7":
            print("Agent offline. Go finish something.")
            break
        else:
            print("Choose 1-7.")


def cmd_agent_loop():
    print("JamesOS agent loop. Press Enter to refresh. Ctrl+C to quit.")
    try:
        while True:
            input("\nPress Enter for refresh...")
            cmd_focus()
            cmd_gitcheck()
    except KeyboardInterrupt:
        print("\nAgent loop stopped.")


def cmd_node():
    agent = load_agent()
    header("JAMESOS NODE")
    for field in ["machine_id", "machine_name", "machine_role", "network_mode", "last_check_in", "assigned_projects", "autonomy_level"]:
        print(f"{field}: {agent.get(field)}")


def cmd_assign(project_key):
    if project_key not in PROJECT_FILES:
        print("Unknown project")
        return
    agent = load_agent()
    projects = set(agent.get("assigned_projects", []))
    projects.add(project_key)
    agent["assigned_projects"] = sorted(projects)
    save_agent(agent)
    print(f"Assigned {project_key} to this node")
    append_log(f"**Assigned project to node:** {project_key}")


def cmd_opportunity():
    projects = load_all_projects()
    best = max(projects.values(), key=lambda p: p["revenue_score"])
    header("JAMESOS OPPORTUNITY SNIFFER")
    print(f"Project: {best['name']}")
    print(f"What could make money: {best['fastest_route_to_revenue']}")
    print("First customer: someone with a painful problem this project directly solves")
    print(f"What to build first: {best['next_task']}")
    print("What to ask James: approve one small outreach, test, listing, or demo step")
    print(f"Risk: {best['risk_level']} - {best['current_blocker']}")
    print(f"Next action: {best['next_task']}")
    print("Approval needed: yes, before external contact or spending")
    append_log(f"**Opportunity generated:** {best['name']}")


def cmd_queue_action(description):
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if not URGENT_FILE.exists():
        URGENT_FILE.write_text("# JamesOS Urgent Actions\n\n", encoding="utf-8")
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(URGENT_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n## {stamp}\nAction needed: {description}\nApproval needed: yes\nSuggested next step: review and decide manually.\n")
    print("Action queued for approval")


def cmd_approvals():
    header("JAMESOS APPROVALS")
    if URGENT_FILE.exists():
        print(URGENT_FILE.read_text(encoding="utf-8"))
    else:
        print("No approval queue yet.")


def cmd_deal_sniffer():
    header("JAMESOS DEAL SNIFFER")
    print("This version does not scrape marketplaces automatically.")
    print("It prepares the sniffing brief for safe manual or approved search.")
    print("\nLook for:")
    print("- cheap mini PCs, laptops, monitors, storage, Android phones, XREAL-compatible kit")
    print("- free or underpriced items within driving range")
    print("- items that help Door in 5, Evidence Core, or ChipOS")
    print("\nScore each find:")
    print("profit potential, distance, condition risk, project usefulness, resale speed")
    print("\nNever pay deposits or share codes without manual verification.")
    append_log("**Deal sniffer brief generated**")


def usage():
    print("JamesOS v0.4 - Your local money-sniffing command centre")
    print("\nCommands:")
    for cmd in [
        "status", "next", "doctor", "review", "money", "agent", "mission", "focus",
        "dashboard", "gitcheck", "node", "opportunity", "deal-sniffer", "agent-loop", "momentum"
    ]:
        print(f"  python james.py {cmd}")
    print("  python james.py project [chipos|doorin5|evidence|inventory]")
    print("  python james.py prompt codex [chipos|doorin5|evidence|inventory|agent]")
    print("  python james.py update [project] [field] [value]")
    print("  python james.py win \"description\"")
    print("  python james.py assign [project]")
    print("  python james.py queue-action \"description\"")
    print("  python james.py approvals")


def main():
    ensure_dirs()
    if len(sys.argv) < 2:
        usage()
        return
    cmd = sys.argv[1].lower()
    if cmd == "status": cmd_status()
    elif cmd == "next": cmd_next()
    elif cmd == "doctor": cmd_doctor()
    elif cmd == "review": cmd_review()
    elif cmd == "money": cmd_money()
    elif cmd == "agent": cmd_agent()
    elif cmd == "mission": cmd_mission()
    elif cmd == "focus": cmd_focus()
    elif cmd == "dashboard": cmd_dashboard()
    elif cmd == "gitcheck": cmd_gitcheck()
    elif cmd == "agent-loop": cmd_agent_loop()
    elif cmd == "node": cmd_node()
    elif cmd == "opportunity": cmd_opportunity()
    elif cmd == "deal-sniffer": cmd_deal_sniffer()
    elif cmd == "momentum": cmd_momentum()
    elif cmd == "project" and len(sys.argv) >= 3: cmd_project(sys.argv[2].lower())
    elif cmd == "prompt" and len(sys.argv) >= 4: cmd_prompt(sys.argv[2].lower(), sys.argv[3].lower())
    elif cmd == "log" and len(sys.argv) >= 3: cmd_log(" ".join(sys.argv[2:]))
    elif cmd == "win" and len(sys.argv) >= 3: cmd_win(" ".join(sys.argv[2:]))
    elif cmd == "update" and len(sys.argv) >= 5: cmd_update(sys.argv[2].lower(), sys.argv[3], sys.argv[4])
    elif cmd == "assign" and len(sys.argv) >= 3: cmd_assign(sys.argv[2].lower())
    elif cmd == "queue-action" and len(sys.argv) >= 3: cmd_queue_action(" ".join(sys.argv[2:]))
    elif cmd == "approvals": cmd_approvals()
    else:
        usage()


if __name__ == "__main__":
    main()
