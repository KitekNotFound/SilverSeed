import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CATEGORY_ID = int(os.getenv("CATEGORY_ID"))
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Zamykanie ticketa...", ephemeral=True)
        await interaction.channel.delete(reason="Ticket zamknięty przez użytkownika")

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"🔁 Zsynchronizowano {len(synced)} komend slash.")
    except Exception as e:
        print(e)

@bot.tree.command(name="ticket", description="Utwórz zgłoszenie o wykonanie strony")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def ticket(interaction: discord.Interaction):
    guild = interaction.guild
    category = guild.get_channel(CATEGORY_ID)
    admin_role = guild.get_role(ADMIN_ROLE_ID)

    # sprawdzamy, czy użytkownik już ma ticket
    for ch in category.channels:
        if ch.name == f"ticket-{interaction.user.name}".lower():
            await interaction.response.send_message("❗ Masz już otwarty ticket!", ephemeral=True)
            return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        admin_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    channel = await guild.create_text_channel(
        name=f"ticket-{interaction.user.name}",
        category=category,
        overwrites=overwrites,
        topic=f"Ticket użytkownika {interaction.user.name}"
    )

    await interaction.response.send_message(f"🎟️ Ticket utworzony: {channel.mention}", ephemeral=True)

    embed = discord.Embed(
        title="Nowe zgłoszenie 💬",
        description=f"Cześć {interaction.user.mention}! Opisz dokładnie, jaką stronę chcesz, a nasz zespół się tym zajmie.",
        color=0x2ecc71
    )

    await channel.send(embed=embed, view=TicketButton())

bot.run(TOKEN)
