from typing import Optional
from pypika import Table, Query

class TypedTable(Table):
    __table__ = ""

    def __init__(
            self,
            name: Optional[str] = None,
            schema: Optional[str] = None,
            alias: Optional[str] = None,
            query_cls: Optional[Query] = None,
    ) -> None:
        if name is None:
            if self.__table__:
                name = self.__table__
            else:
                name = self.__class__.__name__

        super().__init__(name, schema, alias, query_cls)

class Gene(TypedTable):
    __table__ = 'gene'

    gene_id: int
    stable_id: str
    region_name: str
    start: int
    end: int
    strand: int
    biotype: str
    source: str
    description: str
    gene_symbol: str
    nomenclature_symbol: str
    nomenclature_provider: str
    canonical_transcript: str
    transcript_stable_ids: list
    translation_stable_ids: list
    synonym: list
    GC_content: list
    havana_cv: list
    proj_parent_gene: list
    alternative_name: list
    go_terms: list
    species: str


class Transcript(TypedTable):
    __table__ = 'transcript'

    transcript_id: int
    stable_id: str
    region_name: str
    start: int
    end: int
    strand: int
    biotype: str
    source: str
    description: str
    transcript_symbol: str
    mirna_coordinates: list
    frameshift: list
    ncrna: list
    mane_select: list
    mane_plus_clinical: list
    go_terms: list
    species: str



class Translation(TypedTable):
    __table__ = 'translation'

    translation_id: int
    stable_id: str
    start: int
    end: int
    go_terms: list
    species: str