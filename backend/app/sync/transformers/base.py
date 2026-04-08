"""Transform records from source format to platform format."""

import logging

logger = logging.getLogger(__name__)


def transform_records(
    records: list[dict],
    field_map: dict[str, str],
    institution_id: str,
) -> list[dict]:
    """
    Apply field mapping to transform source records into platform format.

    Fields starting with '_' are internal references that need special handling
    during the load phase (e.g., _student_source_id → resolved to actual UUID).
    """
    transformed = []
    for record in records:
        row = {"institution_id": institution_id}
        for source_field, target_field in field_map.items():
            value = record.get(source_field)
            if value is not None:
                # Convert source_id to string
                if target_field == "source_id":
                    value = str(value)
                elif target_field.startswith("_") and target_field.endswith("_source_id"):
                    value = str(value)
                row[target_field] = value

        # Handle student status → is_active conversion
        if "_status" in row:
            status_val = row.pop("_status")
            row["is_active"] = status_val in ("active", "probation")

        transformed.append(row)

    logger.info(f"Transformed {len(transformed)} records")
    return transformed
