async def on_submit(self, interaction: discord.Interaction):
        # 1. This tells Discord "I'm working" and keeps it private
        await interaction.response.defer(ephemeral=True) 
        
        try:
            gmail_user = os.environ.get('GMAIL_USER')
            gmail_pass = os.environ.get('GMAIL_PASSWORD')

            msg = EmailMessage()
            # You can customize the body of the email here
            msg.set_content(f"Order Confirmation\n\nOrder Number: {self.order_num.value}\nProduct: {self.product_name.value}\nPrice: ${self.price.value}")
            msg['Subject'] = f"Your Amazon.com order of {self.product_name.value}"
            msg['From'] = gmail_user
            msg['To'] = self.customer_email.value

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(gmail_user, gmail_pass)
                smtp.send_message(msg)

            # 2. This sends the PRIVATE follow-up message only you can see
            await interaction.followup.send(content=f"✅ Check your Gmail, a receipt was sent to **{self.customer_email.value}**!", ephemeral=True)
            
        except Exception as e:
            # If it fails, it will tell you why (e.g., "Username and Password not accepted")
            await interaction.followup.send(content=f"❌ Error: {str(e)}", ephemeral=True)
