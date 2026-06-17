import os
import discord
from discord.ext import commands
import re
from utils.logger import logger
from config.settings import (
    DISCORD_BOT_TOKEN,
)
from services.docs_services import (
    push_workspace_to_docs
)
from services.gemini_service import (
    generate_documentary_blueprint,
    optimize_script
)
from services.elevanlabs_service import(
    generate_voice
)
from services.drive_service import (
    upload_audio_to_drive
)

# Set up Discord bot intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")

    logger.info("Servers:")
    for guild in bot.guilds:
        logger.info(f"- {guild.name} ({guild.id})")
    logger.info(f"DecisionForge Cloud Orchestrator active. Connected as: {bot.user.name}")

import asyncio

async def send_long_message(ctx, text, chunk_size=1900):
    for i in range(0, len(text), chunk_size):
        await ctx.send(text[i:i + chunk_size])

@bot.command(name="suggest")
async def process_suggestion_flow(ctx, *, topic_prompt: str):

    await ctx.send(
        f"🧠 Compiling workspace for '{topic_prompt}'..."
    )

    try:

        user_prompt = (
            "Develop a comprehensive high-retention "
            f"video documentary script configuration "
            f"from scratch covering this concept: {topic_prompt}"
        )

        response_text = await generate_documentary_blueprint(
            topic_prompt
        )
        safe_filename = re.sub(
            r'[^a-zA-Z0-9_-]',
            '-',
            topic_prompt.lower()
        )

        filename = f"{safe_filename}.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(response_text)

        await ctx.send(
            "✅ Blueprint generated.",
            file=discord.File(filename)
        )

        os.remove(filename)

    except Exception as e:

        if "503" in str(e) or "UNAVAILABLE" in str(e):
            await ctx.send(
                "⚠️ Gemini is currently overloaded. "
                "Please try again in a few minutes."
            )
        else:
            await ctx.send(
                f"❌ Suggestion generation failed:\n{e}"
            )

            
@bot.command(name="publish")
async def publish_to_docs(ctx):

    if not ctx.message.attachments:
        await ctx.send("Please attach a text file.")
        return

    attachment = ctx.message.attachments[0]

    if not attachment.filename.endswith((".txt", ".md")):
        await ctx.send("Only .txt and .md files are supported.")
        return

    content = (await attachment.read()).decode("utf-8")

    doc_link = await asyncio.to_thread(
        push_workspace_to_docs,
        attachment.filename,
        content
    )

    if doc_link:
        await ctx.send(
            f"✅ Uploaded to Google Docs\n{doc_link}"
        )
    else:
        await ctx.send(
            "❌ Failed to create Google Doc"
        )


@bot.command(name="optimize")
async def process_refactoring_flow(ctx, *, raw_script_block: str):
    """Workflow 2: Accepts a pasted rough script/essay and perfectly formats it into structured production rows."""
    # Slice title preview out of input payload string length safely
    title_preview = raw_script_block[:40].replace("\n", " ") + "..."
    await ctx.send(f"🔧 *DecisionForge Engine refactoring rough draft copy. Structuring assets for: '{title_preview}'...*")
    
    user_prompt = f"Analyze this pasted rough content text block, align its storytelling pacing to our guidelines, and extract all asset tags:\n\n{raw_script_block}"
    
    try:
        response_text = await optimize_script(
            raw_script_block
        )
        
        doc_link = await asyncio.to_thread(
            push_workspace_to_docs,
            "Optimized Script",
            response_text
        )
        if doc_link:
            await ctx.send(f"✅ **Rough copy aligned and restructured!** Sections 1-3 compiled into your workspace.\n🔗 **Google Doc Portal:** {doc_link}")
        else:
            await ctx.send("⚠️ Structure optimized, but an error occurred uploading to Google Workspace.")
    except Exception as error:
        await ctx.send(f"❌ System failure inside refactoring engine: {str(error)}")


@bot.command(name="audio")
async def generate_audio(ctx):

    if not ctx.message.attachments:
        await ctx.send(
            "Please attach a .md or .txt file."
        )
        return

    attachment = ctx.message.attachments[0]

    if not attachment.filename.endswith(
        (".md", ".txt")
    ):
        await ctx.send(
            "Only .md and .txt files are supported."
        )
        return

    await ctx.send(
        "🎙️ Generating ElevenLabs audio..."
    )

    try:

        content = (
            await attachment.read()
        ).decode("utf-8")

        safe_filename = (
            attachment.filename
            .replace(".md", "")
            .replace(".txt", "")
        )

        audio_path = (
            f"generated/audio/"
            f"{safe_filename}.mp3"
        )

        await asyncio.to_thread(
            generate_voice,
            content,
            audio_path
        )

        await ctx.send(
            "✅ Audio generated.",
            file=discord.File(audio_path)
        )

    except Exception as e:

        logger.exception(e)

        await ctx.send(
            f"❌ Audio generation failed:\n{e}"
        )

@bot.command(name="audio-confirm")
async def confirm_audio(ctx):

    if not ctx.message.attachments:
        await ctx.send(
            "Please attach an MP3 file."
        )
        return

    attachment = ctx.message.attachments[0]

    if not attachment.filename.endswith(".mp3"):
        await ctx.send(
            "Only MP3 files are supported."
        )
        return

    await ctx.send(
        "☁️ Uploading approved audio..."
    )

    try:

        local_file = (
            f"generated/audio/"
            f"{attachment.filename}"
        )

        with open(local_file, "wb") as f:
            f.write(
                await attachment.read()
            )

        drive_link = await asyncio.to_thread(
            upload_audio_to_drive,
            local_file
        )

        await ctx.send(
            f"✅ Audio approved and archived\n"
            f"{drive_link}"
        )

    except Exception as e:

        logger.exception(e)

        await ctx.send(
            f"❌ Upload failed:\n{e}"
        )
        
@bot.command(name="avatar")
async def avatar_command(ctx):

    if not ctx.message.attachments:
        await ctx.send(
            "Attach an mp3 file."
        )
        return

    attachment = ctx.message.attachments[0]

    if not attachment.filename.endswith(".mp3"):
        await ctx.send(
            "Only mp3 supported."
        )
        return

    await ctx.send(
        "🎬 Generating avatar video..."
    )

    try:

        os.makedirs(
            "generated/video",
            exist_ok=True
        )

        audio_path = (
            f"generated/audio/"
            f"{attachment.filename}"
        )

        with open(audio_path, "wb") as f:
            f.write(
                await attachment.read()
            )

        video_filename = (
            attachment.filename
            .replace(".mp3", ".mp4")
        )

        video_path = (
            f"generated/video/"
            f"{video_filename}"
        )

        await asyncio.to_thread(
            generate_avatar_video,
            audio_path,
            video_path
        )

        await ctx.send(
            "✅ Avatar video ready",
            file=discord.File(video_path)
        )

        os.remove(audio_path)
        os.remove(video_path)

    except Exception as e:

        logger.exception(e)

        await ctx.send(
            f"❌ Avatar generation failed:\n{e}"
        )
    
if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)