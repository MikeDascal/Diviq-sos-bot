import asyncio
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SOS_CHANNEL_NAME = os.getenv("SOS_CHANNEL_NAME", "sos")

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_RECIPIENTS = [e.strip() for e in os.getenv("EMAIL_RECIPIENTS", "").split(",") if e.strip()]

DM_TIMEOUT = 300  # seconds the bot waits for the user's DM reply

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Tracks users mid-conversation so a second SOS message doesn't re-trigger the flow
active_conversations: set[int] = set()


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (id: {client.user.id})")
    print(f"Listening for messages in #{SOS_CHANNEL_NAME}")


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if not isinstance(message.channel, discord.TextChannel):
        return

    if message.channel.name.lower() != SOS_CHANNEL_NAME.lower():
        return

    user = message.author
    if user.id in active_conversations:
        return

    active_conversations.add(user.id)
    try:
        await _handle_sos(message)
    finally:
        active_conversations.discard(user.id)


async def _handle_sos(message: discord.Message):
    user = message.author

    try:
        dm = await user.create_dm()
    except discord.Forbidden:
        try:
            await message.channel.send(
                f"{user.mention} I couldn't open a DM with you. "
                "Please enable **Allow direct messages from server members** in your privacy settings.",
                delete_after=15,
            )
        except discord.Forbidden:
            pass
        return

    await dm.send(
        f"Hi {user.display_name}! I noticed your message in **#{message.channel.name}**.\n\n"
        "Please describe what you need and someone from the team will be notified right away. "
        f"_(You have {DM_TIMEOUT // 60} minutes to reply.)_"
    )

    def is_dm_reply(m: discord.Message):
        return m.author == user and isinstance(m.channel, discord.DMChannel)

    try:
        reply = await client.wait_for("message", check=is_dm_reply, timeout=DM_TIMEOUT)
    except asyncio.TimeoutError:
        await dm.send(
            "Your request timed out. Post in the SOS channel again whenever you're ready."
        )
        return

    await dm.send(
        "Got it — your message has been sent to the team. Someone will follow up with you shortly!"
    )

    _send_email(
        user=user,
        sos_message=message.content,
        detail_message=reply.content,
    )


def _send_email(user: discord.Member, sos_message: str, detail_message: str):
    if not EMAIL_RECIPIENTS:
        print("WARNING: No EMAIL_RECIPIENTS configured — skipping email.")
        return

    subject = f"DiviQ SOS — {user.display_name}"
    body = (
        f"A user submitted an SOS request on the DiviQ Discord server.\n\n"
        f"User:       {user.display_name} (@{user.name})\n"
        f"Discord ID: {user.id}\n\n"
        f"--- Original SOS message ---\n"
        f"{sos_message}\n\n"
        f"--- Details provided via DM ---\n"
        f"{detail_message}\n"
    )

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(EMAIL_RECIPIENTS)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, EMAIL_RECIPIENTS, msg.as_string())
        print(f"Email sent for SOS from {user.name} to {EMAIL_RECIPIENTS}")
    except Exception as exc:
        print(f"ERROR sending email: {exc}")


client.run(TOKEN)
