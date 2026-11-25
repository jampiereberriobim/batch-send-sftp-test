# S3 to SFTP integration

Transfers files from an Amazon S3 prefix to a remote SFTP directory using a hexagonal architecture.

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

`date_offset` is an optional numeric attribute in the DynamoDB dataset item. It defaults to `0` when omitted.

AWS credentials and region use the standard boto3 credential provider chain.

## Local execution

Set the required environment variables and optional `INTEGRATION`, `DATASET`, `START_DATE`, and `END_DATE` variables, then run:

```bash
python test_local.py
```

## Execution event

```json
{
  "integration": "compartamos_sftp",
  "dataset": "transaction",
  "start_date": "2026-11-22",
  "end_date": "2026-11-24"
}
```
