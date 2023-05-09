docker compose up -d

# ask the user if we want to start the local api
start_local_api='n'

echo "\n\tYou must have the connection string for postgres, you can get it replacing the values in the file: sam_local_envs_parameters.json\n"
read -p "Do you want to start the local api? (y/n) " start_local_api

if [ "$start_local_api" = 'y' ] ; then
  # Start local api
  echo "\nStarting local api...\n"
  sh start_local_api.sh
else
  echo "\n\tYou can start the local api later with the command: sh start_local_api.sh\n"
fi

# ask the user if we want to deploy the api
deploy_api='n'

read -p "Do you want to deploy the api? (y/n) " deploy_api

if [ "$deploy_api" = 'y' ] ; then
  # Deploy api
  aws_profile=""
  echo "\nDeploying api...\n"
  read -p "Enter the aws profile: " aws_profile
  sh deploy.sh $aws_profile
else
  echo "\n\tYou can deploy the api later with the command: sh deploy.sh <aws_profile>\n"
fi