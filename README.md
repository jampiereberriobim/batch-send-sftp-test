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
  "dataset": {"S": "user_balances"},
  "source_bucket": {"S": "qa-datalake-golden-reporte-final-zone-992382450203"},
  "source_prefix": {"S": "FCOMPARTAMOS/"},
  "source_date_template": {"S": "{YYYY-MM-DD}"},
  "source_suffix": {"S": "/USER-BALANCES/"},
  "remote_path": {"S": "/entrada/processed/"},
  "destination_date_template": {"S": "{YYYY-MM-DD}"},
  "enabled": {"BOOL": true},
  "recursive": {"BOOL": false}
}
```

### Source path

The S3 source prefix is composed in this order:

`source_prefix + source_date_template + source_suffix`

For example, with `source_prefix = FCOMPARTAMOS/`, `source_date_template = {YYYY-MM-DD}`, and `source_suffix = /USER-BALANCES/`, the resolved S3 prefix for November 22, 2026 is:

`FCOMPARTAMOS/2026-11-22/USER-BALANCES/`

### SFTP destination path

The SFTP destination is composed independently:

`remote_path + destination_date_template`

For example, with `remote_path = /entrada/processed/` and `destination_date_template = {YYYY-MM-DD}`, the resolved destination for November 22, 2026 is:

`/entrada/processed/2026-11-22/`

Both date templates are optional and independent:

- If `source_date_template` is omitted or empty, no date partition is added to the S3 source path.
- If `destination_date_template` is omitted or empty, files are uploaded directly into `remote_path`.
- The supported date token is `{YYYY-MM-DD}`.
- If either template contains the date token, the execution iterates through the requested date range. If only the destination template is date-partitioned, the same configured S3 source prefix is read for each requested date and uploaded to each corresponding destination partition.

When `start_date` and `end_date` are omitted, the current date is used if date partitioning is configured. For a date range, provide both dates in ISO format (`YYYY-MM-DD`).

### Recursive listing

- `recursive = false`: only files directly inside the resolved S3 prefix are transferred.
- `recursive = true`: files in the resolved prefix and all nested folders are transferred.

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

The SFTP destination directory is created if it does not exist.

## Execution event

```json
{
  "integration": "compartamos_sftp",
  "dataset": "user_balances",
  "start_date": "2026-11-22",
  "end_date": "2026-11-24"
}
```
