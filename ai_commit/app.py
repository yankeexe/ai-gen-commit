import ipaddress
import os
import subprocess
import sys
from typing import Optional
import urllib

from openai import OpenAI

from ai_commit import args
from ai_commit.prompts import system_prompt

commands = {
    "is_git_repo": "git rev-parse --git-dir",
    "clear_screen": ["cls" if os.name == "nt" else "clear"],
    "commit": "git commit -m",
    "get_stashed_changes": "git diff --cached",
}


def get_api_key(remote: bool = False) -> str:
    """Check if API keys are set in environment variables for remote models.
    If the model is run locally (via Ollama), then the 'ollama' key is returned back.

    Returns:
        bool: True if OPENAI_API_KEY environment variable is set, False otherwise.
    """
    if not remote:
        return "ollama"

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
            encoding="utf-8"
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: \n{e.stderr}")
        sys.exit(1)


def parse_host(host: Optional[str] = None) -> str:
    host, port = host or '', 11434
    scheme, _, hostport = host.partition('://')
    if not hostport:
        scheme, hostport = 'http', host
    elif scheme == 'http':
        port = 80
    elif scheme == 'https':
        port = 443

    split = urllib.parse.urlsplit('://'.join([scheme, hostport]))
    host = split.hostname or '127.0.0.1'
    port = split.port or port

    # Fix missing square brackets for IPv6 from urlsplit
    try:
        if isinstance(ipaddress.ip_address(host), ipaddress.IPv6Address):
            host = f"[{host}]"
    except ValueError:
        ...

    if path := split.path.strip('/'):
        return f'{scheme}://{host}:{port}/{path}'

    return f'{scheme}://{host}:{port}'


def generate_commit_message_remote_model(staged_changes: str, remote: bool = False) -> str:
    api_key: str = get_api_key(remote)
    base_url: str = ""
    model_name: str = ""

    if api_key != "ollama":
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
    else:
        model_name = get_model()
        base_url = parse_host()

        if args.debug:
            print(f">>> Using Ollama with {model_name}")

    try:
        client = OpenAI(base_url=base_url, api_key=api_key)
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
        commit_message: str = ""

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
        commit_message = generate_commit_message_remote_model(staged_changes, args.remote)

        action = input("\n\nProceed to commit? [y(yes) | n[no] | r(regenerate)] ")

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
