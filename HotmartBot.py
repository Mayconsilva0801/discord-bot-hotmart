import discord
from discord.ext import commands
import aiohttp
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CANAL_PERMITIDO_ID = os.getenv("CANAL_ID")
MAKE_WEBHOOK_URL = os.getenv("WEBHOOOK_URL")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

class VerificarButton(discord.ui.View):
    @discord.ui.button(label="Verificar Email", style=discord.ButtonStyle.primary)
    async def verificar(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = EmailModal()
        await interaction.response.send_modal(modal)

class EmailModal(discord.ui.Modal, title="Verificação de Email"):
    email = discord.ui.TextInput(label="Digite seu email(O mesmo utilizado na conta da Hotmart):", placeholder="exemplo@email.com")

    async def on_submit(self, interaction: discord.Interaction):
        payload = {
            "usuario": interaction.user.name,
            "id": str(interaction.user.id),
            "email": self.email.value
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(MAKE_WEBHOOK_URL, json=payload) as response:
                if response.status == 200:
                    mensagem = await response.text()
                else:
                    mensagem = f"Erro {response.status}: falha ao enviar os dados."

        await interaction.response.send_message(mensagem, ephemeral=True)

@bot.command()
async def verificar(ctx):
    if ctx.channel.id != CANAL_PERMITIDO_ID:
        await ctx.send("Este comando só pode ser usado no canal específico.")
        return
    view = VerificarButton()
    await ctx.send("Clique no botão abaixo para verificar seu email:", view=view)

@bot.event
async def on_member_join(member):
    canal = member.guild.get_channel(CANAL_PERMITIDO_ID)
    if canal:
        view = VerificarButton()
        await canal.send(
            f"👋 Olá {member.mention}, bem-vindo ao servidor!\nClique no botão abaixo para verificar seu email:",
            view=view
        )

bot.run(TOKEN)
