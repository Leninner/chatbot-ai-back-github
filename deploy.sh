#!/bin/bash
profile=$1 || "default"
docker compose build
sam build -uc -bi chatbot-ai-back-github-app-node -bi ChatHandlerFunction=chatbot-ai-back-github-app-python 
sam deploy --config-env dev --profile $profile --no-confirm-changeset --no-fail-on-empty-changeset