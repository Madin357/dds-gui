"""Load transformed records into the platform database."""

import uuid
import logging
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.sync.transformers.base import BOOLEAN_COLUMNS, to_bool

logger = logging.getLogger(__name__)

# Lookup caches per sync run (source_id → platform UUID)
_caches: dict[str, dict[str, str]] = {}


def _get_cache(table: str) -> dict:
    if table not in _caches:
        _caches[table] = {}
    return _caches[table]


def _resolve_source_id(db: Session, table: str, institution_id: str, source_id: str) -> str | None:
    """Resolve a source_id reference to a platform UUID."""
    cache = _get_cache(table)
    cache_key = f"{institution_id}:{source_id}"
    if cache_key in cache:
        return cache[cache_key]

    result = db.execute(
        text(f"SELECT id FROM {table} WHERE institution_id = :inst AND source_id = :sid"),
        {"inst": institution_id, "sid": source_id},
    ).fetchone()

    if result:
        cache[cache_key] = str(result[0])
        return str(result[0])
    return None


def clear_caches():
    _caches.clear()


def _normalize_values(record: dict) -> dict:
    """Ensure all values are PostgreSQL-compatible types.

    - Boolean columns get proper Python bool (not int 1/0)
    """
    for col in BOOLEAN_COLUMNS:
        if col in record:
            record[col] = to_bool(record[col])
    return record


def upsert_records(
    db: Session,
    target_table: str,
    records: list[dict],
    institution_id: str,
    source_key: str = "source_id",
) -> tuple[int, int]:
    """
    Upsert records into the target table.
    Uses savepoints so a single bad record does not abort the whole batch.
    Returns (synced_count, failed_count).
    """
    synced = 0
    failed = 0

    for record in records:
        try:
            # Use a savepoint so one failure doesn't poison the transaction
            with db.begin_nested():
                # Resolve foreign key references
                resolved = {}
                for key, value in record.items():
                    if key == "_student_source_id":
                        resolved_id = _resolve_source_id(db, "students", institution_id, str(value))
                        if resolved_id:
                            resolved["student_id"] = resolved_id
                    elif key == "_course_source_id":
                        resolved_id = _resolve_source_id(db, "courses", institution_id, str(value))
                        if resolved_id:
                            resolved["course_id"] = resolved_id
                    elif key == "_program_source_id":
                        resolved_id = _resolve_source_id(db, "programs", institution_id, str(value))
                        if resolved_id:
                            resolved["program_id"] = resolved_id
                    else:
                        resolved[key] = value

                # Skip if required FK couldn't be resolved
                if target_table in ("enrollments",) and ("student_id" not in resolved or "program_id" not in resolved):
                    failed += 1
                    continue
                if target_table in ("attendance_records", "assessments") and ("student_id" not in resolved or "course_id" not in resolved):
                    failed += 1
                    continue

                source_id = resolved.get("source_id")
                if not source_id:
                    failed += 1
                    continue

                # Normalize types for PostgreSQL compatibility
                resolved = _normalize_values(resolved)

                # Check if record exists
                existing = db.execute(
                    text(f"SELECT id FROM {target_table} WHERE institution_id = :inst AND source_id = :sid"),
                    {"inst": institution_id, "sid": source_id},
                ).fetchone()

                if existing:
                    # UPDATE
                    set_clause = ", ".join(
                        f"{k} = :{k}" for k in resolved.keys()
                        if k not in ("institution_id", "source_id")
                    )
                    if set_clause:
                        resolved["_existing_id"] = str(existing[0])
                        resolved["_updated_now"] = datetime.now(timezone.utc).isoformat()
                        db.execute(
                            text(f"UPDATE {target_table} SET {set_clause}, updated_at = :_updated_now WHERE id = :_existing_id"),
                            resolved,
                        )
                else:
                    # INSERT
                    new_id = str(uuid.uuid4())
                    resolved["id"] = new_id
                    now = datetime.now(timezone.utc).isoformat()
                    resolved["created_at"] = now
                    resolved["updated_at"] = now
                    cols = ", ".join(resolved.keys())
                    vals = ", ".join(f":{k}" for k in resolved.keys())
                    db.execute(text(f"INSERT INTO {target_table} ({cols}) VALUES ({vals})"), resolved)

                    # Cache the new ID
                    cache = _get_cache(target_table)
                    cache[f"{institution_id}:{source_id}"] = new_id

            synced += 1

        except Exception as e:
            # Savepoint was rolled back automatically — transaction is still usable
            logger.warning(f"Failed to upsert record into {target_table}: {e}")
            failed += 1

    db.commit()
    return synced, failed
