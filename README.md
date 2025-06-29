# Bluesky Summary Newsletter

Automatically fetch posts from your favorite Bluesky users, generate AI summaries, and email them to yourself daily.

## Features

- 🦋 **Bluesky Integration** - Monitor any Bluesky users
- 🤖 **AI Summaries** - Powered by Groq (free Llama3)
- 📧 **Email Delivery** - Send to multiple recipients
- ⏰ **Scheduled Runs** - Daily automation via GitHub Actions
- 🆓 **100% Free** - No paid services required

## Quick Setup

### 1. Get Your API Keys

**Bluesky App Password:**
1. Go to [Bluesky Settings](https://bsky.app/settings)
2. Create an App Password for "Newsletter Script"

**Groq API Key (Free):**
1. Sign up at [Groq](https://groq.com)
2. Get your API key from the console

**Gmail App Password:**
1. Enable 2FA on your Gmail account
2. Generate an App Password for this script

### 2. Local Setup (Optional)

```bash
# Clone the repository
git clone <your-repo-url>
cd bluesky-summary-newsletter

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Edit config.yaml with your desired Bluesky users and email settings

# Test locally
python src/main.py
```

### 3. GitHub Actions Setup (Automated)

1. **Push to GitHub** (if you haven't already)
2. **Add Repository Secrets:**
   - Go to your repo → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `BLUESKY_USERNAME`: your-username.bsky.social
     - `BLUESKY_PASSWORD`: your-bluesky-app-password
     - `EMAIL_SENDER_PASSWORD`: your-gmail-app-password
     - `GROQ_API_KEY`: your-groq-api-key

3. **Configure the Newsletter:**
   - Edit `config.yaml` to set:
     - Bluesky users to monitor
     - Your email addresses
     - Email subject

4. **Test the Workflow:**
   - Go to Actions tab → "Daily Bluesky Newsletter" → "Run workflow"

## Configuration

### Monitored Users (`config.yaml`)
```yaml
bluesky_users:
  - "bsky.app"
  - "your-favorite-user.bsky.social"
```

### Email Settings
```yaml
email:
  sender_email: "your-email@gmail.com"
  recipient_emails:
    - "recipient1@example.com"
    - "recipient2@example.com"
  subject: "Daily Bluesky Summary"
```

### Schedule
The newsletter runs daily at 9:00 AM UTC. To change:
1. Edit `.github/workflows/daily-newsletter.yml`
2. Modify the cron expression: `'0 9 * * *'`

## Available AI Models

**Groq (Free, Fast):**
- `llama3-8b-8192` (default, fastest)
- `llama3-70b-4096` (slower, higher quality)
- `mixtral-8x7b-32768` (good balance)

## Troubleshooting

**No posts found:**
- Check if the Bluesky users are active
- Adjust `hours_lookback` in config

**Email not sending:**
- Verify Gmail App Password
- Check sender email matches your Gmail

**GitHub Actions failing:**
- Verify all secrets are set correctly
- Check the Actions logs for specific errors

## Architecture

```
src/
├── main.py           # Main orchestrator
├── bluesky_client.py # Bluesky API integration
├── ai_summarizer.py  # AI summary generation
├── email_sender.py   # Email functionality
└── config_loader.py  # Configuration management
```

## Contributing

Feel free to fork and customize for your needs! Common modifications:
- Add more AI providers
- Support other social platforms
- Customize email templates
- Add web interface

## License

MIT License - feel free to use and modify!