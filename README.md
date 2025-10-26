# linkp

**linkp** is an AI-powered tool that automates daily LinkedIn developer progress posts. It tracks your git activity, generates concise AI summaries of your work, creates engaging visuals, and posts updates directly to LinkedIn.

## Features

- Tracks daily git commits and file changes
- Summarizes your progress using OpenAI
- Generates custom visuals for your posts
- Posts updates to LinkedIn automatically
- CLI interface for easy integration into your workflow

## Installation

```bash
pip install linkp
```

## Usage
initialize linkp by run
```bash
linkp init
```
that will generate linkp.env and md 

then everyday you make changes you just run this command below

```bash
linkp run
```

## Configuration

Set up your `.env` file with the required API keys and LinkedIn credentials.

## License

MIT
