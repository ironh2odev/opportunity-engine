import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from app.schemas import (
    PersonalLead,
    PersonalLeadCreateRequest,
    PersonalLeadUpdateRequest,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_private_data_dir() -> Path:
    default_path = _repo_root() / "private" / "local-data"
    configured = os.environ.get("OE_PRIVATE_DATA_DIR")
    return Path(configured).resolve() if configured else default_path


def get_db_path() -> Path:
    configured = os.environ.get("OE_PERSONAL_DB_PATH")
    if configured:
        return Path(configured).resolve()
    return get_private_data_dir() / "personal_mode.db"


def _connect() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        create table if not exists personal_leads (
            id text primary key,
            name text not null default '',
            role text not null default '',
            organisation text not null default '',
            organisation_website text not null default '',
            linkedin_url text not null default '',
            email text not null default '',
            location text not null default '',
            source text not null default '',
            opportunity_type text not null,
            relationship_strength text not null,
            status text not null,
            fit_score integer not null,
            priority text not null,
            problem_observed text not null default '',
            why_relevant text not null default '',
            suggested_angle text not null default '',
            notes text not null default '',
            tags text not null default '[]',
            next_action text not null default '',
            follow_up_date text,
            created_at text not null,
            updated_at text not null
        )
        """
    )
    conn.commit()
    return conn


def _to_model(row: sqlite3.Row) -> PersonalLead:
    return PersonalLead(
        id=row["id"],
        name=row["name"],
        role=row["role"],
        organisation=row["organisation"],
        organisation_website=row["organisation_website"],
        linkedin_url=row["linkedin_url"],
        email=row["email"],
        location=row["location"],
        source=row["source"],
        opportunity_type=row["opportunity_type"],
        relationship_strength=row["relationship_strength"],
        status=row["status"],
        fit_score=row["fit_score"],
        priority=row["priority"],
        problem_observed=row["problem_observed"],
        why_relevant=row["why_relevant"],
        suggested_angle=row["suggested_angle"],
        notes=row["notes"],
        tags=json.loads(row["tags"] or "[]"),
        next_action=row["next_action"],
        follow_up_date=row["follow_up_date"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def list_leads(
    *,
    opportunity_type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> list[PersonalLead]:
    conn = _connect()
    try:
        query = "select * from personal_leads where 1=1"
        params: list[str] = []
        if opportunity_type:
            query += " and opportunity_type = ?"
            params.append(opportunity_type)
        if status:
            query += " and status = ?"
            params.append(status)
        if priority:
            query += " and priority = ?"
            params.append(priority)
        query += " order by updated_at desc"
        rows = conn.execute(query, params).fetchall()
        return [_to_model(row) for row in rows]
    finally:
        conn.close()


def get_lead(lead_id: str) -> Optional[PersonalLead]:
    conn = _connect()
    try:
        row = conn.execute("select * from personal_leads where id = ?", [lead_id]).fetchone()
        return _to_model(row) if row else None
    finally:
        conn.close()


def create_lead(payload: PersonalLeadCreateRequest) -> PersonalLead:
    if not payload.name.strip() and not payload.organisation.strip():
        raise ValueError("name or organisation is required")

    now = _now_iso()
    lead = PersonalLead(
        id=f"lead_{uuid4().hex[:12]}",
        name=payload.name.strip(),
        role=payload.role.strip(),
        organisation=payload.organisation.strip(),
        organisation_website=payload.organisation_website.strip(),
        linkedin_url=payload.linkedin_url.strip(),
        email=payload.email.strip(),
        location=payload.location.strip(),
        source=payload.source.strip(),
        opportunity_type=payload.opportunity_type,
        relationship_strength=payload.relationship_strength,
        status=payload.status,
        fit_score=payload.fit_score,
        priority=payload.priority,
        problem_observed=payload.problem_observed.strip(),
        why_relevant=payload.why_relevant.strip(),
        suggested_angle=payload.suggested_angle.strip(),
        notes=payload.notes.strip(),
        tags=[tag.strip() for tag in payload.tags if tag.strip()],
        next_action=payload.next_action.strip(),
        follow_up_date=payload.follow_up_date,
        created_at=now,
        updated_at=now,
    )

    conn = _connect()
    try:
        conn.execute(
            """
            insert into personal_leads (
                id, name, role, organisation, organisation_website, linkedin_url, email,
                location, source, opportunity_type, relationship_strength, status, fit_score,
                priority, problem_observed, why_relevant, suggested_angle, notes, tags,
                next_action, follow_up_date, created_at, updated_at
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                lead.id,
                lead.name,
                lead.role,
                lead.organisation,
                lead.organisation_website,
                lead.linkedin_url,
                lead.email,
                lead.location,
                lead.source,
                lead.opportunity_type,
                lead.relationship_strength,
                lead.status,
                lead.fit_score,
                lead.priority,
                lead.problem_observed,
                lead.why_relevant,
                lead.suggested_angle,
                lead.notes,
                json.dumps(lead.tags),
                lead.next_action,
                lead.follow_up_date,
                lead.created_at,
                lead.updated_at,
            ],
        )
        conn.commit()
        return lead
    finally:
        conn.close()


def update_lead(lead_id: str, payload: PersonalLeadUpdateRequest) -> Optional[PersonalLead]:
    existing = get_lead(lead_id)
    if existing is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data:
        update_data["name"] = update_data["name"].strip()
    if "organisation" in update_data:
        update_data["organisation"] = update_data["organisation"].strip()

    next_name = update_data.get("name", existing.name)
    next_org = update_data.get("organisation", existing.organisation)
    if not next_name.strip() and not next_org.strip():
        raise ValueError("name or organisation is required")

    values = {**existing.model_dump(), **update_data}
    values["updated_at"] = _now_iso()
    if isinstance(values.get("tags"), list):
        values["tags"] = [tag.strip() for tag in values["tags"] if tag.strip()]

    conn = _connect()
    try:
        conn.execute(
            """
            update personal_leads
            set name = ?, role = ?, organisation = ?, organisation_website = ?, linkedin_url = ?,
                email = ?, location = ?, source = ?, opportunity_type = ?, relationship_strength = ?,
                status = ?, fit_score = ?, priority = ?, problem_observed = ?, why_relevant = ?,
                suggested_angle = ?, notes = ?, tags = ?, next_action = ?, follow_up_date = ?,
                updated_at = ?
            where id = ?
            """,
            [
                values["name"],
                values["role"],
                values["organisation"],
                values["organisation_website"],
                values["linkedin_url"],
                values["email"],
                values["location"],
                values["source"],
                values["opportunity_type"],
                values["relationship_strength"],
                values["status"],
                values["fit_score"],
                values["priority"],
                values["problem_observed"],
                values["why_relevant"],
                values["suggested_angle"],
                values["notes"],
                json.dumps(values["tags"]),
                values["next_action"],
                values["follow_up_date"],
                values["updated_at"],
                lead_id,
            ],
        )
        conn.commit()
    finally:
        conn.close()

    return get_lead(lead_id)


def delete_lead(lead_id: str) -> bool:
    conn = _connect()
    try:
        result = conn.execute("delete from personal_leads where id = ?", [lead_id])
        conn.commit()
        return result.rowcount > 0
    finally:
        conn.close()


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()
    

