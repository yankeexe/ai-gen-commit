import argparse
from dataclasses import dataclass
from typing import Annotated


@dataclass
class CLIArgs:
    remote: Annotated[bool, "Use remote model for commit generation"]
    debug: Annotated[bool, "Run the CLI in debug mode"]
    model: Annotated[str | None, "Model to use for commit generation"] = None
    command: Annotated[str | None, "Sub-command passed to the CLI"] = None


parser = argparse.ArgumentParser(
    description="Generate commit message using AI.",
    usage="aic [options]",
    formatter_class=argparse.RawTextHelpFormatter,
)
parser.add_argument(
    "-d",
    "--debug",
    action="store_true",
    help="Enable debug logging",
    default=False,
)
parser.add_argument("-m", "--model", help="Ollama model name")


remote_model_help = """
🐙 Use remote model for commit message generation.
Get an API key for OpenAI, Groq, Gemini, TogetherAI, or Deepseek, and export it to use a remote model.

> export OPENAI_API_KEY=<your-api-key>
"""
parser.add_argument(
    "-r", "--remote", help=remote_model_help, default=False, action="store_true"
)


version_parser = parser.add_subparsers(title="version", dest="command")
version_parser.add_parser("version", help="Show app version")
raw_args = parser.parse_args()


cli_args = CLIArgs(
    remote=raw_args.remote,
    debug=raw_args.debug,
    model=raw_args.model,
    command=raw_args.command,
)
