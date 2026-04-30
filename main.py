import discord
from discord import app_commands
from discord.ext import commands
import os
import smtplib
from email.message import EmailMessage

# 1. BOT SETUP
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Bot is online: {self.user}")

bot = MyBot()

# 2. THE MODAL (The popup where you enter info)
class AmazonModal(discord.ui.Modal, title='Amazon Receipt Generator'):
    email_input = discord.ui.TextInput(label='Customer Email', placeholder='user@gmail.com')
    product_input = discord.ui.TextInput(label='Product Name', placeholder='Airpods Max - Midnight')
    price_input = discord.ui.TextInput(label='Price', placeholder='548.00')
    order_input = discord.ui.TextInput(label='Order Number', placeholder='202-4969648-4397107')

    async def on_submit(self, interaction: discord.Interaction):
        html_content = f"""
        <html>
        <body style="margin:0; padding:0; background-color:#000; font-family:Arial,sans-serif;">
            <center>
                <div style="background-color:#232f3e; color:#fff; padding:20px; border-radius:15px; max-width:380px; text-align:left; margin-top:20px;">
                    <table width="100%">
                        <tr>
                            <td>
                                <p style="margin:0; font-size:14px; color:#ccc;">1 item from Amazon.co.uk</p>
                                <h2 style="margin:10px 0; font-size:24px;">Your package was delivered!</h2>
                            </td>
                            <td width="60">
                                <img src="https://m.media-amazon.com/images/I/61f9N057X7L._AC_SL1500_.jpg" width="50" style="border-radius:5px; background:#fff;">
                            </td>
                        </tr>
                    </table>
                    <p style="font-weight:bold; margin-bottom:5px;">Delivered today</p>
                    <p style="font-size:13px; color:#aaa; margin-top:0;">Your package was left near the front door or porch.</p>
                    <p style="margin-bottom:2px;"><strong>Max — COVENTRY</strong></p>
                    <p style="font-size:12px; color:#aaa; margin-top:0;">Order # {self.order_input.value}</p>
                    <div style="background-color:#febd69; color:#000; padding:10px; border-radius:20px; text-align:center; font-weight:bold; margin-top:15px; width:120px; font-size:13px;">
                        Track package
                    </div>
                </div>
                <p style="color:#aaa; font-size:12px; margin-top:20px;">amazon.co.uk</p>
            </center>
        </body>
        </html>
        """

        try:
            msg = EmailMessage()
            msg['Subject'] = f"Delivered: {self.product_input.value}"
            msg['From'] = os.environ['GMAIL_USER']
            msg['To'] = self.email_input.value
            msg.set_content("Your order has been delivered.")
            msg.add_alternative(html_content, subtype='html')

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(os.environ['GMAIL_USER'], os.environ['GMAIL_PASSWORD'])
                smtp.send_message(msg)

            await interaction.response.send_message(f"✅ Sent to {self.email_input.value}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

# 3. THE COMMAND
@bot.tree.command(name="gen", description="Generate a receipt")
async def gen(interaction: discord.Interaction):
    await interaction.response.send_modal(AmazonModal())

bot.run(os.environ['DISCORD_TOKEN'])
