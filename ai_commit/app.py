import ipaddress
import os
import subprocess
import sys
import urllib
from dataclasses import dataclass

from openai import OpenAI

from ai_commit import args
from ai_commit.prompts import system_prompt

commands = {
    "is_git_repo": "git rev-parse --git-dir",
    "clear_screen": ["cls" if os.name == "nt" else "clear"],
    "commit": "git commit -m",
    "get_stashed_changes": "git diff --cached",
}


@dataclass
class Provider:
    name: str
    model: str
    base_url: str | None


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
            encoding="utf-8",
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: \n{e.stderr}")
        sys.exit(1)


def parse_host(host: str | None = None) -> str:
    """Parses a host string into a fully qualified URL for Ollama.

    Handles parsing of scheme, hostname, port and path components from the input host string.
    Defaults to http://127.0.0.1:11434 if no host is provided.

    Args:
        host: Optional host string to parse. Can include scheme, hostname, port and path.
            Examples:
            - "localhost"
            - "http://localhost"
            - "https://example.com:8080/path"
            - None (defaults to localhost)

    Returns:
        str: Fully qualified URL string in format: scheme://host:port/path
            IPv6 addresses are properly wrapped in square brackets.

    Source: https://github.com/ollama/ollama-python/blob/e956a331e8f5585c0fa70fa56d222c3b83844271/ollama/_client.py#L1145
    """
    host, port = host or "", 11434
    scheme, _, hostport = host.partition("://")
    if not hostport:
        scheme, hostport = "http", host
    elif scheme == "http":
        port = 80
    elif scheme == "https":
        port = 443

    split = urllib.parse.urlsplit("://".join([scheme, hostport]))
    host = split.hostname or "127.0.0.1"
    port = split.port or port

    # Fix missing square brackets for IPv6 from urlsplit
    try:
        if isinstance(ipaddress.ip_address(host), ipaddress.IPv6Address):
            host = f"[{host}]"
    except ValueError:
        ...

    if path := split.path.strip("/"):
        return f"{scheme}://{host}:{port}/{path}"

    return f"{scheme}://{host}:{port}"


def get_llm_provider(remote: bool, api_key: str) -> Provider:
    if not remote:
        return Provider(
            name="ollama",
            model=get_model(),
            base_url=parse_host(os.getenv("OLLAMA_HOST")) + "/v1",
        )

    if api_key.startswith("sk-"):
        return Provider(name="openai", model=args.model or "gpt-4o")

    if api_key.startswith("gsk_"):
        return Provider(
            name="groq",
            model=args.model or "llama-3.2-3b-preview",
            base_url="https://api.groq.com/openai/v1",
        )

    if api_key.startswith("AI"):
        return Provider(
            name="gemini",
            model=args.model or "gemini-1.5-pro",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )


def generate_commit_message(staged_changes: str, remote: bool = False) -> str:
    api_key = get_api_key(remote)
    provider = get_llm_provider(remote, api_key)

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


def interaction_loop(staged_changes: str):
    while True:
        commit_message = generate_commit_message(staged_changes, args.remote)

        action = input("\n\nProceed to commit? [y(yes) | n[no] | r(regenerate)] ")
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
