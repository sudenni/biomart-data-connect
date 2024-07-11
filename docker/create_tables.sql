create schema hive.biomart with (location = 's3a://20240625-241-genomes/');

create table
hive.biomart.gene (
gene_id BIGINT,
stable_id VARCHAR,
region_name VARCHAR,
"start" BIGINT,
"end" BIGINT,
strand BIGINT,
biotype VARCHAR,
source VARCHAR,
gene_name VARCHAR,
gene_symbol VARCHAR,
nomenclature_symbol VARCHAR,
nomenclature_provider VARCHAR,
canonical_transcript VARCHAR,
transcript_stable_ids ARRAY(VARCHAR),
translation_stable_ids ARRAY(VARCHAR),
synonym ARRAY(VARCHAR),
GC_content ARRAY(VARCHAR),
havana_cv ARRAY(VARCHAR),
proj_parent_gene ARRAY(VARCHAR),
alternative_name ARRAY(VARCHAR),
go_terms ARRAY(VARCHAR),
species VARCHAR
)
with (external_location = 's3a://20240625-241-genomes/gene', format = 'PARQUET', partitioned_by = ARRAY['species']);

create table
hive.biomart.transcript (
transcript_id BIGINT,
stable_id VARCHAR,
region_name VARCHAR,
"start" BIGINT,
"end" BIGINT,
strand BIGINT,
biotype VARCHAR,
source VARCHAR,
description VARCHAR,
transcript_symbol VARCHAR,
translation_stable_ids ARRAY(VARCHAR),
miRNA_coordinates ARRAY(VARCHAR),
frameshift ARRAY(VARCHAR),
ncRNA ARRAY(VARCHAR),
MANE_select ARRAY(VARCHAR),
MANE_plus_clinical ARRAY(VARCHAR),
go_terms ARRAY(VARCHAR),
species VARCHAR
)
with (external_location = 's3a://20240625-241-genomes/transcript', format = 'PARQUET', partitioned_by = ARRAY['species']);

create table
hive.biomart.translation (
translation_id BIGINT,
stable_id VARCHAR,
"start" BIGINT,
"end" BIGINT,
go_terms ARRAY(VARCHAR),
species VARCHAR
)
with (external_location = 's3a://20240625-241-genomes/translation', format = 'PARQUET', partitioned_by = ARRAY['species']);

call hive.system.sync_partition_metadata('biomart', 'gene', 'ADD');

call hive.system.sync_partition_metadata('biomart', 'transcript', 'ADD');

call hive.system.sync_partition_metadata('biomart', 'translation', 'ADD');