import asyncio
import discord
import boto3
from boto3.dynamodb.conditions import Key, Attr
from env.env import get_discord_api_key, get_table_name
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz

class HaroonBot(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Init DynamoDB
        self.dynamodb = boto3.resource('dynamodb', region_name="us-east-2")
        self.table = self.dynamodb.Table(get_table_name())

    def get_today_date(self):
        timezone = pytz.timezone("US/Central")
        now = datetime.now(timezone)
        if now.hour < 18: #not 6pm yet, its yesterday's daily challenge
            today = now - timedelta(days=1)
        else:
            today = now
        return today.strftime('%m%d%Y')

    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):

        if message.author == self.user: #prevent loop
            return



        # print(f'Message from {message.author}: {message.content}')
        if "!geo" in message.content: #DETECT SOME SOR OF INPUT LIKE !geo <your_score>
            try: #scrape for <score>
                score = int(message.content.split("!geo")[1].strip())
                user_id = str(message.author.id)
                today_date = self.get_today_date()

                if score > 15000 or score < 0:
                    await message.channel.send("Invalid score range")
                    return

                #check if score already in db
                response = self.table.query(
                    KeyConditionExpression = boto3.dynamodb.conditions.Key('user_id').eq(user_id) & boto3.dynamodb.conditions.Key('date').eq(today_date)
                )

                if response['Items']:
                    await message.channel.send(f"You already submitted a score for today's challenge ({response['Items'][0]['score']}). If it's wrong, ask haroon to fix it")
                else:
                    self.table.put_item(
                        Item={
                            'user_id': user_id,
                            'date': today_date,
                            'score': score
                        }
                    )

                    await message.channel.send(f"Your score today was recorded: {score}")

            except(IndexError, ValueError): #if no score then say hey ur score is not a valid format
                await message.channel.send("Invalid format. Use `!geo <score>` with a numerical only score")
                return



        if message.content.startswith("!db"):
            user_id = str(message.author.id)
            try: #get something from the database
                response = self.table.query(
                    KeyConditionExpression = boto3.dynamodb.conditions.Key('user_id').eq(user_id)
                )
                items = response.get('Items', [])
                if items:
                    formatted_items = [f"Date: {item['date']} - Score: {item['score']}" for item in items]
                    await message.channel.send("\n".join(formatted_items))
                else:
                    await message.channel.send("no items")
            except Exception as e:
                await message.channel.send(f"Error fetching data for {user_id}: {str(e)}")



        if message.content == "!daily": #daily leaderboard
            today_date = self.get_today_date()

            try:
                # get dynamodb all entries that are today
                response = self.table.scan()

                all_items = response.get('Items', [])
                items = [item for item in all_items if item['date'] == today_date]
                leaderboard = []

                if items:
                    sorted_items = sorted(items, key=lambda x: x['score'], reverse=True)
                    place = 1
                    for item in sorted_items:
                        user_id = item['user_id']
                        score = item['score']

                        member = message.guild.get_member(int(user_id))
                        if member is not None: #check to see if member is in server
                            member_name = member.nick if member and member.nick else member.name
                            leaderboard.append(f"{place}. {member_name}: {score}")
                            place += 1

                    await message.channel.send("\n".join(leaderboard))
                else:
                    await message.channel.send(f"No scores for today ({today_date}) yet")

            except Exception as e:
                await message.channel.send(f"Error fetching leaderboard: {str(e)}")

        #leaderboard format:
        # message.author.userid
        # user1, user2, user3, user4, etc.
        # day 1, 10k, 15k , 14k,
        # day 2, 12k , 123 k, 124
        # day3, 14, 56k, 12
        # user2, user3, user1
        voice_channel_id =831302754772451376

        if message.content == "!m":
            try:
                # Hardcoded voice channel ID or name
                   # Replace with your voice channel ID
                voice_channel = message.guild.get_channel(voice_channel_id)

                if voice_channel and isinstance(voice_channel, discord.VoiceChannel):
                    # Use asyncio.gather to run mute operations concurrently
                    await asyncio.gather(*[
                        member.edit(mute=True)
                        for member in voice_channel.members
                    ])
                    await message.channel.send(f"All members in the voice channel '{voice_channel.name}' have been muted.")
                else:
                    await message.channel.send("Hardcoded voice channel not found.")
            except Exception as e:
                await message.channel.send(f"Error muting members: {str(e)}")

        if message.content == "!u":
            try:
                # Hardcoded voice channel ID or name
                
                voice_channel = message.guild.get_channel(voice_channel_id)

                if voice_channel and isinstance(voice_channel, discord.VoiceChannel):
                    # Use asyncio.gather to run unmute operations concurrently
                    await asyncio.gather(*[
                        member.edit(mute=False)
                        for member in voice_channel.members
                    ])
                    await message.channel.send(f"All members in the voice channel '{voice_channel.name}' have been unmuted.")
                else:
                    await message.channel.send("Hardcoded voice channel not found.")
            except Exception as e:
                await message.channel.send(f"Error unmuting members: {str(e)}")
                
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = HaroonBot(intents=intents)
client.run(get_discord_api_key())

