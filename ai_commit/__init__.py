import argparse

from dataclasses import dataclass


@dataclass
class CLIArgs:
    remote: bool
    debug: bool
    model: str | None = None


parser = argparse.ArgumentParser(
    description="Generate commit message using AI.", usage="aic [options]"
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
🐙 Use remote model for commit message generation.\n

Get either OpenAI or Gemini API keys and export them to use a remote model:

> export OPENAI_API_KEY=<your-openai-or-gemini-api-key>
"""
parser.add_argument(
    "-r", "--remote", help=remote_model_help, default=False, action="store_true"
)

raw_args = parser.parse_args()
cli_args = CLIArgs(remote=raw_args.remote, debug=raw_args.debug, model=raw_args.model)
