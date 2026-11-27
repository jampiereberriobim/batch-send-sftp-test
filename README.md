# S3 to SFTP integration

Transfers files from an Amazon S3 prefix to a remote SFTP directory using a hexagonal architecture. The container is designed to run as an AWS Batch job.

## DynamoDB configuration

### Integration table

Configured through `INTEGRATION_TABLE`.

- Partition key: `integration` (String)
- Required attributes: `secret_name` (String), `enabled` (Boolean)
- Optional attribute: `description` (String)
- `secret_name` accepts either the Secrets Manager secret name or its full ARN.

### Dataset table

Configured through `DATASET_TABLE`.

- Partition key: `integration` (String)
- Sort key: `dataset` (String)

Example dataset item in DynamoDB JSON attribute format:

```json
{
  "integration": {"S": "compartamos_sftp"},
  "dataset": {"S": "transaction"},
  "source_bucket": {"S": "qa-datalake-golden-reporte-final-zone-992382450203"},
  "source_prefix": {"S": "FCOMPARTAMOS/"},
  "source_date_template": {"S": "{YYYY-MM-DD}"},
  "source_suffix": {"S": "/TRANSACTION/"},
  "remote_path": {"S": "/entrada/processed/"},
  "destination_date_template": {"S": "{YYYY-MM-DD}"},
  "date_offset": {"N": "1"},
  "enabled": {"BOOL": true},
  "recursive": {"BOOL": false}
}
```

### Source and destination paths

The S3 source prefix is composed as `source_prefix + source_date_template + source_suffix`.
The SFTP destination is composed as `remote_path + destination_date_template`.

The supported date token is `{YYYY-MM-DD}`. If either template contains the date token, the execution iterates through the requested date range. When `start_date` is omitted, the batch uses the current date in Peru (`America/Lima`) minus `date_offset` days. `date_offset = 0` means today in Peru; `date_offset = 1` means yesterday in Peru; `date_offset = 2` means two days ago. If an explicit `start_date` is sent in the event, it takes precedence over the configured offset. `end_date` defaults to the resolved start date. Both templates are optional and independent.

### Recursive listing

- `recursive = false`: only files directly inside the resolved S3 prefix are transferred.
- `recursive = true`: files in the resolved prefix and all nested folders are transferred.

## Secrets Manager and SFTP authentication

The integration's `secret_name` references a Secrets Manager secret by name or full ARN. The secret must contain a JSON object with connection fields and one supported authentication method.

### SSH private-key authentication

```json
{
  "host": "sftp.example.com",
  "port": 22,
  "username": "sftp_user",
  "private_key": "-----BEGIN OPENSSH PRIVATE KEY-----\\n...\\n-----END OPENSSH PRIVATE KEY-----",
  "private_key_passphrase": ""
}
```

### Password authentication

```json
{
  "host": "sftp.example.com",
  "port": 22,
  "username": "sftp_user",
  "password": "your-password"
}
```

- If `private_key` is present and non-empty, Paramiko uses SSH private-key authentication.
- Otherwise, if `password` is present and non-empty, Paramiko uses password authentication.
- At least one authentication method is required.

## Execution metadata

Metadata Parquet files are stored in `METADATA_BUCKET` under:

```text
SFTP/{report_name}/year={YYYY}/month={M}/day={D}/{report_name}_{execution_id}_{timestamp}.parquet
```

## S3 notification

At the end of every execution, whether the SFTP transfer succeeds or fails, the batch writes one JSON notification to `NOTIFICATION_BUCKET`. The JSON includes `status` with the execution result: `OK` or `ERROR`.

Object key:

```text
NOTIFICACIONES/{PROCESS}/{PROCESS}.json
```

For the `transaction` dataset, the key is `NOTIFICACIONES/TRANSACTION/TRANSACTION.json` and the JSON body is:

```json
{
  "process_name": "TRANSACTION",
  "type": "SFTP",
  "fecha": "2026-11-22",
  "status": "OK"
}
```

The `fecha` value is always the date when the batch execution started in Peru (`America/Lima`), regardless of `date_offset`, `start_date`, or `end_date` used to select files. For failed executions, the same object key is written with `"status": "ERROR"`. The notification write is attempted even when the transfer fails; an S3 write failure is logged and does not hide the original transfer error.

## Environment variables

- `DATASET_TABLE`: DynamoDB dataset table.
- `INTEGRATION_TABLE`: DynamoDB integration table.
- `METADATA_BUCKET`: S3 bucket for execution metadata.
- `NOTIFICATION_BUCKET`: S3 bucket for process notification JSON files.

AWS credentials and region use the standard boto3 credential provider chain. For AWS Batch, attach an appropriate Job Role to the job definition; do not bake credentials into the image.

## AWS Batch execution

The container command is:

```bash
python -m src.entrypoints.batch_handler '<event-json>'
```

Example event:

```json
{
  "integration": "compartamos_sftp",
  "dataset": "TRANSACTION",
  "start_date": "2026-11-22",
  "end_date": "2026-11-22"
}
```

The dates are optional. If omitted, the application resolves the execution date using the dataset's `date_offset` and the Peru timezone.

Configure the following environment variables in the AWS Batch job definition:

- `DATASET_TABLE`
- `INTEGRATION_TABLE`
- `METADATA_BUCKET`
- `NOTIFICATION_BUCKET`

Pass the event JSON as the container command override. The process exits with code `0` when the use case completes successfully. An unhandled execution error causes a non-zero exit code so AWS Batch marks the job as failed.

## Build and run locally

Build the image:

```bash
docker build -t analyticssftp-send-batch:latest .
```

Run a job locally (the machine must have AWS credentials and network access to the required AWS services and SFTP host):

```bash
docker run --rm \
  -e DATASET_TABLE="sftp_delivery_dataset" \
  -e INTEGRATION_TABLE="sftp_delivery_integration" \
  -e METADATA_BUCKET="qa-datalake-metadata-zone-992382450203" \
  -e NOTIFICATION_BUCKET="qa-datalake-silver-zone-temp-992382450203" \
  analyticssftp-send-batch:latest \
  '{"integration":"compartamos_sftp","dataset":"TRANSACTION","start_date":"2026-11-22","end_date":"2026-11-22"}'
```
