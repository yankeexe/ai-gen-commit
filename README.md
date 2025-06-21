## 🐙 AI Commit Generator

Use AI to generate commit message for your staged changes.

<a href="https://youtu.be/1y2TohQdNbo">
<img src="https://i.imgur.com/cwdzCUw.gif" width="800">
</a>


## ⚡️ Features

- Use local models (via Ollama) or remote models (with OpenAI API compatible providers like:  `openai`, `groq`, `gemini`, `togetherai`, `deepseek`, `qwen`) or your [custom provider](#-bring-your-own-provider).
- Regenerate commit messages until you find the perfect one
- In-place editing of generated commit
- Define your custom commit message format
- Simple CLI interface with debug mode

## ⚡️ Install

```sh
pip install ai-gen-commit
```

## ✨ Generate Commit messages

In any git directory with staged changes, run:

```sh
aic
```

### 🔍 Run in debug mode

```sh
aic -d
```
### 🦙 Local Mode [Specify model to use]

```sh
aic -m <model-name>

aic -m "llama3.2:3b"

# OR

export OLLAMA_MODEL="llama3.2:3b"
```

### 🛜 Remote Mode

To run in remote mode, export your API keys as:

```sh
export OPENAI_API_KEY=<your-api-key>
```

Specify which remote provider to use:

```sh
export AI_COMMIT_PROVIDER="gemini" or "openai" or "togetherai" or "groq" or "deepseek" or "mistral"
```

then enable remote mode:

```sh
aic -r
```

Specify the model to use based on the provider:

```sh
export AI_COMMIT_PROVIDER="groq"
export AI_COMMIT_MODEL="qwen-2.5-32b" # pass the model as env var
aic -r

# ---

export AI_COMMIT_PROVIDER="openai"
aic -r -m "gpt-4o-2024-11-20" # pass the model as flag

# ---

export AI_COMMIT_PROVIDER="gemini"
aic -r -m "gemini-1.5-flash"
```

### ✨ Bring your own Provider

You can use any OPEN AI compatible provider/server for commit generation.

```sh
export AI_COMMIT_PROVIDER=custom # should be set to custom
export AI_COMMIT_MODEL=llama3.2:3b # example
export AI_COMMIT_PROVIDER_BASE_URL=http://localhost:11434/v1 # example
export OPENAI_API_KEY=<your-api-key> # if your custom provider requires one
```

### 📝 In-place Editing

[🎥 Watch the Demo](https://www.linkedin.com/feed/update/urn:li:activity:7293488744391675905/)

Set your editor environment variable:

```sh
export EDITOR=vim
export EDITOR=nvim

# For VSCode
export EDITOR='code --wait'
```

After commit message is generated, press `e` to edit using the defined `$EDITOR`.

Defaults to using `vi`.

### 🤖 Custom commit message format

Users can generate commit messages based on the format and instructions defined in the system prompt.

**To define system prompt on project level**

1. Create a `.ai-commit` file in your git repository's root directory (same location as the `.git` folder)
2. Add your system prompt to this file

**To define a global system prompt**

1. Create a file on `~/.$HOME/.ai-commit`
2. Add your system prompt to this file

| Project-level System Prompt > Global System Prompt >  [Built-in system prompt](https://github.com/yankeexe/ai-gen-commit/blob/5c8b6374752a84046d8ce5d5a78fe0481ce1362d/ai_commit/prompts.py#L3-L29).

## Getting Help

```sh
aic -h
```

## 🔨 Development

### 👀 Prerequisites Local mode [default]

- [ollama](https://ollama.dev/download)


### 🚀 Setting up

```sh
make setup
```
