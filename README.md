

Get-ChildItem -Path . -Directory -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force



aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 992382450203.dkr.ecr.us-east-1.amazonaws.com
docker build -t analytics/athena-service-lambda-test:qa .
docker tag analytics/athena-service-lambda-test:qa 992382450203.dkr.ecr.us-east-1.amazonaws.com/analytics/athena-service-lambda-test:qa
docker push 992382450203.dkr.ecr.us-east-1.amazonaws.com/analytics/athena-service-lambda-test:qa


aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 654654503580.dkr.ecr.us-east-1.amazonaws.com
docker build -t analytics/sftp-ingest-batch:qa .
docker tag analytics/sftp-ingest-batch:qa 654654503580.dkr.ecr.us-east-1.amazonaws.com/analytics/sftp-ingest-batch:qa
docker push 654654503580.dkr.ecr.us-east-1.amazonaws.com/analytics/sftp-ingest-batch:qa


ENV DATASET_TABLE="sftp-dataset"
ENV INTEGRATION_TABLE="sftp-integration"
ENV BRONZE_BUCKET="uat-temp-992382450203"
ENV METADATA_BUCKET="uat-temp-992382450203"
ENV METADATA_PREFIX="BRONZE"