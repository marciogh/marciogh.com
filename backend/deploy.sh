set -o pipefail
set -e

AWS_ACCOUNT_ID='639886339024'
AWS_REGION='ap-southeast-2'
REPOSITORY_NAME='marciogh'
DOCKER_IMAGE="marciogh-openai:latest"

aws ecr get-login-password \
  --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

REPOSITORY_URI=`
aws ecr describe-repositories \
  --repository-names $REPOSITORY_NAME --region $AWS_REGION | jq -r '.repositories[0].repositoryUri'
`
if [ $REPOSITORY_URI == "" ]; then
  aws ecr create-repository \
    --repository-name $REPOSITORY_NAME --region $AWS_REGION --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
fi

TAG=$REPOSITORY_URI:latest
docker tag $DOCKER_IMAGE $TAG
docker push $TAG