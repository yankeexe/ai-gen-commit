from pathlib import Path
import subprocess

default_system_prompt = """
You are an expert AI commit message generator specialized in creating concise, informative commit messages that follow best practices in version control.

Your ONLY task is to generate a well-structured commit message based on the provided diff. The commit message must:
1. Use a clear, descriptive title in the imperative mood (50 characters max)
2. Provide a detailed explanation of changes in bullet points
3. Focus solely on the technical changes in the code
4. Use present tense and be specific about modifications

Key Guidelines:
- Analyze the entire diff comprehensively
- Capture the essence of only MAJOR changes
- Use technical, precise languages
- Avoid generic or vague descriptions
- Avoid quoting any word or sentences
- Avoid adding description for minor changes with not much context
- Return just the commit message, no additional text
- Don't return more bullet points than required

Output Format:
Concise Title Summarizing Changes

- Specific change description
- Another specific change description
- Rationale for key modifications
- Impact of changes
"""


def read_prompt(path: Path) -> str:
    with open(str(path)) as config_file:
        return config_file.read()


def get_system_prompt() -> str:
    """Gets the system prompt from config file or returns default.

    This function checks for a custom system prompt configuration file in the following
    order:
    1. .ai-commit file in the current git worktree root
    2. .ai-commit file in the user's home directory
    If neither exists or contains content, returns the default system prompt.

    Returns:
        str: The system prompt to use - either custom from config or default
    """
    # Check for `.ai-commit` file in current git worktree
    try:
        git_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        git_ai_commit_config = Path(git_root) / ".ai-commit"
    except subprocess.CalledProcessError:
        pass  # Not in a git repo

    if git_ai_commit_config.exists():
        git_system_prompt = read_prompt(git_ai_commit_config)
        if git_system_prompt:
            return git_system_prompt

    # Check for `.ai-commit` file in users $HOME
    ai_commit_config = Path.home() / ".ai-commit"
    if ai_commit_config.exists():
        global_system_prompt = read_prompt(ai_commit_config)
        if global_system_prompt:
            return default_system_prompt
        else:
            return default_system_prompt
