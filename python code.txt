"""Interactive LangChain ReAct shopping assistant."""

import argparse
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from shopping_tools import SHOPPING_TOOLS

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

MODEL_NAME = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

SYSTEM_PROMPT = """
You are a careful shopping assistant. Use the provided tools as a ReAct agent:
search the catalogue first, then use PricingAPI, InventoryAPI, and ReviewAPI
for each product you are considering. Use the observed price to apply any
explicit budget in the user's request. The API has no discount data, so report
"No discount" for every product.

Only make claims supported by tool results. The catalogue contains only a
product ID, name, category, and description; it has no structured color,
material, or size data. Do not claim those criteria match unless the returned
catalogue text supports the claim. If no product meets the request, return no
recommendations and explain which criteria could not be met or verified.
Include out-of-stock items only when relevant, accurately set stock to false,
and explain their availability.

When more than one product remains a reasonable candidate, include comparisons
with evidence-based pros and cons. Do not invent product attributes. Always
provide a concise, user-facing explanation of the criteria applied and evidence
used; do not reveal hidden chain-of-thought.

Return the requested structured response. The price field must be a string.
"""


class Recommendation(BaseModel):
    product_id: str
    name: str
    price: str = Field(description="Price as a string, including currency.")
    discount: str
    stock: bool
    reviews: str


class Comparison(BaseModel):
    product_id: str
    pros: list[str]
    cons: list[str]


class ShoppingResponse(BaseModel):
    recommendations: list[Recommendation]
    comparisons: list[Comparison] = Field(default_factory=list)
    explanation: str


class PromptDebugHandler(BaseCallbackHandler):
    """Print each chat-model request's messages and parameters before sending."""

    def __init__(self) -> None:
        self.call_number = 0

    @staticmethod
    def _redact(value: Any, key: str = "") -> Any:
        if any(secret in key.lower() for secret in ("api_key", "apikey", "token", "authorization", "secret")):
            return "[REDACTED]"
        if isinstance(value, dict):
            return {str(item_key): PromptDebugHandler._redact(item_value, str(item_key))
                    for item_key, item_value in value.items()}
        if isinstance(value, (list, tuple)):
            return [PromptDebugHandler._redact(item) for item in value]
        return value

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[Any]],
        **kwargs: Any,
    ) -> None:
        self.call_number += 1
        model_info = self._redact(serialized)
        request_parameters = self._redact(kwargs)
        print(f"\n[LLM DEBUG] Request {self.call_number}", flush=True)
        print(
            json.dumps(
                {
                    "model": model_info,
                    "messages": [
                        [message.model_dump(mode="json", exclude_none=True) for message in batch]
                        for batch in messages
                    ],
                    "request_parameters": request_parameters,
                },
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
            flush=True,
        )


def create_shopping_agent():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to ecomm-agents/.env before starting the agent."
        )

    model = ChatOpenAI(
        model=MODEL_NAME,
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
        temperature=0,
    )
    return create_agent(
        model=model,
        tools=SHOPPING_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        response_format=ToolStrategy(ShoppingResponse),
    )


def get_recommendations(
    agent,
    query: str,
    callbacks: list[BaseCallbackHandler] | None = None,
) -> ShoppingResponse:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": query}]},
        config={"callbacks": callbacks if callbacks is not None else [PromptDebugHandler()]},
    )
    response = result.get("structured_response")
    if not isinstance(response, ShoppingResponse):
        raise ValueError("The agent did not return a valid structured shopping response.")
    return response


def main() -> None:
    parser = argparse.ArgumentParser(description="Get shopping recommendations from the ecommerce API.")
    parser.add_argument(
        "query",
        nargs="*",
        help='Optional one-shot shopping query, for example "black leather jacket under $300".',
    )
    args = parser.parse_args()

    agent = create_shopping_agent()
    if args.query:
        response = get_recommendations(agent, " ".join(args.query))
        print(response.model_dump_json(indent=2))
        return

    print("Shopping assistant ready. Type 'quit' to exit.")

    while True:
        query = input("\nWhat are you looking for? ").strip()
        if query.lower() in {"quit", "exit"}:
            break
        if not query:
            continue

        response = get_recommendations(agent, query)
        print(response.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
