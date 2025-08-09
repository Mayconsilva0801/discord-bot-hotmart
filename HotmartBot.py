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
    def __init__(self, canal_para_apagar=None):
        super().__init__(timeout=None)
        self.canal_para_apagar = canal_para_apagar

    @discord.ui.button(label="Verificar Email", style=discord.ButtonStyle.primary)
    async def verificar(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = EmailModal(self.canal_para_apagar)
        await interaction.response.send_modal(modal)

class EmailModal(discord.ui.Modal, title="Verificação de Email"):
    def __init__(self, canal_para_apagar=None):
        super().__init__()
        self.canal_para_apagar = canal_para_apagar

    email = discord.ui.TextInput(
        label="Digite seu email Hotmart: ",
        placeholder="exemplo@email.com"
    )

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
        if self.canal_para_apagar:
            try:
                await self.canal_para_apagar.delete(reason="Verificação concluída")
            except Exception as e:
                print(f"Erro ao deletar canal: {e}")

@bot.command()
async def verificar(ctx):
    if ctx.channel.id != CANAL_PERMITIDO_ID:
        await ctx.send("Este comando só pode ser usado no canal específico.")
        return
    view = VerificarButton()
    await ctx.send("Clique no botão abaixo para verificar seu email:", view=view)

@bot.event
async def on_member_join(member):
    guild = member.guild

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(view_channel=True)
    }

    canal = await guild.create_text_channel(
        name=f"verificação-{member.name}",
        overwrites=overwrites,
        reason="Canal privado para verificação de email"
    )

    view = VerificarButton(canal)
    await canal.send(
        f"👋 Olá {member.mention}, bem-vindo ao servidor da Formação ADC de Elite!\nClique abaixo para verificar seu email.",
        view=view
    )

@bot.event
async def on_ready():
    print(f"Bot iniciado como {bot.user}")

bot.run(TOKEN)
