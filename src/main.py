import asyncio
import discord
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv
from discord import app_commands
from keep_alive import keep_alive

# ================================
# Environment Setup & Startup
# ================================
load_dotenv()
keep_alive()

# ================================
# HaroonBot Class Definition
# ================================
class HaroonBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = app_commands.CommandTree(self)

        # AWS DynamoDB setup
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name="us-east-2",
            aws_access_key_id=os.getenv('aws_access_key_id'),
            aws_secret_access_key=os.getenv('aws_secret_access_key')
        )
        self.table = self.dynamodb.Table(os.getenv('table_name'))

        # Voice channel for mute/unmute
        self.voice_channel_id = 831302754772451376

    # ==========================
    # Date Utility Function
    # ==========================
    def get_today_date(self):
        timezone = pytz.timezone("US/Central")
        now = datetime.now(timezone)
        if now.hour < 18:
            today = now - timedelta(days=1)
        else:
            today = now
        return today.strftime('%m%d%Y')

    # ==========================
    # Bot Event Handlers
    # ==========================
    async def on_ready(self):
        await self.tree.sync()
        print(f'Logged on as {self.user}')

    async def setup_hook(self):

        # ==========================
        # /geo Command
        # ==========================
        @self.tree.command(name="geo", description="Submit a GeoGuessr score")
        @app_commands.describe(score="Your GeoGuessr score (0-15000)")
        async def geo(interaction: discord.Interaction, score: int):
            user_id = str(interaction.user.id)
            today_date = self.get_today_date()

            if score > 15000 or score < 0:
                await interaction.response.send_message("Invalid score range")
                return

            response = self.table.query(
                KeyConditionExpression=Key('user_id').eq(user_id) & Key('date').eq(today_date)
            )

            if response['Items']:
                await interaction.response.send_message(
                    f"You already submitted a score for today's challenge ({response['Items'][0]['score']}). If it's wrong, ask Haroon to fix it."
                )
            else:
                self.table.put_item(
                    Item={
                        'user_id': user_id,
                        'date': today_date,
                        'score': score
                    }
                )
                await interaction.response.send_message(f"Your score today was recorded: {score}")

        # ==========================
        # /db Command
        # ==========================
        @self.tree.command(name="db", description="View your score history")
        async def db(interaction: discord.Interaction):
            user_id = str(interaction.user.id)
            try:
                response = self.table.query(KeyConditionExpression=Key('user_id').eq(user_id))
                items = response.get('Items', [])
                if items:
                    formatted_items = [f"{item['date']} - {item['score']}" for item in items]
                    await interaction.response.send_message("\n".join(formatted_items))
                else:
                    await interaction.response.send_message("No scores found.")
            except Exception as e:
                await interaction.response.send_message(f"Error fetching data: {str(e)}")

        # ==========================
        # /daily Command
        # ==========================
        @self.tree.command(name="daily", description="View the daily leaderboard")
        async def daily(interaction: discord.Interaction):
            today_date = self.get_today_date()
            try:
                response = self.table.scan()
                all_items = response.get('Items', [])
                items = [item for item in all_items if item['date'] == today_date]
                leaderboard = []
                if items:
                    sorted_items = sorted(items, key=lambda x: x['score'], reverse=True)
                    for place, item in enumerate(sorted_items, start=1):
                        user_id = item['user_id']
                        score = item['score']
                        member = interaction.guild.get_member(int(user_id))
                        member_name = member.nick if member and member.nick else (member.name if member else "Unknown")
                        leaderboard.append(f"{place}. {member_name}: {score}")
                    await interaction.response.send_message("\n".join(leaderboard))
                else:
                    await interaction.response.send_message(f"No scores for today ({today_date}) yet")
            except Exception as e:
                await interaction.response.send_message(f"Error fetching leaderboard: {str(e)}")

        # ==========================
        # /m Command
        # ==========================
        @self.tree.command(name="m", description="Mute all users in your voice channel")
        async def mute(interaction: discord.Interaction):
            try:
                voice_state = interaction.user.voice
                if voice_state and voice_state.channel:
                    voice_channel = voice_state.channel
                    await asyncio.gather(*[member.edit(mute=True) for member in voice_channel.members])
                    await interaction.response.send_message(f"All members in '{voice_channel.name}' have been muted.")
                else:
                    await interaction.response.send_message("You must be in a voice channel to use this command.")
            except Exception as e:
                await interaction.response.send_message(f"Error muting members: {str(e)}")

        # ==========================
        # /u Command
        # ==========================
        @self.tree.command(name="u", description="Unmute all users in your voice channel")
        async def unmute(interaction: discord.Interaction):
            try:
                voice_state = interaction.user.voice
                if voice_state and voice_state.channel:
                    voice_channel = voice_state.channel
                    await asyncio.gather(*[member.edit(mute=False) for member in voice_channel.members])
                    await interaction.response.send_message(f"All members in '{voice_channel.name}' have been unmuted.")
                else:
                    await interaction.response.send_message("You must be in a voice channel to use this command.")
            except Exception as e:
                await interaction.response.send_message(f"Error unmuting members: {str(e)}")

# ==========================
# Run the Bot
# ==========================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = HaroonBot(intents=intents)
client.run(os.getenv('discord_api_key'))