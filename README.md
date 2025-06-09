# Suisei Bot

![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white&style=flat&labelColor=24292e)
![License](https://img.shields.io/badge/License-BSD--3--Clause-orange.svg?style=flat&labelColor=24292e)

> [!CAUTION]
> Currently, the application only supports running in a local environment. If you plan to run it in a server environment, make sure to manage the .env file or environment variables appropriately.

## Getting Started

### Prerequisites

The following preparations are required:
  - Python runtime environment
  - Anthropic API Key
  - OpenAI API Key
  - Discord Bot configuration

For detailed information, please refer to [PREREQUISITES.md](https://github.com/okirimi/suisei/blob/main/docs/PREREQUISITES.md).

### Set up

**1. Clone repository and install dependencies**

```
# ----- clone repo -----
git clone https://github.com/okirimi/suisei.git

# ----- install dependencies -----
# with uv
uv sync

# without uv
pip install -r requirements.txt
```

**2. Prepare env file**

This application requires a `.env` file for configuration. Follow these steps:

  - Copy the `.env.example` file and rename it to `.env`
  - Fill in all the required values in the `.env` file

**3. Customize system prompts**

> [!IMPORTANT]
> If you use this bot in public contexts or server environments, it is strongly recommended to configure the system prompt appropriately.

**Example**:

Safe System Prompt Design
- Include explicit instructions to prohibit harmful code or actions
- Restrict access to sensitive information (e.g., API keys, environment variables)
- Implement prompt injection protection (e.g., input sanitization and validation)

Multi-User Considerations
- Strictly isolate user sessions and data
- Prevent input/output that could affect other users

Resource Management
- Introduce rate limiting and concurrency controls to avoid overload or abuse

Logging and Privacy
- Avoid storing personal data in logs; use anonymization or minimal logging
- Use logs to detect and monitor suspicious behavior (e.g., injection attempts)

### Run the Bot

Finally, make sure all values in the `.env` file and `.prompt.yml` file are filled in correctly, and then execute the following:

```
python -m src.suisei --log <log_level>
```

**Note**: The `--log <log_level>` parameter is optional and allows you to set the log level. Available values are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (case-insensitive). If not specified, `INFO` will be used as default.
