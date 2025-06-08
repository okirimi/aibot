# Suisei Bot

![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white&style=flat&labelColor=24292e)
![License](https://img.shields.io/badge/License-BSD--3--Clause-orange.svg?style=flat&labelColor=24292e)

> [!CAUTION]
> This project is currently under development.

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

**3. Write system prompts**

> [!IMPORTANT]
> If you use this bot on public servers or in public contexts, it is strongly recommended to configure the system prompt appropriately.


### Run the Bot

Finally, make sure all values in the `.env` file and `.prompt.yml` file are filled in correctly, and then execute the following:

```
python -m src.comet --log <log_level>
```

**Note**: The `--log <log_level>` parameter is optional and allows you to set the log level. Available values are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (case-insensitive). If not specified, `INFO` will be used as default.
