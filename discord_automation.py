import os
import discord
from discord.ext import commands
import requests
from google import genai
from google.genai import types
import random
import re

# Google Workspace API Client modules
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env_local")
load_dotenv(env_path)
# ==============================================================================
# CONFIGURATION BLOCK
# ==============================================================================
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
GOOGLE_DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "YOUR_FOLDER_ID")

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

# Set up Discord bot intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def get_google_services():

    creds = Credentials.from_authorized_user_file(
        "token.json",
        SCOPES
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return (
        build("docs", "v1", credentials=creds),
        build("drive", "v3", credentials=creds)
    )

def push_workspace_to_docs(title, structural_text):
    """
    Builds a structured asset document via Google Cloud, embeds 
    open-source visual illustrations, and saves it into the video assets root.
    """
    try:
        docs_service, drive_service = get_google_services()
        print("STEP 1: Creating document")
        
        # Step 1: Create empty baseline document template file
        doc_meta = {'title': f"{title} - Production Blueprint"}
        doc = docs_service.documents().create(body=doc_meta).execute()
        doc_id = doc.get('documentId')
        print(f"Created Doc ID: {doc_id}")
        # Append standard text headers safely to document timeline body
        body_content = structural_text + "\n\n--- AUTO-GENERATED STORYBOARD BLUEPRINT ---\n\n"
        requests_payload = [{
            'insertText': {
                'location': {'index': 1},
                'text': body_content
            }
        }]
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests_payload}).execute()
        
        # Step 2: Dynamically construct public infographic preview assets for embedding
        encoded_query = requests.utils.quote(f"A clean minimalist concept dashboard diagram illustrating {title}")
        public_img_url = f"https://image.pollinations.ai/p/{encoded_query}?width=600&height=600&nologo=true"
        
        
        # Step 3: File document inside shared project folder
        print(f"Folder ID: {GOOGLE_DRIVE_FOLDER_ID}")
        if GOOGLE_DRIVE_FOLDER_ID and GOOGLE_DRIVE_FOLDER_ID != "YOUR_FOLDER_ID":
            file_meta = drive_service.files().get(fileId=doc_id, fields='parents').execute()
            previous_parents = ",".join(file_meta.get('parents', []))
            drive_service.files().update(
                fileId=doc_id,
                addParents=GOOGLE_DRIVE_FOLDER_ID,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            print("Document moved successfully")
            
        return f"https://docs.google.com/document/d/{doc_id}/edit"
    except Exception as e:
        print(f"❌ Document compilation thread exception: {str(e)}")
        return None

# System prompt enforcing strict documentary formatting frameworks
MASTER_SYSTEM_INSTRUCTION = (
    "You are DecisionForge, an enterprise content orchestration pipeline. "
    "Your job is to generate premium documentary-style breakdown files following the exact structure below. "
    "You must return clear, explicit markdown sections containing:\n\n"
    "--- BLUEPRINT WORKSPACE STRUCTURE ---\n\n"
    "1. METADATA: 3 high-impact Title Choice variations, and an optimized YouTube description filled with CTAs.\n"
    "2. SECTION 1 - COLD HOOK SCRIPT: An aggressive, fast-paced opening hook (45-60 seconds) structured for a narrator.\n"
    "3. SECTION 2 - DUAL-SEGREGATED TIMELINE: A comprehensive 7-10 minute video script divided into explicitly labeled blocks: "
    "'[HEYGEN TALKING HEAD AVATAR]' (Sleek executive setting delivering mindset shifts) versus '[AUTOMATED VOICE-OVER]' (B-Roll segments).\n"
    "4. SECTION 3 - AUTOMATION SCRAPING TARGETS:\n"
    "   - GIPHY_KEYWORDS: A comma-separated python list of high-level moods, nouns, actions, or emotions ONLY (e.g., 'Revolutionary', 'Mindblown', 'Crypto Crash'). No specific brands/years.\n"
    "   - SPECIFIC_IMAGE_PROMPTS: Explicit prompts for historical references, specific eras, blueprints, or technical diagrams (e.g., '1970s corporate office', '4 quadrant decision matrix grid').\n"
    "5. REPURPOSE CHANNELS: Complete text structures to instantly deploy this content as an X thread, a text framework for a LinkedIn post, and a YouTube Shorts concept hook."
)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    print("Servers:")
    for guild in bot.guilds:
        print(f"- {guild.name} ({guild.id})")
    print(f"🚀 DecisionForge Cloud Orchestrator active. Connected as: {bot.user.name}")

import asyncio


async def generate_content_with_retry(
    client,
    model,
    contents,
    config,
    max_attempts=5,
):
    """
    Retry Gemini requests using exponential backoff.

    Delays:
    1s -> 2s -> 4s -> 8s -> 16s
    """

    for attempt in range(max_attempts):
        try:
            return await asyncio.to_thread(
                lambda: client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                )
            )

        except Exception as e:

            error_text = str(e)

            retryable_errors = [
                "503",
                "UNAVAILABLE",
                "RESOURCE_EXHAUSTED",
                "429",
            ]

            should_retry = any(
                err in error_text
                for err in retryable_errors
            )

            if not should_retry:
                raise

            if attempt == max_attempts - 1:
                raise

            wait_time = (2 ** attempt) + random.uniform(0, 1)

            print(
                f"⚠️ Gemini retry "
                f"{attempt + 1}/{max_attempts} "
                f"after {wait_time}s"
            )

            await asyncio.sleep(wait_time)

async def send_long_message(ctx, text, chunk_size=1900):
    for i in range(0, len(text), chunk_size):
        await ctx.send(text[i:i + chunk_size])

@bot.command(name="suggest")
async def process_suggestion_flow(ctx, *, topic_prompt: str):

    await ctx.send(
        f"🧠 Compiling workspace for '{topic_prompt}'..."
    )

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        user_prompt = (
            "Develop a comprehensive high-retention "
            f"video documentary script configuration "
            f"from scratch covering this concept: {topic_prompt}"
        )

        response = await generate_content_with_retry(
            client=client,
            model="gemini-2.5-flash-lite",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=MASTER_SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=8192,
            ),
        )
        safe_filename = re.sub(
            r'[^a-zA-Z0-9_-]',
            '-',
            topic_prompt.lower()
        )

        filename = f"{safe_filename}.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)

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

    doc_link = push_workspace_to_docs(
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
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    user_prompt = f"Analyze this pasted rough content text block, align its storytelling pacing to our guidelines, and extract all asset tags:\n\n{raw_script_block}"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=MASTER_SYSTEM_INSTRUCTION,
                temperature=0.3  # Lower temperature prevents code manipulation shifts while keeping strict structural syntax
            )
        )
        
        doc_link = push_workspace_to_docs("Optimized Script Script", response.text)
        if doc_link:
            await ctx.send(f"✅ **Rough copy aligned and restructured!** Sections 1-3 compiled into your workspace.\n🔗 **Google Doc Portal:** {doc_link}")
        else:
            await ctx.send("⚠️ Structure optimized, but an error occurred uploading to Google Workspace.")
    except Exception as error:
        await ctx.send(f"❌ System failure inside refactoring engine: {str(error)}")

if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)