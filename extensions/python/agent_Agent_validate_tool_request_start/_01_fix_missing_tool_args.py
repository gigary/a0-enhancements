"""
Fixes the overly strict tool_args validation in Agent.validate_tool_request.

The original validation rejects tool calls where tool_args is missing or an empty
dict. This is a known issue with Qwen3.5 models that sometimes omit tool_args when
no arguments are needed (matching Agent Zero's own skills_tool:list example).

This extension intercepts validate_tool_request_start, normalizes the tool_request
dict, and performs a corrected validation that replaces the buggy original.
"""

from helpers.extension import Extension


class FixMissingToolArgs(Extension):

    async def execute(self, data=None, **kwargs):
        if data is None:
            return

        args = data.get("args", ())
        if not args or len(args) < 2:
            return

        # args[0] = self (Agent), args[1] = tool_request
        tool_request = args[1]

        if not isinstance(tool_request, dict):
            data["exception"] = ValueError("Tool request must be a dictionary")
            return

        if not tool_request.get("tool_name") or not isinstance(
            tool_request.get("tool_name"), str
        ):
            data["exception"] = ValueError(
                "Tool request must have a tool_name (type string) field"
            )
            return

        # Normalize: accept "args" as alias for "tool_args", default to empty dict
        if "tool_args" not in tool_request:
            tool_request["tool_args"] = tool_request.get("args", {})

        tool_args = tool_request["tool_args"]

        # Allow None / missing -> treat as empty dict
        if tool_args is None:
            tool_request["tool_args"] = {}
        elif not isinstance(tool_args, dict):
            data["exception"] = ValueError(
                "Tool request tool_args must be a dictionary, "
                f"got {type(tool_args).__name__}"
            )
            return

        # Validation passed - short-circuit the original buggy validate_tool_request
        data["result"] = None
