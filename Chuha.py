# chuha.py
import random
import os
import sys
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import traceback
from guess_manager import GuessManager
from scores import ScoreManager
from scores import ScoreManager, LocalScoreManager


#FUNCTIONS------------------------------------------------------------

def chuha_facts():
    return random.choice([
        "Asmit is 5'11 tall.",
        "Asmit has a very cute voice.",
        "Self assigned nickname for Asmit is \"Chuha\".",
        "SirC-----k says that Asmit is Old.",
        "SirD-----n says that Unfortunately Asmit is not Daddy.",
        "SirL-----d calls Dear Asmit a discord Nolifer. How suiting.",
        "Asmit has a cute voice.",
        "SirL-----d says Asmit has become Asexual due to lack of... [Redacted].",
        "Asmit finds confusion in his identity as a Chuha or as a Billi.",
        "Asmit once was Mr. Boombastik as he weighed over 95kgs. Wow so massive. So demure."
    ])

score_mgr = ScoreManager("scores.json")         # global
local_score_mgr = LocalScoreManager("local_scores.json")   # local

#BOT TOKEN----------------------------------------------------------------

TOKEN = os.getenv("BOT_TOKEN")  # set this in your terminal environment

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=["kek ", "k ", "K "], intents=intents, case_insensitive=True)

guess_mgr = GuessManager("memes.json", fuzzy_threshold=0.90)
score_mgr = ScoreManager("scores.json")

class PlayAgainView(View):
    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="Play Again", style=discord.ButtonStyle.primary, custom_id="play_again")
    async def play_again(self, interaction: discord.Interaction, button: Button):
        # Only allow if in same channel
        if interaction.channel.id != self.channel_id:
            await interaction.response.send_message("This button is not for this channel.", ephemeral=True)
            return

        meme = guess_mgr.start_game(self.channel_id)
        await interaction.response.edit_message(content=meme["url"], view=PlayAgainView(self.channel_id))

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    
@bot.command()
async def local(ctx):
    meme = guess_mgr.start_game(ctx.channel.id)
    await ctx.send(f"(Local Game) {meme['url']}")

@bot.command()
async def echo(ctx, *, text: str):
    try:
        # delete the user's command message
        await ctx.message.delete()
    except discord.Forbidden:
        # if bot doesn't have permission, ignore deletion
        pass

    # send the text as bot's message
    await ctx.send(text)


@bot.command()
async def fact(ctx):
    await ctx.send(chuha_facts())

@bot.command()
async def meme(ctx):
    meme = guess_mgr.start_game(ctx.channel.id)
    await ctx.send(meme["url"])  # no button on first meme

@bot.command()
async def reveal(ctx):
    answers = guess_mgr.reveal_answer(ctx.channel.id)
    if not answers:
        return await ctx.send("No active meme in this channel.")
    await ctx.send("Answer(s): " + ", ".join(answers))

@bot.command()
async def leaderboard(ctx, top: int = 10):
    top_list = score_mgr.top(top)
    if not top_list:
        return await ctx.send("No scores yet — start with `kek meme`!")

    lines = []
    for i, (uid_str, pts) in enumerate(top_list, start=1):
        uid = int(uid_str)
        user = bot.get_user(uid)
        # fetch if not cached
        if user is None:
            try:
                user = await bot.fetch_user(uid)
            except Exception:
                user = None
        name = f"{user.name}#{user.discriminator}" if user else uid_str
        lines.append(f"{i}. **{name}** — {pts} pts")

    await ctx.send("🏆 Global leaderboard 🏆\n" + "\n".join(lines))

@bot.event
async def on_message(message):
    if message.author.bot:
        return await bot.process_commands(message)

    # only check guesses if a game is active in this channel
    if message.channel.id in guess_mgr.current:
        correct, matched = guess_mgr.check_guess(message.channel.id, message.content)
        if correct:
            total = score_mgr.add_point(message.author.id, 1)
            await message.channel.send(
                f"✅ {message.author.mention} guessed it! (+1 point — total: {total})\nAnswer: **{matched}**",
                view=PlayAgainView(message.channel.id)  # add button here after win
            )
            guess_mgr.end_game(message.channel.id)
        else:
            try:
                await message.add_reaction("❌")
            except Exception:
                pass

    await bot.process_commands(message)

@bot.command()
async def restart(ctx):
    try:
        await ctx.send("Restarting...")
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        error_msg = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        await ctx.send(f"Restart Failed!: \n```{error_msg[:1900]}```")

if not TOKEN:
    print("ERROR: BOT_TOKEN not set. Export it in your shell with: export BOT_TOKEN='...'(mac/linux) or $env:BOT_TOKEN='...' (PowerShell)")
else:
   bot.run(TOKEN)



