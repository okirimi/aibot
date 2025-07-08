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
python -m src.aibot --log DEBUG    # Run with debug logging
python -m src.aibot --log INFO     # Run with info logging (default)
python -m src.aibot --log WARNING  # Run with warning logging
python -m src.aibot --log ERROR    # Run with error logging
```

## Architecture Overview

**aibot** is an AI-powered Discord bot with a layered architecture supporting Claude, OpenAI, and Gemini APIs.

### Core Layers

1. **Discord Layer** (`src/aibot/discord/`)
   - `client.py`: Singleton BotClient managing Discord connection
   - `commands/`: Slash command implementations (`/chat`, `/fixpy`, `/provider`, access control)

2. **Adapter Layer** (`src/aibot/adapters/`)
   - `chat.py`: Message abstraction (`ChatMessage`, `ChatHistory`)
   - `response.py`: Response formatting and handling

3. **Infrastructure Layer** (`src/aibot/infrastructure/`)
   - `api/`: API clients for Anthropic Claude, OpenAI, and Gemini with factory pattern
   - `db/dao/`: Database access objects with async SQLite support

4. **Services Layer** (`src/aibot/services/`)
   - `prompt_manager.py`: Dynamic and static system prompt management
   - `provider_manager.py`: AI provider selection and configuration
   - `system_prompt.py`: System prompt database operations

5. **Configuration & Utilities**
   - `env.py`: Environment management with `.env` file support
   - `types.py`: Type definitions (`ClaudeParams`, `GPTParams`)
   - `utils/`: Logging, error handling, and access control decorators

### Key Patterns

- **Singleton Pattern**: BotClient and ProviderManager for centralized state management
- **Factory Pattern**: ApiFactory for creating appropriate API clients
- **DAO Pattern**: Database abstraction through Data Access Objects
- **Decorator Pattern**: Error handling and access control via decorators
- **Service Layer**: Business logic separation through dedicated service classes
- **Async/Await**: Full async support throughout the application

## Bot Features

### Discord Commands
- `/chat`: Single-turn chat with AI providers
- `/fixpy`: Python code analysis and debugging assistance
- `/provider`: Configure AI provider settings (admin only)
- Access control commands for user management

### AI Provider Support
- **Anthropic Claude**: claude-sonnet-4 (default)
- **OpenAI GPT**: gpt-4.1 (default)
- **Google Gemini**: gemini-2.5-flash (default)
- Dynamic provider switching with per-user preferences

### System Prompt Management
- Static prompts for consistent behavior
- Dynamic prompts stored in database
- Per-command prompt customization
- Fallback system for reliability

## Configuration Requirements

- `.env` file with Discord token, API keys, admin users, authorized servers (see `.env.sample`)
- `prompts/` directory for system prompts configuration
- `locale/translation-*.json` files for multi-language support (EN/JA)
- Python 3.12 required
- SQLite database file for persistence

## Code Style Standards

- **Line Length**: 99 characters (following team agreement)
- **Quotes**: Double quotes preferred
- **Type Checking**: Strict MyPy configuration - all functions must have type annotations
- **Formatting**: Ruff with trailing commas enforced, docstring code formatting enabled
- **Import Style**: Wildcard imports allowed (F403 ignored)
- **Design Principles**: Follow SOLID and GRASP principles for maintainable code architecture

## Database

Uses async SQLite (`aiosqlite`) with DAO pattern for user access control and persistence.

## Security Considerations

- User access level system with database persistence
- Admin user configuration via environment variables
- Server authorization controls
- Graceful error handling without exposing internals
