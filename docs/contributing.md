# Contributing

## Dev Containers

This project includes a [dev container](https://containers.dev/) configuration for a consistent development environment.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [VS Code](https://code.visualstudio.com/) with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Getting Started

1. Clone the repo:
```bash
   git clone --recurse-submodules https://github.com/you/gasp.git
```
2. Open in VS Code
3. When prompted, click **"Reopen in Container"** (or run `Dev Containers: Reopen in Container` from the command palette)
4. The container will build with all dependencies (Python, CUDA Toolkit)

### Without VS Code

```bash
docker build -t gasp-dev .
docker run -it --rm -v $(PWD):/app gasp-dev /bin/bash
```