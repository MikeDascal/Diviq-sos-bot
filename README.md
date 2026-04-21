# Diviq SOS Bot

A Discord bot for the DiviQ server that watches the `#sos` channel. When a user posts there, the bot opens a DM to ask what they need, then emails the details to the configured recipients.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `DISCORD_TOKEN` | Bot token from the [Discord Developer Portal](https://discord.com/developers/applications) |
| `SOS_CHANNEL_NAME` | Channel name to watch (default: `sos`) |
| `SMTP_SERVER` | SMTP host (default: `smtp.gmail.com`) |
| `SMTP_PORT` | SMTP port (default: `587`) |
| `SMTP_USER` | Email address the bot sends from |
| `SMTP_PASSWORD` | For Gmail, use an [App Password](https://myaccount.google.com/apppasswords), not your login password |
| `EMAIL_RECIPIENTS` | Comma-separated list of addresses to notify |

### 3. Configure the Discord bot

In the [Discord Developer Portal](https://discord.com/developers/applications):

- Under **OAuth2 → URL Generator**, select the `bot` scope with these permissions:
  - Read Messages / View Channels
  - Send Messages
- Under **Bot → Privileged Gateway Intents**, enable **Message Content Intent**

Invite the bot to the DiviQ server using the generated URL.

### 4. Run

```bash
python bot.py
```

## How it works

1. A user posts anything in `#sos`
2. The bot opens a DM and asks them to describe what they need (5-minute reply window)
3. Once they reply, the bot confirms receipt and sends an email to all recipients containing:
   - The user's Discord display name and ID
   - Their original `#sos` message
   - Their detailed DM reply

If a user has DMs disabled, the bot mentions them in `#sos` with instructions to enable DMs.
