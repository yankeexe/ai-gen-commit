import argparse

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
parser.add_argument("-m", "--model", help="Ollama model name", default=None, type=str)


remote_model_help = """
🐙 Use remote model for commit message generation.\n

Get either OpenAI or Gemini API keys and export them to use a remote model:

> export OPENAI_API_KEY=<your-openai-or-gemini-api-key>
"""
parser.add_argument(
    "-r",
    "--remote",
    help=remote_model_help,
    default=False,
    action="store_true",
)

args = parser.parse_args()
