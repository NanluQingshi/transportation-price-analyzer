"""
Agent 主流程：只做编排，不直接写外部调用。
工具调用通过 tools/ 层执行，prompt 从 prompts/ 读取。
"""

import json
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import anthropic
import structlog

from src.config import settings
from src.tools import analyze_price, get_price_trend, search_flights

logger = structlog.get_logger(__name__)

_SYSTEM_PROMPT = (Path(__file__).parent.parent.parent / "prompts/system.md").read_text(
    encoding="utf-8"
)

_TOOL_REGISTRY = {
    "search_flights": search_flights.execute,
    "get_price_trend": get_price_trend.execute,
    "analyze_price": analyze_price.execute,
}

_TOOLS = [
    search_flights.get_schema(),
    get_price_trend.get_schema(),
    analyze_price.get_schema(),
]


def _sse(event_type: str, data: Any) -> str:
    return f"data: {json.dumps({'type': event_type, **data}, ensure_ascii=False)}\n\n"


async def run_agent(message: str) -> AsyncGenerator[str, None]:
    """驱动 Claude Tool Use 循环，通过 SSE 逐步输出事件。"""
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    messages: list[dict[str, Any]] = [{"role": "user", "content": message}]
    log = logger.bind(message_preview=message[:60])

    for iteration in range(5):  # 最多 5 轮工具调用，防止无限循环
        log.info("agent_iteration", round=iteration)

        response = await client.messages.create(
            model=settings.agent_model,
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            tools=_TOOLS,  # type: ignore[arg-type]
            messages=messages,
        )

        # 把 Claude 的回复加入消息历史
        messages.append({"role": "assistant", "content": response.content})

        has_tool_use = any(b.type == "tool_use" for b in response.content)

        # 先流出文本块
        for block in response.content:
            if block.type == "text" and block.text:
                yield _sse("text", {"content": block.text})

        # 没有工具调用 → 对话结束
        if not has_tool_use or response.stop_reason == "end_turn":
            break

        # 执行工具调用
        tool_results: list[dict[str, Any]] = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            tool_name = block.name
            tool_args = block.input
            yield _sse("tool_call", {"tool": tool_name, "args": tool_args})

            executor = _TOOL_REGISTRY.get(tool_name)
            if executor is None:
                result: Any = {"error": f"Unknown tool: {tool_name}"}
                log.error("unknown_tool", tool=tool_name)
            else:
                try:
                    result = await executor(**tool_args)  # type: ignore[arg-type]
                    log.info("tool_success", tool=tool_name)
                except Exception as exc:
                    result = {"error": str(exc)}
                    log.error("tool_error", tool=tool_name, error=str(exc))

            yield _sse("tool_result", {"tool": tool_name, "data": result})
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result, ensure_ascii=False, default=str),
            })

        messages.append({"role": "user", "content": tool_results})

    yield _sse("done", {})
