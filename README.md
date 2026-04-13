# Arkady

A terminal-based AI coding agent powered by the Gemini API. Navigate to any codebase, run `arkady`, and talk to it — it will explore the code, reason about it, and take action autonomously.

## What it does

- Lists and reads files in your current directory
- Writes and modifies files
- Runs Python files and inspects output
- Maintains conversation history across turns in a single session
- Iterates autonomously using a tool-calling loop until it has a final answer

## Project structure

```
mini-claude-code/
├── pyproject.toml
├── arkady/
│   ├── main.py                     # Entry point, REPL loop, agent loop
│   ├── prompts.py                  # System prompt versions
│   ├── config.py                   # Configuration (e.g. MAX_CHARS)
│   └── functions/
│       ├── get_files_info.py       # List files in a directory
│       ├── get_file_content.py     # Read file contents
│       ├── write_file.py           # Write or overwrite a file
│       ├── run_python_file.py      # Execute a Python file
│       └── genai/
│           └── call_function.py    # Tool dispatcher and schema registry
└── calculator/                     # Sample codebase to test the agent on
```

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- A Gemini API key — get one free at [aistudio.google.com](https://aistudio.google.com)

## Installation

Clone the repo and install `arkady` as a global tool:

```bash
git clone <repo-url>
cd mini-claude-code
uv tool install .
```

`arkady` is now available as a command anywhere on your system.

## Usage

Navigate to any project and run:

```bash
cd /path/to/your/project
arkady --provider google --api-key YOUR_KEY
```

Arkady will ask for permission to access the directory, then drop you into an interactive session:

```
Arkady wants to access:
  /home/user/myproject

Allow? [y/N]: y

Arkady is ready. Type your request, or 'exit' to quit.

you: how does authentication work in this codebase?
  > get_files_info({'directory': '.'})
  > get_file_content({'file_path': 'auth/middleware.py'})

Arkady: Authentication is handled by ...

you: fix the bug where expired tokens aren't being rejected
  > get_file_content({'file_path': 'auth/middleware.py'})
  > write_file({'file_path': 'auth/middleware.py', ...})
  > run_python_file({'file_path': 'tests/test_auth.py'})

Arkady: Fixed. The token expiry check was ...

you: exit
```

**Flags:**
- `--provider google` — LLM provider to use (currently only `google` is supported)
- `--api-key KEY` — API key for the provider
- `--verbose` — print token usage and raw function responses each iteration

## Try it on the sample codebase

The `calculator/` directory contains a simple infix expression evaluator you can use to test the agent:

```bash
cd calculator
arkady --provider google --api-key YOUR_KEY
```

```
you: how does operator precedence work here?
you: fix the bug: 3 + 7 * 2 gives 20 instead of 17
```

## Rate limits

The free tier of the Gemini API allows 5 requests per minute on `gemini-2.5-flash`. The agent handles rate limit errors automatically by waiting and retrying. For heavier use, add billing at [aistudio.google.com](https://aistudio.google.com).

## Development

To work on Arkady itself:

```bash
git clone <repo-url>
cd arkady
uv sync
uv run arkady --provider google --api-key YOUR_KEY
```

Run tests:

```bash
uv run pytest
```
