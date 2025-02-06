import os
import shutil
import subprocess
import sys
import tempfile

from openai import OpenAI

from ai_commit import cli_args as args
from ai_commit.prompts import system_prompt
from ai_commit.providers import get_ai_provider, provider_names

commands = {
    "is_git_repo": "git rev-parse --git-dir",
    "clear_screen": ["cls" if os.name == "nt" else "clear"],
    "commit": "git commit -m",
    "get_stashed_changes": "git diff --cached",
}


def get_api_key() -> str:
    """Check if API keys are set in environment variables for remote models.
    If the model is run locally (via Ollama), then the 'ollama' key is returned back.

    Returns:
        bool: True if OPENAI_API_KEY environment variable is set, False otherwise.
    """
    if not args.remote:
        return "ollama"

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            f"""
🔑 No API Key set to use a remote model.

Get API keys for {provider_names} and export them to use a remote model:

> export OPENAI_API_KEY=<your-api-key>
"""
        )
        sys.exit(1)

    return api_key


def run_command(command: list[str] | str, extra_args: list[str] = []):
    try:
        shell_command = command.split() if isinstance(command, str) else command
        if args.debug:
            print("-" * 50)
            print(f"⚡️ Running command: {shell_command}")
            print("-" * 50)
        result = subprocess.run(
            shell_command + extra_args,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
            encoding="utf-8",
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: \n{e.stderr}")
        sys.exit(1)


def generate_commit_message(staged_changes: str) -> str:
    provider = get_ai_provider()
    api_key = get_api_key()
    if not provider:
        print("❌ No LLM provider found for remote mode.")
        sys.exit(1)

    if args.debug:
        print(f">>> Using {provider.name} with {provider.model}")

    try:
        client = OpenAI(base_url=provider.base_url, api_key=api_key)
        stream = client.chat.completions.create(
            model=provider.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Here are the staged changes '''{staged_changes}'''",
                },
            ],
            temperature=0,
            stream=True,
        )

        print("✨ Generating commit message...")
        print("-" * 50 + "\n")
        commit_message = ""

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
                commit_message += content

        return commit_message
    except Exception as e:
        print(f"❌ Error generating commit message: {str(e)}")
        sys.exit(1)


def handle_editing(commit_message: str):
    editor = os.environ.get("EDITOR", "vi")
    has_default_editor = shutil.which(editor) is not None

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".txt"
    ) as temp_file:
        temp_file.write(commit_message)
        temp_file_path = temp_file.name

    try:
        subprocess.run([editor, temp_file_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error opening editor: {e}")


def interaction_loop(staged_changes: str):
    while True:
        commit_message = generate_commit_message(staged_changes)

        action = input(
            "\n\nProceed to commit? [y(yes) | n[no] | r(regenerate) | e(edit)]"
        )
        action = action.strip()

        match action:
            case "r" | "regenerate":
                subprocess.run(commands["clear_screen"], shell=True)
                continue
            case "y" | "yes":
                print("committing...")
                res = run_command(commands["commit"], [commit_message])
                print(res)
                print("\n✨ Committed!")
                break
            case "n" | "no":
                print("\n❌ Discarding AI commit message.")
                break
            case "e" | "edit":
                handle_editing(commit_message)
            case _:
                print("\n🤖 Invalid action")
                break


def run():
    try:
        run_command(commands["is_git_repo"])
        staged_changes = run_command(commands["get_stashed_changes"])

        if not staged_changes:
            print("\n🗂️ No staged changes")
            sys.exit(1)

        if args.debug:
            print(staged_changes)
            print("-" * 50)

        interaction_loop(staged_changes)
    except KeyboardInterrupt:
        print("\n\n❌ AI commit exited.")


if __name__ == "__main__":
    run()
