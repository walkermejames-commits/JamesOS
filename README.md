# JamesOS v0.3 - Your Fabulous Local Command Centre

**Build things. Finish things. Launch things. Make money. Stay fabulous. Repeat.**

JamesOS is a tiny, dependency-free Python CLI that acts as your personal project command centre. It tracks your projects, gives you momentum scores, generates ready-to-paste Codex prompts, and keeps you focused on revenue and shipping.

**New in v0.3**: Agent mode, daily missions, focus mode, local dashboard, git checks, and agent memory.

No cloud. No login. No heavy dependencies. Just you, your projects, and momentum.

---

## Quick Start

```bash
python james.py doctor
python james.py agent
python james.py mission
python james.py focus
```

---

## Core Commands

| Command | What It Does |
|---|---|
| `python james.py status` | Portfolio overview and current priority |
| `python james.py next` | Next action mode |
| `python james.py doctor` | System health check |
| `python james.py money` | Revenue focus mode |
| `python james.py review` | Weekly executive review |
| `python james.py agent` | Interactive JamesOS Agent session |
| `python james.py mission` | Creates today's mission |
| `python james.py focus` | Gives one single action only |
| `python james.py dashboard` | Generates `dashboard.html` |
| `python james.py gitcheck` | Safe local git status check |
| `python james.py project doorin5` | Project deep dive |
| `python james.py prompt codex doorin5` | Generates a Codex prompt |
| `python james.py prompt codex agent` | Generates a prompt to improve JamesOS itself |
| `python james.py win "description"` | Records a win |
| `python james.py update PROJECT FIELD VALUE` | Updates project JSON |

---

## JamesOS Agent Mode

Run:

```bash
python james.py agent
```

Agent mode shows:

- current priority
- today's mission
- fastest route to money
- biggest blocker
- suggested next command
- one Codex prompt suggestion

It then opens a simple text menu.

---

## Daily Mission Mode

Run:

```bash
python james.py mission
```

This generates one daily mission and saves it to the daily log.

---

## Focus Mode

Run:

```bash
python james.py focus
```

This gives exactly one action:

- do this now
- time estimate
- why it matters
- what not to do
- win condition

---

## Dashboard

Run:

```bash
python james.py dashboard
```

This creates:

```text
dashboard.html
```

Open it in your browser for a local project dashboard.

---

## Git Check

Run:

```bash
python james.py gitcheck
```

This performs safe local git checks only:

- current branch
- status summary
- last commit
- whether there are uncommitted changes

It does not pull, push, merge, reset, or delete anything.

---

## Autonomy Levels

JamesOS stores agent settings in:

```text
state/agent.json
```

Supported levels:

- `advisor`: suggests actions only
- `operator`: can write local logs, prompts, and reports
- `commander`: stronger planning and focus enforcement

v0.3 defaults to safe local behaviour.

---

## Safety Boundaries

JamesOS can help create money-making actions, but it does not guarantee income.

JamesOS may:

- read local JSON state
- write local logs
- generate prompts
- generate dashboards
- suggest actions
- run safe git status checks
- prepare customer or payment wording for review

JamesOS must not:

- spend money
- contact customers without approval
- push to GitHub without approval
- delete files
- run destructive git commands
- access bank accounts
- control wallets
- move funds
- store seed phrases or private keys
- promise guaranteed income

Public receiving addresses only. James approves and executes external actions manually.

---

## Project State

Project data lives in:

```text
state/projects/
```

Current projects:

- ChipOS Mark II
- Door in 5
- Evidence Transcript Core
- Inventory Application

---

## Motto

> Build things.  
> Finish things.  
> Launch things.  
> Make money.  
> Stay fabulous.  
> Repeat.
