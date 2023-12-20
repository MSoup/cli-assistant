# GPT CLI

This command-line interface (CLI) tool enables the use of OpenAI's GPT models directly from your terminal. It is designed to be cost-effective by utilizing the latest "turbo" versions of the GPT models, including GPT 3.5 turbo and GPT 4 turbo, as of December 2023.

## Table of Contents

-   [Prerequisites](#prerequisites)
-   [Installation](#installation)
-   [Configuration](#configuration)
-   [Usage](#usage)

## Prerequisites

Before you begin, ensure you are on:

-   a Unix system (no guarantees that this will work for Windows)
-   Python 3.11 or higher

## Installation

Follow these steps to set up the GPT CLI on your system:

### Set up the install script.

-   In `install_scripts/install.sh`, change the below parameters to match your system. By default `SOURCE_CONFIG_FILE_PATH` is `~`, and `CONFIG_FILENAME` is `.zshrc`.

```bash
SOURCE_CONFIG_FILE_PATH="~"
CONFIG_FILENAME=".zshrc"
```

### Run the provided install script

```bash
cd install_scripts
sh install.sh
```
