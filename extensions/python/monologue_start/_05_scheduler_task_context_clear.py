"""
Clears the task's chat history before each new run when the previous run was successful.

Rationale: Scheduler tasks accumulate history across runs, growing the context window
over time. For successful runs, the history is noise — failures and errors are the only
signal worth preserving for debugging. This extension resets the context (clears history
and log) before each new run if the previous run was NOT an error.

Fires at: monologue_start (once per task run, for agent #0 only)
"""

from agent import LoopData
from helpers.extension import Extension
from helpers import persist_chat


class SchedulerTaskContextClear(Extension):

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        agent = self.agent
        if not agent:
            return

        # Only apply to the root agent (agent #0), not subordinates
        if agent.number != 0:
            return

        # Only act on the very first iteration of each monologue to avoid clearing
        # mid-task (subordinate delegation triggers nested monologues on agent 0's context)
        if loop_data.iteration > 0:
            return

        # Only act if there is existing history to clear (first-ever run has no history)
        if not agent.history.output_text():
            return

        try:
            from helpers.task_scheduler import TaskScheduler, TaskState

            scheduler = TaskScheduler.get()
            context_id = agent.context.id
            tasks = scheduler.get_tasks_by_context_id(context_id)

            if not tasks:
                return  # Not a scheduled task context

            task = tasks[0]

            # Only clear when the PREVIOUS run succeeded (last_result is set and not an error).
            # Preserve history when: no prior result (first run), or last run errored out.
            if not task.last_result:
                return
            if task.last_result.startswith("ERROR:"):
                return

            # Clear: reset context history and remove persisted message files
            agent.context.reset()
            persist_chat.remove_msg_files(context_id)

        except Exception:
            pass  # Non-critical: if this fails, task still runs with existing history
