from pathlib import Path

system_prompt = """
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


def get_system_prompt():
    """Gets the system prompt from config file or returns default.

    Checks for a custom system prompt in ~/.ai-commit config file.
    If the file exists and contains content, returns that as the prompt.
    Otherwise returns the default system prompt.

    Returns:
        str: The system prompt to use - either custom from config or default
    """
    ai_commit_config = Path.home() / ".ai-commit"
    if not ai_commit_config.exists():
        return system_prompt

    with open(str(ai_commit_config)) as config_file:
        config_system_prompt = config_file.read()

        if config_system_prompt:
            return config_system_prompt
        else:
            return system_prompt
