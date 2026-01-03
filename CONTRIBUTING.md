# Contributing to Awesome Agent RAG & LLM Apps

Thank you for your interest in contributing to **Awesome Agent RAG & LLM Apps**! We welcome contributions from the community to help make this the best collection of AI agents and RAG applications.

## 🚀 Getting Started

### Prerequisites

To contribute to this project, you will need the following tools installed on your system:

- **Git**: For version control.
- **[uv](https://github.com/astral-sh/uv)**: An extremely fast Python package installer and resolver. We use `uv` to manage dependencies and virtual environments.
- **[GitHub CLI (gh)](https://cli.github.com/)**: For interacting with GitHub from the command line (creating issues, PRs, etc.).

### Installation

1.  **Fork and Clone the Repository**:
    Use the GitHub CLI to fork and clone the repository:
    ```bash
    gh repo fork mustafabozkaya/Awesome_Agent_Rag_LMMs_apps --clone
    cd Awesome_Agent_Rag_LMMs_apps
    ```

2.  **Initialize Environment**:
    We use `uv` to manage the environment. You can sync the dependencies using:
    ```bash
    uv sync
    ```
    This will create a virtual environment and install all necessary dependencies defined in `pyproject.toml` (or `requirements.txt` if we are transitioning).

## 📂 Project Structure

The repository is organized into several categories:

- `starter_ai_agents/`: Beginner-friendly agents.
- `advanced_ai_agents/`: Complex, multi-agent systems.
- `rag_tutorials/`: RAG implementation examples.
- `voice_ai_agents/`: Voice-enabled agents.
- `mcp_ai_agents/`: Agents using the Model Context Protocol.

## 🤝 How to Contribute

### Adding a New Agent or App

1.  **Choose the Right Category**: Decide which directory your project belongs to.
2.  **Create a Directory**: Create a new folder for your project. Use `snake_case` for naming.
3.  **Add Your Code**: Include all source code.
4.  **Add a README**: **Crucial!** Every project MUST have its own `README.md` explaining:
    - What the agent does.
    - How to set it up.
    - How to run it.
    - Dependencies.
5.  **Add Requirements**: Include a `requirements.txt` or `pyproject.toml` for your specific project.

### Updating Documentation

- If you change the directory structure or add a new project, please update the main `README.md` to include a link to your new project in the appropriate section.
- Ensure all links are working.

## 🔄 Pull Request Process

1.  **Create a Branch**:
    ```bash
    git checkout -b feature/my-new-agent
    ```
2.  **Make Changes**: Add your code and documentation.
3.  **Verify**:
    - Ensure your code runs.
    - Check that you have updated the main `README.md`.
4.  **Push and Create PR**:
    ```bash
    git push origin feature/my-new-agent
    gh pr create --title "Add [Agent Name]" --body "Description of the agent..."
    ```

## 📝 Style Guide

- **Code**: Follow PEP 8 for Python code.
- **Commits**: Write clear, descriptive commit messages.
- **Documentation**: Use Markdown. Be concise but helpful.

Thank you for contributing! 🌟
