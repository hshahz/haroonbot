# haroonbot
discord bot that runs the haroon bot account

# HOW TO RUN
- Pull repo locally

## specify discord api key
- create ".env" dir locally in root folder haroonbot
- inside of .env, create file named env.py
- in env.py, label variable "api_key" for connecting to discord api and "table_name" from dynamoDB
- put keys in env file
- make getter functions inside the env.py so that your main.py can call them (very jank,sry)

## specify aws key
- in C:/Users/<you>/.aws/credentials, add aws access key and private key
- in C:/Users/<you>/.aws/config, set region to us-east-2

## run the bot
- cd into src cuz why not
- make sure you install requirements in requirements.txt
- run python3 main.py
- should be online