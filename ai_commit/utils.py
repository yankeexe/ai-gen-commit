import ipaddress
import os
import sys
import urllib

from ai_commit import cli_args as args


def get_model():
    ollama_model = args.model or os.environ.get("OLLAMA_MODEL")
    if not ollama_model and not args.remote:
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
