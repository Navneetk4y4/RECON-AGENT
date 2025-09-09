# RECON-AGENT

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/Navneetk4y4/RECON-AGENT/blob/master/LICENSE)

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

## Features

This reconnaissance agent provides a comprehensive suite of tools for various security tasks, with more to be added in the future. Currently, it includes:

-   **Nmap:** Perform network scanning to discover hosts and services.
-   **Dig:** Conduct DNS queries for detailed DNS information.
-   **Nslookup:** Resolve domain names and IP addresses.
-   **WHOIS:** Retrieve domain registration information.
-   **Amass:** Perform advanced subdomain enumeration.
-   **Subfinder:** Discover subdomains using various techniques.
-   **WhatWeb:** Identify web technologies used on websites.



## Setup and Installation

To set up and run this project, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Navneetk4y4/RECON-AGENT.git
    cd RECON-AGENT
    ```

2.  **Install dependencies:**
    ```bash
    uv pip install -e .
    ```



## AI Client Configuration

To integrate this reconnaissance agent with your AI client, configure it with the following settings:

```json
{
  "mcpServers": {
    "recon-agent": {
      "command": "path/to/your/python_executable",
      "args": [
        "path/to/your/recon_agent/server.py"
      ],
      "env": {
        "PYTHONPATH": "path/to/your/recon_agent"
      }
    }
  }
}
```

Once the server is running, you can interact with the reconnaissance tools through the MCP framework. Each tool can be invoked using the `run_mcp` command with the appropriate tool name and parameters. Refer to the FastMCP documentation for more details on how to use the tools and their available parameters.

## Contributing

Contributions are welcome! Please feel free to submit issues, pull requests, or suggest improvements. See `CONTRIBUTING.md` for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.