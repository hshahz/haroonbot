import discord
import boto3
from env.env import get_discord_api_key, get_table_name





class HaroonBot(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Init DynamoDB
        self.dynamodb = boto3.resource('dynamodb', region_name="us-east-2")
        self.table = self.dynamodb.Table(get_table_name())

    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        if message.author == self.user: #prevent loop
            return

        print(f'Message from {message.author}: {message.content}')
        if "!geo" in message.content: #DETECT SOME SOR OF INPUT LIKE !geo <your_score>
            try: #scrape for <score>
                score = int(message.content.split("!geo")[1].strip())
                await message.channel.send(f"Your score today was {score}")
            except(IndexError, ValueError): #if no score then say hey ur score is not a valid format
                await message.channel.send("Invalid format. Use `!geo <score> with a numerical only score")
                return


        #leaderboard format:
        # message.author.userid
        # user1, user2, user3, user4, etc.
        # day 1, 10k, 15k , 14k,
        # day 2, 12k , 123 k, 124
        # day3, 14, 56k, 12
        # user2, user3, user1

intents = discord.Intents.default()
intents.message_content = True

client = HaroonBot(intents=intents)
client.run(get_discord_api_key())

