from typing import Annotated
from pathlib import Path
from langchain_core.tools import tool
import os
import uuid
import json
import voyageai
from tidb_vector.integrations import TiDBVectorClient
from tidb_vector.integrations.vector_client import QueryResult
from dotenv import load_dotenv
from sqlalchemy import text
from ..database import SessionLocal
from ...utils.datetime_utils import get_utc_now_naive

load_dotenv()

voyager = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
vector_client = TiDBVectorClient(
    connection_string=os.getenv("TIDB_CONNECTION_STRING"),
    vector_dimension=1024,
    table_name="sample_ecommerce_app_code",
    drop_existing_table=False,
)


@tool
def get_data_from_embeddings(
    query: Annotated[str, "query for vector db"],
    top_K: Annotated[int, "No of nodes needs to be retried"] = 5,
) -> list[QueryResult]:
    """
    Retrieves the AST semantic nodes (abstract syntax tree–based code representations enriched with semantic metadata)
    of the project’s codebase from the vector database. This allows the agent to access relevant code structure, symbols,
    and relationships for tasks like debugging, refactoring, or answering stack-trace–related queries

    Search the indexed codebase (AST nodes with semantics).

    Generate human-like queries that capture the error, methods, classes, or stack trace context.

    Dynamically ask for more data if initial results are insufficient.

    Adjust the number of results (k) as needed to cover all relevant nodes.

    Always cross-verify results: only conclude root cause when multiple sources or nodes consistently point to the same issue.
    """
    query_embedding = voyager.embed(
        texts=[query], model="voyage-code-3", input_type="query"
    ).embeddings[0]
    relevant_files = vector_client.query(query_vector=query_embedding, k=top_K)
    return relevant_files


@tool
def get_file_content_from_path(
    path: Annotated[str, "file_path from the meta data of queryResult"],
) -> str:
    """Retrieves the content of the file from the path. Use this to get the full file content from the ast node's metadata"""
    path = Path(path)
    if path.is_file():
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            return f"error reading file: {e}"
    else:
        return "file not found"


@tool
def save_rca_to_db(
    crash_id: Annotated[str, "The Id of the crash given"],
    description: Annotated[str, "High-level description of the crash incident."],
    problem_identification: Annotated[
        str,
        "Details about how the crash was identified, including symptoms and triggers.",
    ],
    data_collection: Annotated[
        str,
        "Information or evidence collected during the investigation (logs, traces, metrics).",
    ],
    root_cause_identification: Annotated[
        str,
        "The underlying root cause of the crash (e.g., null pointer dereference, race condition).",
    ],
    solution: Annotated[
        str,
        "Proposed or implemented solution to resolve the issue and prevent recurrence.",
    ],
    supporting_documents: Annotated[
        list[str], "List of strings of supporting document references if any ."
    ],
):
    """
    Save a Root Cause Analysis (RCA) record into the database.

    This tool should be used when RCA workflow is completed
     for a crash and needs to persist the findings.
    """
    print("Saving RCA to DB")
    
    # Create database session
    db = SessionLocal()
    try:
        # Generate unique ID for the RCA record
        rca_id = str(uuid.uuid4())
        now = get_utc_now_naive()
        
        # Check if RCA already exists for this crash
        check_query = text("""
            SELECT id FROM crash_rca WHERE crash_id = :crash_id
        """)
        
        existing_result = db.execute(check_query, {"crash_id": crash_id})
        existing_rca = existing_result.fetchone()
        
        # Serialize supporting_documents to JSON
        supporting_documents_json = json.dumps(supporting_documents) if supporting_documents else None
        
        if existing_rca:
            # Update existing RCA record
            update_query = text("""
                UPDATE crash_rca 
                SET description = :description,
                    problem_identification = :problem_identification,
                    data_collection = :data_collection,
                    root_cause_identification = :root_cause_identification,
                    solution = :solution,
                    supporting_documents = :supporting_documents,
                    updated_at = :updated_at
                WHERE crash_id = :crash_id
            """)
            
            db.execute(update_query, {
                "crash_id": crash_id,
                "description": description,
                "problem_identification": problem_identification,
                "data_collection": data_collection,
                "root_cause_identification": root_cause_identification,
                "solution": solution,
                "supporting_documents": supporting_documents_json,
                "updated_at": now,
            })
            
            print(f"Updated existing RCA record for crash_id: {crash_id}")
        else:
            # Insert new RCA record
            insert_query = text("""
                INSERT INTO crash_rca (
                    id, crash_id, description, problem_identification, 
                    data_collection, root_cause_identification, solution, 
                    supporting_documents, created_at, updated_at
                ) VALUES (
                    :id, :crash_id, :description, :problem_identification,
                    :data_collection, :root_cause_identification, :solution,
                    :supporting_documents, :created_at, :updated_at
                )
            """)
            
            db.execute(insert_query, {
                "id": rca_id,
                "crash_id": crash_id,
                "description": description,
                "problem_identification": problem_identification,
                "data_collection": data_collection,
                "root_cause_identification": root_cause_identification,
                "solution": solution,
                "supporting_documents": supporting_documents_json,
                "created_at": now,
                "updated_at": now,
            })
            
            print(f"Created new RCA record with ID: {rca_id} for crash_id: {crash_id}")
        
        # Commit the transaction
        db.commit()
        print("RCA successfully saved to database")
        
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        print(f"Error saving RCA to database: {str(e)}")
        raise e
    finally:
        # Close the database session
        db.close()


@tool
def save_diff_to_db(diff: Annotated[str, "git diff of the changes"]):
    """Save the git diff of the changes to fix the crash to db"""
    # todo: save diff to db
    print("Saving diff to DB")
    print(diff)
