"""Streamlit interface for the interactive shopping assistant."""

import json
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from threading import Lock
from typing import Any

import streamlit as st
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

from smart_shopping_agent import (
    MODEL_NAME,
    ShoppingResponse,
    create_shopping_agent,
    get_recommendations,
)


def _format_value(value: Any) -> str:
    if isinstance(value, str):
        try:
            return json.dumps(json.loads(value), ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            return value
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def _format_model_input(messages: list[BaseMessage]) -> list[dict[str, Any]]:
    formatted = []
    for message in messages:
        if isinstance(message, HumanMessage):
            formatted.append({"role": "User", "content": _format_value(message.content)})
        elif isinstance(message, ToolMessage):
            formatted.append(
                {
                    "role": f"Tool result: {message.name or 'tool'}",
                    "content": _format_value(message.content),
                }
            )
        elif isinstance(message, AIMessage):
            assistant_message: dict[str, Any] = {"role": "Assistant"}
            if message.tool_calls:
                assistant_message["tool_calls"] = [
                    {"tool": call["name"], "arguments": call["args"]}
                    for call in message.tool_calls
                ]
            if message.content:
                assistant_message["content"] = (
                    "[Free-text assistant content omitted; intermediate reasoning is not shown.]"
                )
            formatted.append(assistant_message)
        else:
            formatted.append(
                {
                    "role": message.type.capitalize(),
                    "content": _format_value(message.content),
                }
            )
    return formatted


class StreamlitTraceHandler(BaseCallbackHandler):
    """Capture model and tool activity without exposing private reasoning text."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.event_queue: Queue[dict[str, Any]] = Queue()
        self.model_call_count = 0
        self.model_inputs: dict[str, list[dict[str, Any]]] = {}
        self.tool_inputs: dict[str, dict[str, Any]] = {}
        self.lock = Lock()

    def on_chat_model_start(
        self,
        _serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: Any,
        **_kwargs: Any,
    ) -> None:
        del _serialized, _kwargs
        with self.lock:
            self.model_inputs[str(run_id)] = _format_model_input(messages[0] if messages else [])

    def on_llm_end(self, response: Any, *, run_id: Any, **_kwargs: Any) -> None:
        del _kwargs
        model_response: list[dict[str, Any]] = []
        generations = getattr(response, "generations", [])
        for batch in generations:
            for generation in batch:
                message = getattr(generation, "message", None)
                if not isinstance(message, AIMessage):
                    continue
                for call in message.tool_calls:
                    if call["name"] == ShoppingResponse.__name__:
                        model_response.append(
                            {
                                "action": "Structured final response",
                                "schema": call["name"],
                                "response": call["args"],
                            }
                        )
                    else:
                        model_response.append(
                            {
                                "action": "Tool requested",
                                "tool": call["name"],
                                "arguments": call["args"],
                            }
                        )
                if not message.tool_calls and message.content:
                    model_response.append(
                        {
                            "action": "Text response",
                            "response": "[Free-text response omitted; intermediate reasoning is not shown.]",
                        }
                    )

        with self.lock:
            self.model_call_count += 1
            call_number = self.model_call_count
            model_input = self.model_inputs.pop(str(run_id), [])
        event = {
            "type": "Model call",
            "call_number": call_number,
            "sent_to_model": model_input,
            "model_response": model_response or [
                {"action": "No tool call or visible text response returned."}
            ],
        }
        self._record_event(event)

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: Any,
        **_kwargs: Any,
    ) -> None:
        del _kwargs
        with self.lock:
            self.tool_inputs[str(run_id)] = {
                "tool": serialized.get("name", "tool"),
                "input": _format_value(input_str),
            }

    def on_tool_end(self, output: Any, *, run_id: Any, **_kwargs: Any) -> None:
        del _kwargs
        with self.lock:
            event = self.tool_inputs.pop(str(run_id), {"tool": "tool", "input": ""})
        event["type"] = "Tool result"
        event["output"] = _format_value(output)
        self._record_event(event)

    def on_tool_error(self, error: BaseException, *, run_id: Any, **_kwargs: Any) -> None:
        del _kwargs
        with self.lock:
            event = self.tool_inputs.pop(str(run_id), {"tool": "tool", "input": ""})
        event.update({"type": "Tool error", "error": str(error)})
        self._record_event(event)

    def on_llm_error(self, error: BaseException, *, run_id: Any, **_kwargs: Any) -> None:
        del _kwargs
        with self.lock:
            self.model_call_count += 1
            call_number = self.model_call_count
            model_input = self.model_inputs.pop(str(run_id), [])
        event = {
            "type": "Model error",
            "call_number": call_number,
            "sent_to_model": model_input,
            "error": str(error),
        }
        self._record_event(event)

    def _record_event(self, event: dict[str, Any]) -> None:
        with self.lock:
            self.events.append(event)
        self.event_queue.put(event)


def _render_trace_event(event: dict[str, Any]) -> None:
    title = event["type"]
    if "call_number" in event:
        title += f" #{event['call_number']}"
    with st.expander(title, expanded=True):
        if "sent_to_model" in event:
            st.caption("Messages sent to the LLM")
            st.json(event["sent_to_model"])
        if "input" in event:
            st.caption(f"Input to {event.get('tool', 'tool')}")
            st.code(event["input"], language="json")
        if "model_response" in event:
            st.caption("LLM response")
            st.json(event["model_response"])
        if "arguments" in event:
            st.caption("Arguments")
            st.json(event["arguments"])
        if "output" in event:
            st.caption(f"Output from {event.get('tool', 'tool')}")
            st.code(event["output"], language="json")
        if "error" in event:
            st.error(event["error"])


def _render_response(response: dict[str, Any]) -> None:
    st.markdown("#### Recommendations")
    if not response["recommendations"]:
        st.info("No products matched the request.")
    for recommendation in response["recommendations"]:
        with st.container(border=True):
            st.subheader(recommendation["name"])
            left, right = st.columns(2)
            left.write(f"**Product ID:** {recommendation['product_id']}")
            left.write(f"**Price:** {recommendation['price']}")
            right.write(f"**In stock:** {'Yes' if recommendation['stock'] else 'No'}")
            right.write(f"**Discount:** {recommendation['discount']}")
            st.write(f"**Reviews:** {recommendation['reviews']}")

    if response["comparisons"]:
        st.markdown("#### Comparisons")
        for comparison in response["comparisons"]:
            name = next(
                (
                    item["name"]
                    for item in response["recommendations"]
                    if item["product_id"] == comparison["product_id"]
                ),
                comparison["product_id"],
            )
            with st.expander(name):
                left, right = st.columns(2)
                left.markdown("**Pros**")
                for pro in comparison["pros"]:
                    left.write(f"- {pro}")
                right.markdown("**Cons**")
                for con in comparison["cons"]:
                    right.write(f"- {con}")

    st.markdown("#### Explanation")
    st.write(response["explanation"])
    with st.expander("Response JSON"):
        st.json(response)


def main() -> None:
    st.set_page_config(page_title="Smart Shopping Assistant", page_icon="🛍️")
    st.title("Smart Shopping Assistant")
    st.caption(
        f"Powered by {MODEL_NAME}. The trace shows model inputs, tool actions, "
        "and tool results; private chain-of-thought is not displayed."
    )

    if "shopping_history" not in st.session_state:
        st.session_state.shopping_history = []

    st.sidebar.title("LLM Debug Log")
    st.sidebar.caption(
        "Shows request messages, tool calls, and tool results. "
        "Free-text intermediate reasoning is omitted."
    )
    for index, entry in enumerate(st.session_state.shopping_history, start=1):
        with st.sidebar.expander(f"Request {index}: {entry['query'][:40]}"):
            if "error" in entry:
                st.error(entry["error"])
            for event in entry["trace"]:
                _render_trace_event(event)

    for entry in st.session_state.shopping_history:
        with st.chat_message("user"):
            st.write(entry["query"])
        with st.chat_message("assistant"):
            if "error" in entry:
                st.error(entry["error"])
            else:
                _render_response(entry["response"])
    query = st.chat_input("What are you looking for?")
    if not query:
        return

    with st.chat_message("user"):
        st.write(query)
    with st.chat_message("assistant"):
        trace_handler = StreamlitTraceHandler()
        try:
            agent = create_shopping_agent()
            with st.status("Searching products and checking product details...", expanded=False) as status:
                with st.sidebar.expander(f"Live trace: {query[:40]}", expanded=True):
                    trace_container = st.container()
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        get_recommendations,
                        agent,
                        query,
                        callbacks=[trace_handler],
                    )
                    while not future.done():
                        try:
                            event = trace_handler.event_queue.get(timeout=0.1)
                        except Empty:
                            continue
                        with trace_container:
                            _render_trace_event(event)

                    while True:
                        try:
                            event = trace_handler.event_queue.get_nowait()
                        except Empty:
                            break
                        with trace_container:
                            _render_trace_event(event)

                    response = future.result()
                status.update(label="Shopping results ready", state="complete", expanded=False)
            response_data = response.model_dump(mode="json")
            _render_response(response_data)
            history_entry = {
                "query": query,
                "response": response_data,
                "trace": trace_handler.events,
            }
        except Exception as exc:
            st.error(f"Unable to complete the shopping request: {exc}")
            history_entry = {
                "query": query,
                "error": str(exc),
                "trace": trace_handler.events,
            }
    st.session_state.shopping_history.append(history_entry)


if __name__ == "__main__":
    main()
