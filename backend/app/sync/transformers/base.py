"""Transform records from source format to platform format."""

import logging

logger = logging.getLogger(__name__)

# Tables that have an is_active NOT NULL column
_TABLES_WITH_IS_ACTIVE = {"programs", "courses", "students"}
# Tables that have max_score NOT NULL column
_TABLES_WITH_MAX_SCORE = {"assessments"}


def transform_records(
    records: list[dict],
    field_map: dict[str, str],
    institution_id: str,
    target_table: str = "",
) -> list[dict]:
    transformed = []
    for record in records:
        row = {"institution_id": institution_id}
        for source_field, target_field in field_map.items():
            value = record.get(source_field)
            if value is not None:
                if target_field == "source_id":
                    value = str(value)
                elif target_field.startswith("_") and target_field.endswith("_source_id"):
                    value = str(value)
                row[target_field] = value

        # Handle student status → is_active conversion
        if "_status" in row:
            status_val = row.pop("_status")
            row["is_active"] = 1 if status_val in ("active", "probation") else 0

        # Add defaults for NOT NULL columns
        if target_table in _TABLES_WITH_IS_ACTIVE and "is_active" not in row:
            row["is_active"] = 1
        if target_table in _TABLES_WITH_MAX_SCORE and "max_score" not in row:
            row["max_score"] = 100

        transformed.append(row)

    logger.info(f"Transformed {len(transformed)} records for {target_table}")
    return transformed
