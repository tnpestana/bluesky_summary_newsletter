# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running the Application
```bash
# Run the newsletter locally
python src/main.py

# Install dependencies
pip install -r requirements.txt
```

### Testing and Deployment
- No automated tests are configured in this project
- The application is deployed via GitHub Actions daily at 7:00 AM UTC
- Manual triggering: Go to Actions tab → "Daily Bluesky Newsletter" → "Run workflow"

## Architecture Overview

This is a Python-based newsletter system that fetches Bluesky posts, generates AI summaries, and sends them via email. The architecture follows a modular design with clear separation of concerns:

### Core Components

**Main Orchestrator** (`src/main.py`):
- `BlueskySummaryNewsletter` class coordinates all components
- Handles the main workflow: fetch → summarize → email
- Uses dependency injection pattern for component initialization

**Configuration Management** (`src/config_loader.py`):
- `ConfigLoader` class handles YAML configuration and environment variables
- Supports template variable substitution (e.g., `${BLUESKY_USERNAME}`)
- Centralizes all configuration access

**Data Fetching** (`src/bluesky_client.py`):
- `BlueskyClient` handles Bluesky API integration using atproto library
- Fetches posts from multiple users within specified time window
- Returns structured data for downstream processing

**AI Processing** (`src/ai_summarizer.py`):
- `AISummarizer` supports multiple AI providers (Groq, OpenAI, Anthropic)
- Generates markdown summaries from collected posts
- Configurable models and endpoints via config.yaml

**Email Delivery** (`src/email_sender.py`):
- `EmailSender` handles SMTP email delivery
- Supports multiple recipients
- Generates HTML email with post summaries

### Configuration Structure

The system uses `config.yaml` for settings and environment variables for secrets:

- **Bluesky Config**: Username/password from environment variables
- **AI Config**: Provider, model, and API endpoint configuration
- **Email Config**: SMTP settings and recipient management
- **Settings**: Time window (`hours_lookback`) and post limits (`max_posts_per_user`)

### Environment Variables Required

Production deployment requires these GitHub secrets:
- `BLUESKY_USERNAME`, `BLUESKY_PASSWORD`: Bluesky authentication
- `EMAIL_SENDER_EMAIL`, `EMAIL_SENDER_PASSWORD`: Gmail SMTP credentials
- `EMAIL_RECIPIENTS`: Comma-separated recipient list
- `GROQ_API_KEY`: AI service authentication

### Key Dependencies

- `atproto`: Bluesky API client
- `openai`: AI provider interface (used for multiple providers)
- `requests`: HTTP client
- `PyYAML`: Configuration parsing
- `python-dotenv`: Environment variable management

### Scheduled Execution

The system runs automatically via GitHub Actions (`.github/workflows/daily-newsletter.yml`):
- Daily execution at 7:00 AM UTC
- Creates temporary .env file from secrets
- Runs `python src/main.py`
- Cleans up environment after execution