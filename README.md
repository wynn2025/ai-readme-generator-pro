# AI README Generator Pro v1.0.0

> One-click professional README.md generator for any project

## Features

- **Smart Analysis**: Auto-scan project, detect language, extract functions/classes/entry points
- **Multi-language**: Python / Node.js / Go / Rust / Java / C++
- **3 Template Styles**: minimal / professional / full
- **AI Enhancement**: Optional DeepSeek API to auto-improve README content
- **GitHub Integration**: Pass a GitHub URL, auto-clone and analyze
- **Zero Dependencies**: Pure Python stdlib, works out of the box
- **CI/CD Ready**: Automate README generation in your workflow

## Quick Start

```bash
# Analyze local project (professional template, default)
python ai_readme_generator_pro.py /path/to/your/project

# Analyze GitHub repository
python ai_readme_generator_pro.py https://github.com/user/repo

# Specify template style
python ai_readme_generator_pro.py ./my-project --template full

# Output to file
python ai_readme_generator_pro.py ./my-project -o README.md

# Preview without writing
python ai_readme_generator_pro.py ./my-project --dry-run

# Show analysis details
python ai_readme_generator_pro.py ./my-project -v

# AI Enhancement with DeepSeek API
python ai_readme_generator_pro.py ./my-project --api-key sk-xxx
```

## Usage Examples

### Example 1: Local Python Project

```bash
python ai_readme_generator_pro.py /home/user/my-flask-app --template professional -o README.md -v
```

Generates badges, directory tree, install instructions, API reference, contributing guide.

### Example 2: GitHub Repository

```bash
python ai_readme_generator_pro.py https://github.com/pallets/flask --template full --dry-run
```

### Example 3: CI/CD Integration

```yaml
# .github/workflows/readme.yml
name: Auto README
on: [push]
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python ai_readme_generator_pro.py . -o README.md
      - uses: stefanzweifel/git-auto-commit-action@v5
```

## Generated README Sections

| Section | Content |
|---------|---------|
| Title | Project name |
| Badges | Language / Files / Lines / License |
| Description | Auto-generated project overview |
| TOC | Anchor links (professional/full) |
| Features | Function/class counts, language info |
| Structure | Directory tree |
| Installation | Auto-detect language install commands |
| Usage | Run commands based on entry file |
| API Reference | Public function and class signatures |
| Testing | Test commands (if test files exist) |
| Contributing | Standard PR workflow |
| License | MIT (if LICENSE file detected) |

## Template Comparison

| Template | Use Case | Sections |
|----------|----------|----------|
| minimal | Small projects/scripts | Title+Features+Structure+Install+Usage |
| professional | Medium projects (default) | All sections |
| full | Large/open-source projects | All sections with details |

## Requirements

- Python 3.7+
- Optional: DeepSeek API Key (for AI enhancement)
- Git (for GitHub repository analysis)

## License

MIT License
