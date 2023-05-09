#!/bin/bash
profile=$1

docker compose build
sam build -uc -bi chatbot-ai-back-github-app-node -bi ChatHandlerFunction=chatbot-ai-back-github-app-python 

if [ -z "$profile" ]; then
  sam deploy --config-env dev --profile $profile --no-confirm-changeset --no-fail-on-empty-changeset
else
  sam deploy --config-env dev --no-confirm-changeset --no-fail-on-empty-changeset
fi
