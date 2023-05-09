#!/bin/bash

sam build -uc -bi chatbot-ai-back-app-node -bi ChatHandlerFunction=chatbot-ai-back-app-python 

echo '\nPlease make sure you have the correct envs in the sam_local_envs_parameters.json file\n'
echo '\n\tIf you want to run a local postgres instance, please run the following command:\n'
echo '\n\tdocker compose up -d\n'
echo '\nMake sure you have the correct connection string in the envs file\n'
echo '\n\tpostgresql://user:password@host:5432/database-name\n'

sam local start-api --env-vars sam_local_envs_parameters.json -p 3002