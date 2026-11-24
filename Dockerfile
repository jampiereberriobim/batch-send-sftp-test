FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt .

RUN pip install \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt \
    --target "${LAMBDA_TASK_ROOT}"

COPY src/ ${LAMBDA_TASK_ROOT}/src/

ENV DATASET_TABLE=""
ENV INTEGRATION_TABLE=""
ENV METADATA_BUCKET=""
ENV METADATA_PREFIX=""

CMD ["src.entrypoints.lambda_handler.lambda_handler"]
