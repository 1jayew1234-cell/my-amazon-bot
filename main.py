import discord
from discord import app_commands
from discord.ext import commands
import os
import smtplib
from email.message import EmailMessage

# 1. Setup Bot Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

# 2. Define the Pop-up Form (Modal)
class ReceiptModal(discord.ui.Modal, title='Amazon Receipt Generator'):
    customer_email = discord.ui.TextInput(label='Customer Email', placeholder='user@gmail.com')
    product_name = discord.ui.TextInput(label='Product Name', placeholder='Airpods Max')
    price = discord.ui.TextInput(label='Price', placeholder='548.00')
    order_num = discord.ui.TextInput(label='Order Number', placeholder='202-4969648-4397107')

    async def on_submit(self, interaction: discord.Interaction):
        # Tells Discord the bot is working so it doesn't time out
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Pulls your secrets from Railway Variables
            gmail_user = os.environ.get('GMAIL_USER')
            gmail_pass = os.environ.get('GMAIL_PASSWORD')

            # Create the Email Content
            msg = EmailMessage()
            msg.set_content(f"Order Confirmation\n\nOrder Number: {self.order_num.value}\nProduct: {self.product_name.value}\nPrice: ${self.price.value}")
            msg['Subject'] = f"Your Amazon.com order of {self.product_name.value}"
            msg['From'] = gmail_user
            msg['To'] = self.customer_email.value

            # Connect to Gmail and Send
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(gmail_user, gmail_pass)
                smtp.send_message(msg)

            # The success message you requested
            await interaction.followup.send(f"✅ Check your Gmail, a receipt was sent to **{self.customer_email.value}**!", ephemeral=True)
            
        except Exception as e:
            # If Gmail login fails or email is wrong, it tells you why
            await interaction.followup.send(f"❌ Error sending email: {str(e)}", ephemeral=True)

# 3. Define the Panel (The Button)
class ReceiptPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Generate Receipt", style=discord.ButtonStyle.green, custom_id="gen_btn")
    async def generate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ReceiptModal())

# 4. The /gen Command
@bot.tree.command(name="gen", description="Show the receipt generation panel")
async def gen(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Amazon Receipt Generator",
        description="Click the button below to start generating your receipt.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, view=ReceiptPanelView())

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} is online and commands are synced!")

bot.run(os.environ.get('DISCORD_TOKEN'))
