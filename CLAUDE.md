# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Package Management (using uv)**
```bash
uv sync                   # Install/update dependencies
uv add <package>          # Add new dependency
uv add --group dev <pkg>  # Add development dependency
```

**Code Quality**
```bash
ruff check src/           # Lint code
ruff format src/          # Format code
ruff check --fix src/     # Auto-fix linting issues
mypy src/                 # Type checking
```

**Running the Bot**
```bash
python -m src.suisei --log DEBUG    # Run with debug logging
python -m src.suisei --log INFO     # Run with info logging (default)
```

## Architecture Overview

**Suisei** is an AI-powered Discord bot with a layered architecture supporting both Claude and OpenAI APIs.

### Core Layers

1. **Discord Layer** (`src/suisei/discord/`)
   - `client.py`: Singleton BotClient managing Discord connection
   - `event.py`: Discord event handlers
   - `commands/`: Slash command implementations (`/fixpy`, access control)

2. **Adapter Layer** (`src/suisei/adapters/`)
   - `chat.py`: Message abstraction (`ChatMessage`, `ChatHistory`)
   - `response.py`: Response formatting and handling

3. **Infrastructure Layer** (`src/suisei/infrastructure/`)
   - `api/`: API clients for Anthropic Claude and OpenAI
   - `db/dao/`: Database access objects with async SQLite support

4. **Configuration & Utilities**
   - `env.py`: Environment management with `.env` file support
   - `types.py`: Type definitions (`ClaudeParams`, `GPTParams`)
   - `utils/`: Logging, error handling, and access control decorators

### Key Patterns

- **Singleton Pattern**: BotClient for Discord connection management
- **DAO Pattern**: Database abstraction through Data Access Objects
- **Decorator Pattern**: Error handling and access control via decorators
- **Async/Await**: Full async support throughout the application

## Configuration Requirements

- `.env` file with Discord token, API keys, admin users, authorized servers
- `.prompt.yml` file for system prompts (planned)
- Python 3.12 required

## Code Style Standards

- **Line Length**: 99 characters (following team agreement)
- **Quotes**: Double quotes preferred
- **Type Checking**: Strict MyPy configuration - all functions must have type annotations
- **Formatting**: Ruff with trailing commas enforced, docstring code formatting enabled
- **Import Style**: Wildcard imports allowed (F403 ignored)

## Database

Uses async SQLite (`aiosqlite`) with DAO pattern for user access control and persistence.

## Security Considerations

- User access level system with database persistence
- Admin user configuration via environment variables
- Server authorization controls
- Graceful error handling without exposing internals
