# JamesOS v0.2 — Your Fabulous Local Command Centre

**Build things. Finish things. Launch things. Make money. Stay fabulous. Repeat.**

JamesOS is a tiny, dependency-free Python CLI that acts as your personal project command centre. It tracks your projects, gives you momentum scores, generates ready-to-paste Codex prompts, and keeps you focused on revenue and shipping.

**New in v0.2**: `doctor`, `update`, `win`, `review`, and `money` commands.

No cloud. No login. No bullshit. Just you + your projects + momentum.

---

## Quick Start (Windows or Mac)

### 1. Install Python (if you don't have it)

**Mac:**
- Open Terminal and run: `python3 --version`
- If it says "command not found", install from https://www.python.org/downloads/

**Windows:**
- Download from https://www.python.org/downloads/
- During install, **check the box** that says "Add Python to PATH"

### 2. Open the Folder

**Option A (Recommended):**
1. Open VS Code
2. File → Open Folder → select the `jamesos` folder

**Option B:**
- Open Terminal / Command Prompt
- Navigate to the folder:
  - Mac: `cd ~/path/to/jamesos`
  - Windows: `cd C:\path\to\jamesos`

### 3. Run Your First Command

```bash
python james.py status
```

You should see your current portfolio status with fun, camp energy.

---

## Available Commands

| Command                              | What It Does                                      |
|--------------------------------------|---------------------------------------------------|
| `python james.py status`             | Full portfolio overview + current priority        |
| `python james.py next`               | Gives you the single most important next action   |
| `python james.py project chipos`     | Deep dive on ChipOS Mark II                       |
| `python james.py project doorin5`    | Deep dive on Door in 5                            |
| `python james.py project evidence`   | Deep dive on Evidence Transcript Core             |
| `python james.py project inventory`  | Deep dive on Inventory Application                |
| `python james.py prompt codex chipos`| Generates a ready-to-paste Codex prompt           |
| `python james.py log "I did X"`      | Logs what you worked on today                     |
| `python james.py momentum`           | Shows momentum scores across all projects         |

---

## VS Code Integration (Recommended)

Once the folder is open in VS Code:

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type **"Tasks: Run Task"**
3. Choose any of the **JamesOS** tasks:
   - JamesOS Status
   - JamesOS Next Action
   - JamesOS Codex Prompt - Doorin5 (etc.)

This is the closest thing to a "paperclip" experience you can get without building a full extension.

---

## How to Update Projects

All project data lives in simple JSON files:

`state/projects/doorin5.json`  
`state/projects/chipos-mark-ii.json`  
etc.

You can edit these files directly in VS Code. After editing, run `python james.py status` again to see the changes.

---

## Daily Logs

Every time you run `status`, `next`, or `log`, JamesOS writes to:

`logs/daily/YYYY-MM-DD.md`

These are plain markdown files. Read them whenever you want to see what you actually did.

---

## Personality

JamesOS is:
- Money-obsessed
- Momentum-obsessed
- Camp
- Queer
- Encouraging but honest
- Anti-corporate
- Anti-boring

It will celebrate your wins, call out when you're spiralling, and always push you toward **real users + real money**.

---

## Motto

> Build things.  
> Finish things.  
> Launch things.  
> Make money.  
> Stay fabulous.  
> Repeat.

---

## What's Next (v0.2 ideas)

- Better prompt templates per tool (Cursor, Windsurf, etc.)
- Weekly summary command
- Automatic momentum score suggestions
- Git integration (auto-detect recent commits)
- More chaotic encouragement

But first — v0.1 must actually be used.

---

**Now go run `python james.py status` and start shipping.**

You've got this, darling. 💅

---

## Example Screenshots (v0.2)

**`python james.py doctor`**
```
SYSTEM HEALTH SCORE: 100/100
✅ Everything looks healthy.
```

**`python james.py update doorin5 momentum_score 52`**
```
✅ Updated Door in 5
   momentum_score: 35 → 52
```

**`python james.py money`**
```
💰 Fastest route to £100
   Evidence Transcript Core: Paid early access...
```

**`python james.py review`**
```
PROJECTS TO PUSH
   • Door in 5
   • Evidence Transcript Core
```

(Real screenshots coming in later versions)
