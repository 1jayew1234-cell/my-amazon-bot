import discord
from discord import app_commands
from discord.ext import commands
import os
import smtplib
from email.message import EmailMessage

# 1. Setup Bot Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_id=".", intents=intents)

# 2. Define the Receipt Pop-up Form
class ReceiptModal(discord.ui.Modal, title='Amazon Receipt Generator'):
    customer_email = discord.ui.TextInput(label='Customer Email', placeholder='user@gmail.com')
    product_name = discord.ui.TextInput(label='Product Name', placeholder='Airpods Max')
    price = discord.ui.TextInput(label='Price', placeholder='548.00')

    async def on_submit(self, interaction: discord.Interaction):
        # This tells Discord to "Wait" so it doesn't error out
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get variables from Railway
            gmail_user = os.environ.get('GMAIL_USER')
            gmail_pass = os.environ.get('GMAIL_PASSWORD')

            # Create the Email
            msg = EmailMessage()
            msg.set_content(f"Order Confirmation\n\nProduct: {self.product_name.value}\nPrice: ${self.price.value}")
            msg['Subject'] = f"Your Amazon.com order of {self.product_name.value}"
            msg['From'] = gmail_user
            msg['To'] = self.customer_email.value

            # Send the Email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(gmail_user, gmail_pass)
                smtp.send_message(msg)

            await interaction.followup.send(f"✅ Receipt sent to {self.customer_email.value}!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

# 3. The /gen Command
@bot.tree.command(name="gen", description="Open the receipt generator")
async def gen(interaction: discord.Interaction):
    # This opens the pop-up form immediately
    await interaction.response.send_modal(ReceiptModal())

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} is online and commands are synced!")

# 4. Start the Bot
bot.run(os.environ.get('DISCORD_TOKEN'))
