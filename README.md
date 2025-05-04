# haroonbot
discord bot that runs the haroon bot account

# HOW TO RUN
- Pull repo locally

## specify discord api key
- create .env in the /src dir
- in .env fill "api_key" for connecting to discord api and "table_name" from dynamoDB

## specify aws key
- in `C:/Users/<you>/.aws/credentials`, add aws access key and private key
- in `C:/Users/<you>/.aws/config`, set region to us-east-2 (or whatever ur aws region is)

## run the bot
- cd into src cuz why not
- make sure you install requirements in requirements.txt
- run python3 main.py
- should be online
- use commands outlined in main.py on_message()