

run command
python3 bot.py 

run in docker 
docker run \                            
  --env-file .env_local \
  -v $(pwd)/credentials.json:/app/credentials.json \
  -v $(pwd)/token.json:/app/token.json \
  decisionforge

build in docker 
docker build -t decisionforge .