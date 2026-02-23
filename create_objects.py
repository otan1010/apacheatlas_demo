import json
from pyapacheatlas.auth import BasicAuthentication
from pyapacheatlas.core import AtlasClient, AtlasEntity, AtlasProcess

ATLAS_ENDPOINT = "http://localhost:21000/api/atlas/v2"
ATLAS_USER = "admin"
ATLAS_PASS = "admin"

auth = BasicAuthentication(ATLAS_USER, ATLAS_PASS)
client = AtlasClient(endpoint_url=ATLAS_ENDPOINT, authentication=auth)

# ---- Naming convention (must be unique per entity instance) ----
cluster = "dev-cluster"
db_name = "analytics"
db_qn = f"spark://{cluster}/{db_name}"

src_tbl = "events_raw"
dst_tbl = "events_daily"
src_qn = f"{db_qn}/{src_tbl}"
dst_qn = f"{db_qn}/{dst_tbl}"

# ---- Create Spark DB ----
spark_db = AtlasEntity(
    name=db_name,
    typeName="spark_db",
    qualified_name=db_qn,
    guid="-100",
    attributes={
        "name": db_name,
        "qualifiedName": db_qn,
        "clusterName": cluster,
        "location": f"/warehouse/{db_name}.db",
    },
)

# ---- Create Spark tables ----
src_table = AtlasEntity(
    name=src_tbl,
    typeName="spark_table",
    qualified_name=src_qn,
    guid="-101",
    attributes={
        "name": src_tbl,
        "qualifiedName": src_qn,
        "provider": "delta",
        "tableType": "MANAGED",
    },
)

dst_table = AtlasEntity(
    name=dst_tbl,
    typeName="spark_table",
    qualified_name=dst_qn,
    guid="-102",
    attributes={
        "name": dst_tbl,
        "qualifiedName": dst_qn,
        "provider": "delta",
        "tableType": "MANAGED",
    },
)

# Link table -> db using relationshipAttributes
# (Spark model commonly uses relationship attribute name "db" on spark_table)
src_table.addRelationship(db=spark_db)
dst_table.addRelationship(db=spark_db)

# ---- Create Spark columns ----
def spark_column(table_entity: AtlasEntity, col_name: str, col_type: str, guid: str) -> AtlasEntity:
    col_qn = f"{table_entity.qualifiedName}#col={col_name}"
    col = AtlasEntity(
        name=col_name,
        typeName="spark_column",
        qualified_name=col_qn,
        guid=guid,
        attributes={
            "name": col_name,
            "qualifiedName": col_qn,
            "type": col_type,
            "nullable": True,
        },
    )
    # Link column -> table using relationshipAttributes (often "table")
    col.addRelationship(table=table_entity)
    return col

src_cols = [
    spark_column(src_table, "event_time", "timestamp", "-110"),
    spark_column(src_table, "user_id", "string", "-111"),
    spark_column(src_table, "event_type", "string", "-112"),
]

dst_cols = [
    spark_column(dst_table, "event_date", "date", "-120"),
    spark_column(dst_table, "event_type", "string", "-121"),
    spark_column(dst_table, "cnt", "bigint", "-122"),
]

# ---- Create Spark process for lineage (inputs -> outputs) ----
# AtlasProcess forces you to provide inputs and outputs. :contentReference[oaicite:3]{index=3}
process_qn = f"spark://{cluster}/app=demo-job/run=2026-02-23T12:00:00Z"
spark_proc = AtlasProcess(
    name="events_raw_to_events_daily",
    typeName="spark_process",
    qualified_name=process_qn,
    inputs=[src_table],     # table entities are fine; SDK will minimize as needed
    outputs=[dst_table],
    guid="-200",
    attributes={
        "details": "Aggregate raw events into daily counts",
    },
)

# ---- Upload everything in one batch ----
batch = [spark_db, src_table, dst_table, *src_cols, *dst_cols, spark_proc]
resp = client.upload_entities(batch=batch)

print(json.dumps(resp, indent=2))
