# A0 Enhancements

Generic enhancements to Agent Zero's default behaviour. Zero modifications to official code - all customisations are applied via the Agent Zero plugin extensibility system.

> **Theme:** Moved to [a0-theme-futuristic](https://github.com/gigary/a0-theme-futuristic).

## Enhancements

### 1. Extended Code Execution Timeouts

**File:** `plugins/_code_execution/config.json`

Overrides the default 3-minute cap to support long-running scripts (git backups, data pipelines, model builds).

| Timeout | Official Default | Override |
|---------|-----------------|---------|
| `code_exec_first_output_timeout` | 30s | 120s |
| `code_exec_between_output_timeout` | 15s | 1800s (30m) |
| `code_exec_max_exec_timeout` | 180s | 10800s (3h) |
| `code_exec_dialog_timeout` | 5s | 5s |
| `output_first_output_timeout` | 90s | 120s |
| `output_between_output_timeout` | 45s | 1800s (30m) |
| `output_max_exec_timeout` | 300s | 10800s (3h) |
| `output_dialog_timeout` | 5s | 5s |

**Additional fields** (all optional, remove to use official defaults):

- `prompt_patterns` - Newline-separated regex patterns. When a shell prompt matches, output returns immediately without waiting for the timeout. Useful for fast scripts that exit quickly.
- `dialog_patterns` - Newline-separated regex patterns (case-insensitive). When matched after `dialog_timeout`, control returns to the agent. Catches interactive prompts like `Y/N`, `yes/no`, or open-ended `?` questions.

### 2. Scheduled Task History Auto-Clear

**File:** `extensions/python/monologue_start/_05_scheduler_task_context_clear.py`

Automatically clears a scheduled task's chat history before each new run, **when the previous run was successful**. Keeps the context window small without losing failure/error history for debugging.

**Logic:**
- Fires at `monologue_start` for agent #0 only (not subordinates)
- Only runs on the first iteration of each monologue (not mid-task)
- Skips if: no prior history (first run), last result was `ERROR:...`
- Calls `context.reset()` + `remove_msg_files()` to clear in-memory and persisted history

---

## How Agent Zero Plugin Configs Work

Plugin configs at `plugins/<plugin-name>/config.json` are loaded by Agent Zero's plugin system before falling back to official `default_config.yaml`. This plugin places overrides at:

```
usr/plugins/a0-enhancements/plugins/_code_execution/config.json
```

Search priority (highest first):
1. `project/.a0proj/agents/<profile>/plugins/<plugin>/config.json`
2. `project/.a0proj/plugins/<plugin>/config.json`
3. `usr/agents/<profile>/plugins/<plugin>/config.json`
4. **`usr/plugins/<plugin-name>/config.json`** ← this plugin's configs
5. `plugins/<plugin>/default_config.yaml` (official defaults)

---

## Installation

```bash
# Symlink (recommended - picks up changes automatically)
ln -s /path/to/a0-enhancements /a0/usr/plugins/a0-enhancements
```

Then enable in Agent Zero → Settings → Plugins.
