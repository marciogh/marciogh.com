set -o pipefail
set -e
DOCKER_IMAGE="marciogh-openai:latest"
docker buildx build --platform linux/amd64 --provenance=false -t $DOCKER_IMAGE .
#docker run --platform linux/amd64 -p 9000:8080 -v $HOME/.aws/credentials:/root/.aws/credentials:ro $DOCKER_IMAGE
#curl http://localhost:9000/2015-03-31/functions/function/invocations -d '{"queryStringParameters":{"q":"hello world"}}'