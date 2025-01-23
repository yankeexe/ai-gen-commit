## 🐙 AI Commit Generator

Use AI to generate commit message for your staged changes.

<a href="https://youtu.be/1y2TohQdNbo">
<img src="https://i.imgur.com/cwdzCUw.gif" width="800">
</a>


## ⚡️ Features

- Use local models (via Ollama) or remote models (with OpenAI API compatible providers like:  `openai`, `groq`, `gemini`, `togetherai`, `deepseek`)
- Use your preferred AI model
- Regenerate commit messages until you find the perfect one
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
export AI_COMMIT_PROVIDER="gemini" or "openai" or "togetherai" or "groq" or "deepseek"
```

then enable remote mode:

```sh
aic -r
```

Specify the model to use based on the provider's API key:

```sh
export AI_COMMIT_PROVIDER="openai"
aic -r -m "gpt-4o-2024-11-20"

# ---

export AI_COMMIT_PROVIDER="gemini"
aic -r -m "gemini-1.5-flash"
```

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
