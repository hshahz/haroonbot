import discord
import boto3
from env.env import discord_api_key, table_name





class HaroonBot(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Init DynamoDB
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.content.contains("!geo"):
            try: #scrape for <score>
                score = int(message.content.split("!geo")[1].strip())
                await message.channel.send(f"Your score today was {score}")
            except(IndexError, ValueError): #if no score then say hey ur score is not a valid format
                await message.channel.send("Invalid format. Use `!geo <score> with a numerical only score")
                return

        #DETECT SOME SOR OF INPUT LIKE !geo <your_score>
        # message.author.userid
        # user1, user2, user3, user4, etc.
        # day 1, 10k, 15k , 14k,
        # day 2, 12k , 123 k, 124
        # day3, 14, 56k, 12
        # user2, user3, user1

intents = discord.Intents.default()
intents.message_content = True

client = HaroonBot(intents=intents)
client.run(discord_api_key)

