import os
import sys
from dataclasses import dataclass

from ai_commit import cli_args as args
from ai_commit.utils import get_model, parse_host


@dataclass
class Provider:
    name: str
    model: str
    base_url: str


providers_mapping = {
    "ollama": Provider(
        name="ollama",
        model=get_model(),
        base_url=parse_host(os.getenv("OLLAMA_HOST")) + "/v1",
    ),
    "openai": Provider(name="openai", model="gpt-4o", base_url=""),
    "groq": Provider(
        name="groq",
        model="llama-3.2-3b-preview",
        base_url="https://api.groq.com/openai/v1",
    ),
    "gemini": Provider(
        name="gemini",
        model="gemini-2.0-flash-exp",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    ),
    "togetherai": Provider(
        name="togetherai",
        model="google/gemma-2-9b-it",
        base_url="https://api.together.xyz/v1",
    ),
    "deepseek": Provider(
        name="deepseek",
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
    ),
    "qwen": Provider(
        name="qwen",
        model="qwen2.5-7b-instruct",
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    ),
    "mistral": Provider(
        name="mistral", model="ministral-3b-2410", base_url="https://api.mistral.ai/v1"
    ),
    "custom": Provider(
        name=os.environ.get("AI_COMMIT_PROVIDER"),
        model=os.environ.get("AI_COMMIT_MODEL"),
        base_url=os.environ.get("AI_COMMIT_PROVIDER_BASE_URL"),
    ),
}


provider_names = list(providers_mapping.keys())


def get_ai_provider() -> Provider | None:
    if not args.remote:
        return providers_mapping["ollama"]

    ai_provider = os.environ.get("AI_COMMIT_PROVIDER")
    ai_provider = ai_provider.lower() if ai_provider else None
    if not ai_provider:
        print(
            f"""
🔑 No Provider set to use a remote model.

Set one of these providers:
> export AI_COMMIT_PROVIDER={provider_names}
> export AI_COMMIT_PROVIDER=groq

# Optional
> export AI_COMMIT_MODEL=<model-from-provider>
> export AI_COMMIT_MODEL=qwen-2.5-32b

Get API Keys from one of the these providers and export them to use a remote model:
> export OPENAI_API_KEY=<your-api-key>
"""
        )
        sys.exit(1)

    return providers_mapping.get(ai_provider)
