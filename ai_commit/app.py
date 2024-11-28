import os
import subprocess
import sys

import ollama

commands = {
    "is_git_repo": ["git", "rev-parse", "--git-dir"],
    "clear_screen": ["cls" if os.name == "nt" else "clear"],
    "commit": ["git", "commit", "-m"],
    "get_stashed_changes": ["git", "diff", "--cached"],
}

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
- Generate a single commit message

Output Format:
Concise Title Summarizing Changes

- Specific change description
- Another specific change description
- Rationale for key modifications
- Impact of changes
"""


def generate_commit_message(staged_changes: str):
    try:
        stream = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Here is the diff from staged changes:\n {staged_changes}",
                },
            ],
            stream=True,
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


def interaction_loop(staged_changes: str):
    while True:
        commit_message = generate_commit_message(staged_changes)
        action = input("\n\nProceed to commit? [y(yes) | n[no] | r(regenerate)] ")

        match action:
            case "r" | "regenerate":
                subprocess.run(commands["clear_screen"])
                continue
            case "y" | "yes":
                print("committing...")
                res = run_command(commands["commit"] + [commit_message])
                print(f"\n{res}\n✨ Committed!")
                break
            case "n" | "no":
                print("\n❌ Discarding AI commit message.")
                break
            case _:
                print("\n🤖 Invalid action")
                break


def run_command(command: list[str] | str):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: \n{e.stderr}")
        sys.exit(1)


def run():
    try:
        # Check if a valid git repo
        run_command(commands["is_git_repo"])

        # Get diff of stashed changes
        staged_changes = run_command(commands["get_stashed_changes"])
        if not staged_changes:
            print("\n🗂️ No staged changes")
            sys.exit(1)

        interaction_loop(staged_changes)

    except KeyboardInterrupt:
        print("\n\n❌ AI commit exited.")


if __name__ == "__main__":
    run()
