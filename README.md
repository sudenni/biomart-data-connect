# BioMart with Data Connect
EMBL-EBI internship project supervised by Andy Yates (April to July 2024). This project aims to replace BioMart with a new query engine and new data files.

This repo contains a Flask application to query the new BioMart implementation with Data Connect and Trino on Parquet Data in AWS S3 buckets.
The Parquet files for BioMart were generated with the Nextflow pipeline [nf-sql-to-parquet](https://github.com/Ensembl/nf-sql-to-parquet) which convert SQL queries on Ensembl core databases to flat files in Parquet format.

## Installation
This project requires
- Python version 3.10 with packages from `requirements.txt`
- [Trino CLI](https://trino.io/docs/current/client/cli.html)
- Docker

### Build the Data Connect image
Acquire the source and build the Docker image.
```
git clone --branch elwazi https://github.com/DNAstack/data-connect-trino.git
cd data-connect-trino
git checkout  
./ci/build-docker-image data-connect-trino:elwazi data-connect-trino elwazi
```

:warning: This image uses the `elwazi` branch of [data-connect-trino](https://github.com/DNAstack/data-connect-trino). The main difference comes from [disabling indexing-service, collection-service and liquibase](https://github.com/DNAstack/data-connect-trino/compare/main...elwazi). Otherwise, Data Connect throws an error when trying to access pages.

## Running the application
### Configure AWS keys
Replace `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `docker/etc/catalog/hive.properties`, and `docker/conf/metastore-site.xml`

[Guide to create AWS access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey)

### Start Trino and Data Connect
```
cd docker
docker-compose up -d
```

The docker setup runs as is, but if adjustments are needed Trino configuration files are in `docker/etc`, Hive configuration files are in `docker/conf`.

:warning: The [hive-metastore image](https://github.com/bitsondatadev/hive-metastore) should not be used for production.

### Populate the database
Trino can take some time to launch. Check if Trino is running with:
```
trino
show catalogs;
```
Catalogs are defined in the `docker/etc/catalog` folder.

This is a small example for a partitioned translation table, the full script for BioMart tables is in `docker/create_tables.sql`

1. Create a schema for your AWS S3 bucket.
```sql
CREATE SCHEMA hive.biomart WITH (location = 's3a://your-bucket/');
SHOW SCHEMA FROM hive;
```

2. Create tables.

Column name and type should match with the Parquet file.
```sql
CREATE TABLE hive.biomart.translation (
    translation_id BIGINT,
    stable_id VARCHAR,
    "start" BIGINT,
    "end" BIGINT,
    go_terms ARRAY(VARCHAR),
    species VARCHAR
) with (external_location = 's3a://your-bucket/translation', format = 'PARQUET', partitioned_by = ARRAY['species']);
CALL hive.system.sync_partition_metadata('biomart', 'translation', 'ADD');
SELECT * FROM hive.biomart.translation limit 5;
```

Check if everything is running by going on `localhost:8089/tables` and browsing tables.

### Query with Data Connect
Modify `CATALOG` and `SCHEMA` in `app/config.py` to match the schema created with Trino. With the previous example `CATALOG = 'hive'` and `SCHEMA = 'biomart'`. `FILTERS` is a list of columns you want to generate filters on when running a query through the web interface.

```
python -m flask run --port 8000
```

Go to `localhost:8000` and construct your query by selecting the table, species and columns.

Or use API endpoints:
- `localhost:8000/api/species` is the list of species in the database
- `localhost:8000/api/tables` is the list of tables in the database
- `localhost:8000/api/tables/<TABLE>` gives the list of columns in a given table
Build a query by giving columns, filters (optional) and limit (optional) as JSON through `localhost:8000/api/query/<TABLE>`. For example:
```python
import requests

json_data = {
    'columns' : ["stable_id", "region_name", "start", "end", "strand", "biotype"],
    'filters' : {'biotype' : ['protein_coding', 'rRNA'], 'species' : ['homo_sapiens']},
    'limit' : 10
    }

requests.get('http://localhost:8000/api/query/gene',
                    json=json_data,
                    timeout=60)
```
is equivalent to:
```sql
SELECT "stable_id","region_name","start","end","strand","biotype" 
FROM "hive"."biomart"."gene" 
WHERE ("biotype"='protein_coding' OR "biotype"='rRNA') AND "species"='homo_sapiens' 
LIMIT 10;
```

## Stop the application
Once done, stop Docker.
```
docker-compose down
```