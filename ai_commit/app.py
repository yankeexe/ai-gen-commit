import os
import subprocess
import sys

import ollama
from openai import OpenAI

from ai_commit import args
from ai_commit.prompts import system_prompt

commands = {
    "is_git_repo": "git rev-parse --git-dir",
    "clear_screen": ["cls" if os.name == "nt" else "clear"],
    "commit": "git commit -m",
    "get_stashed_changes": "git diff --cached",
}


def get_api_key() -> str:
    """Check if API keys are set in environment variables.

    Returns:
        bool: True if OPENAI_API_KEY environment variable is set, False otherwise.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            """
🔑 No API Key set to use a remote model.

Get either OpenAI or Gemini API keys and export them to use a remote model:

> export OPENAI_API_KEY=<your-openai-or-gemini-api-key>
"""
        )
        sys.exit(1)

    return api_key


def get_model():
    ollama_model = args.model or os.environ.get("OLLAMA_MODEL")

    if not ollama_model:
        print(
            """
🦙 No Ollama model specified for use.

Specify ollama model to use by:

- passing `-m` flag:
> aic -m "llama3.2:3b"

- using environment variable (recommended):

> export OLLAMA_MODEL="llama3.2:3b"
    """
        )
        sys.exit(1)
    return ollama_model


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
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: \n{e.stderr}")
        sys.exit(1)


def generate_commit_message_local_model(staged_changes: str):
    model_name = get_model()
    if args.debug:
        print(f">>> Using Ollama with {model_name}")

    try:
        stream = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Here are the staged changes '''{staged_changes}'''",
                },
            ],
            stream=True,
            options={"temperature": 0},
        )

        print("✨ Generating commit message...")
        print("-" * 50 + "\n")
        commit_message = ""
        for chunk in stream:
            if chunk["done"] is False:
                content = chunk["message"]["content"]
                print(content, end="", flush=True)
                commit_message += content

        return commit_message
    except Exception as e:
        print(f"❌ Error generating commit message: {str(e)}")
        sys.exit(1)


def generate_commit_message_remote_model(staged_changes: str):
    api_key = get_api_key()
    if api_key.startswith("sk-"):
        model_name = args.model or "gpt-4o"
        base_url = None
        if args.debug:
            print(f">>> Using OpenAI with {model_name}")

    else:
        model_name = args.model or "gemini-1.5-pro"
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        if args.debug:
            print(f">>> Using Gemini with {model_name}")

    try:
        client = OpenAI(base_url=base_url)
        stream = client.chat.completions.create(
            model=model_name,
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


def interaction_loop(staged_changes: str):
    while True:
        if args.remote:
            commit_message = generate_commit_message_remote_model(staged_changes)
        else:
            commit_message = generate_commit_message_local_model(staged_changes)

        action = input("\n\nProceed to commit? [y(yes) | n[no] | r(regenerate)] ")

        match action:
            case "r" | "regenerate":
                subprocess.run(commands["clear_screen"])
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
            case _:
                print("\n🤖 Invalid action")
                break


def run():
    try:
        if not run_command(commands["is_git_repo"]):
            print("\n\n🐙 Not a git repo.")
            sys.exit(1)

        staged_changes = run_command(commands["get_stashed_changes"])
        if args.debug:
            print(staged_changes)
            print("-" * 50)
        if not staged_changes:
            print("\n🗂️ No staged changes")
            sys.exit(1)

        interaction_loop(staged_changes)
    except KeyboardInterrupt:
        print("\n\n❌ AI commit exited.")


if __name__ == "__main__":
    run()
