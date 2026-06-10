# JamesOS v0.2 - Your Fabulous Local Command Centre

**Build things. Finish things. Launch things. Make money. Stay fabulous. Repeat.**

JamesOS is a tiny, dependency-free Python CLI that acts as your personal project command centre. It tracks your projects, gives you momentum scores, generates ready-to-paste Codex prompts, and keeps you focused on revenue and shipping.

**New in v0.2:** `doctor`, `update`, `win`, `review`, and `money` commands.

No cloud. No login. No nonsense. Just you, your projects, and momentum.

---

## Quick Start

### 1. Clone or pull the repo

```bash
git clone https://github.com/walkermejames-commits/JamesOS.git
cd JamesOS
```

If you already have it:

```bash
cd JamesOS
git pull origin main
```

### 2. Check Python

Windows:

```powershell
python --version
```

Mac:

```bash
python3 --version
```

### 3. Run JamesOS

Windows:

```powershell
python james.py status
```

Mac:

```bash
python3 james.py status
```

---

## Available Commands

| Command | What It Does |
|---|---|
| `python james.py status` | Full portfolio overview and current priority |
| `python james.py next` | Gives the single most important next action |
| `python james.py doctor` | Runs a system health check |
| `python james.py money` | Shows fastest routes to money |
| `python james.py review` | Creates a weekly executive review |
| `python james.py momentum` | Shows momentum scores across projects |
| `python james.py project chipos` | Deep dive on ChipOS Mark II |
| `python james.py project doorin5` | Deep dive on Door in 5 |
| `python james.py project evidence` | Deep dive on Evidence Transcript Core |
| `python james.py project inventory` | Deep dive on Inventory Application |
| `python james.py update doorin5 momentum_score 52` | Updates a project field safely |
| `python james.py win "Shipped a test"` | Records a win |
| `python james.py prompt codex doorin5` | Generates a ready-to-paste Codex prompt |
| `python james.py log "I did X"` | Logs what you worked on today |

---

## VS Code Integration

Open the folder in VS Code, then:

1. Press `Ctrl+Shift+P` or `Cmd+Shift+P` on Mac
2. Type `Tasks: Run Task`
3. Choose a JamesOS task

Included tasks:

- JamesOS Status
- JamesOS Next Action
- JamesOS Codex Prompt - ChipOS
- JamesOS Codex Prompt - Doorin5
- JamesOS Codex Prompt - Evidence
- JamesOS Codex Prompt - Inventory
- JamesOS Momentum

---

## How Project State Works

Project data lives in JSON files:

```text
state/projects/chipos-mark-ii.json
state/projects/doorin5.json
state/projects/evidence-transcript-core.json
state/projects/inventory-application.json
```

You can edit them by hand, or use:

```bash
python james.py update doorin5 momentum_score 52
python james.py update evidence completion_percent 30
python james.py update chipos current_blocker "Need Android build"
```

---

## Daily Logs and Wins

Daily logs are written to:

```text
logs/daily/YYYY-MM-DD.md
```

Wins are written to:

```text
memory/wins.md
```

Record a win:

```bash
python james.py win "Generated first working Codex prompt"
```

---

## Example v0.2 Outputs

`python james.py doctor`

```text
SYSTEM HEALTH SCORE: 100/100
Everything looks healthy. You're good to go, darling.
```

`python james.py money`

```text
Fastest route to GBP 100
Evidence Transcript Core: Paid early access for UK solicitors...
```

`python james.py review`

```text
PROJECTS TO PUSH
  - Door in 5
  - Evidence Transcript Core

RECOMMENDED NEXT 10 HOURS
  Focus on Evidence Transcript Core -> build the smallest testable paid flow
```

---

## Personality

JamesOS is:

- Money-focused
- Momentum-focused
- Camp
- Queer
- Encouraging but honest
- Anti-corporate
- Anti-boring

It celebrates wins, calls out project drift, and pushes you toward real users and real money.

---

## Motto

> Build things.  
> Finish things.  
> Launch things.  
> Make money.  
> Stay fabulous.  
> Repeat.

---

## Next Ideas

- Git awareness
- Repo scan command
- Better Codex/Cursor/Windsurf prompt templates
- Weekly markdown report export
- Simple local menu mode

First, use v0.2 for a few real work sessions.
