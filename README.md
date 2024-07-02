# Query Biomart with Data Connect
Tied to project [ensembl-biomart-2024](repos)

This repo contains a Flask application to query the new BioMart implementation with Data Connect, and suppose you already have Trino and S3 set up and running ([biomart-trino-s3](repos)).

## Installation
- Python version 3.10 with packages from `requirements.txt`
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
### Start Data Connect
```
cd docker
docker-compose up -d
```

Check if Data Connect runs correctly by going on `localhost:8089/tables` and browsing tables.

### Query with Data Connect
```
python -m flask run --port 8000
```

Go to `localhost:8000` and construct your query by selecting the table, species and columns.

Once done, stop Docker.
```
docker-compose down
```