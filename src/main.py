import discord
from env import api_key, aws_key

class HaroonBot(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.content.contains("!geo"):
        #scrape for <score>
        #if no score then say hey ur score is not a valid format

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
client.run(api_key)