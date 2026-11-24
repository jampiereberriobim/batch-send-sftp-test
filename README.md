# S3 to SFTP integration

Transfers files from an Amazon S3 prefix to a remote SFTP directory using a hexagonal architecture.

## DynamoDB configuration

### Integration table

Configured through `INTEGRATION_TABLE`.

- Partition key: `integration` (String)
- Required attributes: `secret_name` (String), `enabled` (Boolean)
- Optional attribute: `description` (String)

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
  "date_template": {"S": "{date}/USER-BALANCES/"},
  "remote_path": {"S": "/entrada/processed"},
  "enabled": {"BOOL": true},
  "recursive": {"BOOL": false}
}
```

The `{date}` token is expanded as `YYYY-MM-DD`. Other supported tokens are `{yyyy}`, `{MM}`, `{dd}`, and `{yyyyMMdd}`. If the date template has no date token, its path is processed once.

When `start_date` and `end_date` are omitted, the current date is processed. For a date range, provide both dates in ISO format (`YYYY-MM-DD`).

## Secrets Manager

The integration's `secret_name` references a Secrets Manager secret. The current provider expects the secret JSON to contain the `sftp_qa_2` property with `host`, `port`, `username`, and either `password` or `private_key`.

## Environment variables

- `DATASET_TABLE`: DynamoDB dataset table.
- `INTEGRATION_TABLE`: DynamoDB integration table.
- `METADATA_BUCKET`: S3 bucket for execution metadata.
- `METADATA_PREFIX`: S3 prefix for execution metadata.

AWS credentials and region use the standard boto3 credential provider chain.

## Local execution

Install requirements, authenticate to AWS, and set the four environment variables above. Optional variables:

- `INTEGRATION` (default: `compartamos_sftp`)
- `DATASET` (default: `transaction`)
- `START_DATE` and `END_DATE` (optional ISO dates)

Run:

```bash
python test_local.py
```

The SFTP destination directory is created if it does not exist. By default, only files directly under each resolved S3 prefix are transferred. Set `recursive` to true to include nested folders.

## Execution event

```json
{
  "integration": "compartamos_sftp",
  "dataset": "transaction",
  "start_date": "2026-11-22",
  "end_date": "2026-11-24"
}
```
