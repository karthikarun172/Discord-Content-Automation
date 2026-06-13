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

if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)