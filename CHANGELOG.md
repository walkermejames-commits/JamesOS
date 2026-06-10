# JamesOS Changelog

## [0.3] - 2026-06-10

### Added - Agent Mode
- `python james.py agent` - Interactive agent session
- `python james.py mission` - Daily mission generator
- `python james.py focus` - Single action focus mode
- `python james.py dashboard` - Local HTML dashboard (`dashboard.html`)
- `python james.py gitcheck` - Safe local git status only
- `state/agent.json` - Agent memory, autonomy levels, and safety boundaries
- `prompt codex agent` - Self-improvement prompt for JamesOS

### Changed
- Bumped to v0.3
- Stronger focus on practical daily use and revenue focus
- Clear safety boundaries documented

---

## [0.2] - 2026-06-10

### Added
- `doctor` command - Full system health check with score (0-100)
- `update` command - Safely update any field in project JSON files
- `win` command - Record wins to memory/wins.md + daily log
- `review` command - Weekly Executive Report (Push/Pause/Kill, revenue paths, next 10/20 hours)
- `money` command - Fastest routes to GBP 100 / GBP 1,000 / GBP 10,000

### Improved
- Better error handling in project loading
- More personality in output messages
- Daily logging now includes more context

### Changed
- Bumped to v0.2

---

## [0.1] - 2026-06-10

- Initial release
- Core commands: status, next, project, prompt, momentum, log
- Project JSON state system
- Codex prompt generator
- VS Code tasks integration
- Daily markdown logging
