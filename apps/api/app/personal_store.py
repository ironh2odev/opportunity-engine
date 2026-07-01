import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from app.schemas import (
    ActionChannel,
    ActionDraftRevision,
    CareerContext,
    CareerContextUpdateRequest,
    DailyActionStatus,
    DraftRevisionSource,
    PersonalLead,
    PersonalLeadCreateRequest,
    PersonalRuleAction,
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
    conn.execute("pragma foreign_keys = on")
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
    conn.execute(
        """
        create table if not exists personal_rule_actions (
            id text primary key,
            source_lead_id text not null,
            channel text not null,
            action_type text not null,
            suggested_action text not null,
            suggested_message text not null,
            rationale text not null,
            proof_to_reference text not null,
            status text not null,
            approval_required integer not null,
            follow_up_date text,
            edited_by text,
            edited_at text,
            draft_source text,
            created_at text not null,
            updated_at text not null,
            foreign key (source_lead_id) references personal_leads(id) on delete cascade
        )
        """
    )
    conn.execute(
        """
        create table if not exists personal_rule_action_approvals (
            id text primary key,
            action_id text not null unique,
            approved_by text not null,
            approved_at text not null,
            note text,
            foreign key (action_id) references personal_rule_actions(id) on delete cascade
        )
        """
    )
    conn.execute(
        """
        create table if not exists personal_rule_action_revisions (
            id text primary key,
            action_id text not null,
            draft_message text not null,
            short_version text,
            source text not null,
            confidence_label text,
            risks_or_gaps text not null default '[]',
            review_notes text not null default '[]',
            created_at text not null,
            created_by text not null,
            foreign key (action_id) references personal_rule_actions(id) on delete cascade
        )
        """
    )
    conn.execute(
        """
        create table if not exists personal_career_context (
            id integer primary key check (id = 1),
            current_headline text not null default '',
            target_roles text not null default '[]',
            core_skills text not null default '[]',
            technical_stack text not null default '[]',
            project_highlights text not null default '[]',
            industries text not null default '[]',
            location_preferences text not null default '[]',
            visa_notes text not null default '',
            preferred_opportunity_types text not null default '[]',
            positioning_statement text not null default '',
            proof_points text not null default '[]',
            raw_cv_text text not null default '',
            updated_at text not null
        )
        """
    )
    for column_name, column_type in [
        ("edited_by", "text"),
        ("edited_at", "text"),
        ("draft_source", "text"),
    ]:
        try:
            conn.execute(
                f"alter table personal_rule_actions add column {column_name} {column_type}"
            )
        except sqlite3.OperationalError:
            pass
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

    role_key = payload.role.strip().lower()
    org_key = payload.organisation.strip().lower()
    source_key = payload.source.strip().lower()
    source_url = (payload.linkedin_url or payload.organisation_website or "").strip().lower()

    conn = _connect()
    try:
        existing_row: sqlite3.Row | None = None
        if role_key and org_key and source_url:
            existing_row = conn.execute(
                """
                select id from personal_leads
                where lower(role) = ?
                  and lower(organisation) = ?
                  and (lower(linkedin_url) = ? or lower(organisation_website) = ?)
                limit 1
                """,
                [role_key, org_key, source_url, source_url],
            ).fetchone()
        if existing_row is None and role_key and org_key and source_key:
            existing_row = conn.execute(
                """
                select id from personal_leads
                where lower(role) = ?
                  and lower(organisation) = ?
                  and lower(source) = ?
                limit 1
                """,
                [role_key, org_key, source_key],
            ).fetchone()
        if existing_row is not None:
            raise ValueError("Existing lead found for this source and role. Review the existing lead instead of creating a duplicate.")
    finally:
        conn.close()

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


def _to_rule_action_model(row: sqlite3.Row) -> PersonalRuleAction:
    return PersonalRuleAction(
        id=row["id"],
        source_lead_id=row["source_lead_id"],
        channel=row["channel"],
        action_type=row["action_type"],
        suggested_action=row["suggested_action"],
        suggested_message=row["suggested_message"],
        rationale=row["rationale"],
        proof_to_reference=row["proof_to_reference"],
        status=row["status"],
        approval_required=bool(row["approval_required"]),
        follow_up_date=row["follow_up_date"],
        edited_by=row["edited_by"],
        edited_at=row["edited_at"],
        draft_source=row["draft_source"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _to_rule_action_revision_model(row: sqlite3.Row) -> ActionDraftRevision:
    return ActionDraftRevision(
        id=row["id"],
        action_id=row["action_id"],
        draft_message=row["draft_message"],
        short_version=row["short_version"],
        source=row["source"],
        confidence_label=row["confidence_label"],
        risks_or_gaps=json.loads(row["risks_or_gaps"] or "[]"),
        review_notes=json.loads(row["review_notes"] or "[]"),
        created_at=row["created_at"],
        created_by=row["created_by"],
    )


def _to_career_context_model(row: sqlite3.Row) -> CareerContext:
    return CareerContext(
        current_headline=row["current_headline"],
        target_roles=json.loads(row["target_roles"] or "[]"),
        core_skills=json.loads(row["core_skills"] or "[]"),
        technical_stack=json.loads(row["technical_stack"] or "[]"),
        project_highlights=json.loads(row["project_highlights"] or "[]"),
        industries=json.loads(row["industries"] or "[]"),
        location_preferences=json.loads(row["location_preferences"] or "[]"),
        visa_notes=row["visa_notes"],
        preferred_opportunity_types=json.loads(row["preferred_opportunity_types"] or "[]"),
        positioning_statement=row["positioning_statement"],
        proof_points=json.loads(row["proof_points"] or "[]"),
        raw_cv_text=row["raw_cv_text"],
        updated_at=row["updated_at"],
    )


def get_career_context() -> CareerContext:
    conn = _connect()
    try:
        row = conn.execute("select * from personal_career_context where id = 1").fetchone()
        if row is None:
            now = _now_iso()
            conn.execute(
                """
                insert into personal_career_context (
                    id, current_headline, target_roles, core_skills, technical_stack,
                    project_highlights, industries, location_preferences, visa_notes,
                    preferred_opportunity_types, positioning_statement, proof_points,
                    raw_cv_text, updated_at
                ) values (1, '', '[]', '[]', '[]', '[]', '[]', '[]', '', '[]', '', '[]', '', ?)
                """,
                [now],
            )
            conn.commit()
            row = conn.execute("select * from personal_career_context where id = 1").fetchone()
        return _to_career_context_model(row)
    finally:
        conn.close()


def update_career_context(payload: CareerContextUpdateRequest) -> CareerContext:
    now = _now_iso()
    conn = _connect()
    try:
        conn.execute(
            """
            insert into personal_career_context (
                id, current_headline, target_roles, core_skills, technical_stack,
                project_highlights, industries, location_preferences, visa_notes,
                preferred_opportunity_types, positioning_statement, proof_points,
                raw_cv_text, updated_at
            ) values (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            on conflict(id) do update set
                current_headline = excluded.current_headline,
                target_roles = excluded.target_roles,
                core_skills = excluded.core_skills,
                technical_stack = excluded.technical_stack,
                project_highlights = excluded.project_highlights,
                industries = excluded.industries,
                location_preferences = excluded.location_preferences,
                visa_notes = excluded.visa_notes,
                preferred_opportunity_types = excluded.preferred_opportunity_types,
                positioning_statement = excluded.positioning_statement,
                proof_points = excluded.proof_points,
                raw_cv_text = excluded.raw_cv_text,
                updated_at = excluded.updated_at
            """,
            [
                payload.current_headline.strip(),
                json.dumps([item.strip() for item in payload.target_roles if item.strip()]),
                json.dumps([item.strip() for item in payload.core_skills if item.strip()]),
                json.dumps([item.strip() for item in payload.technical_stack if item.strip()]),
                json.dumps([item.strip() for item in payload.project_highlights if item.strip()]),
                json.dumps([item.strip() for item in payload.industries if item.strip()]),
                json.dumps([item.strip() for item in payload.location_preferences if item.strip()]),
                payload.visa_notes.strip(),
                json.dumps(payload.preferred_opportunity_types),
                payload.positioning_statement.strip(),
                json.dumps([item.strip() for item in payload.proof_points if item.strip()]),
                payload.raw_cv_text,
                now,
            ],
        )
        conn.commit()
    finally:
        conn.close()

    return get_career_context()


def get_rule_action(action_id: str) -> Optional[PersonalRuleAction]:
    conn = _connect()
    try:
        row = conn.execute("select * from personal_rule_actions where id = ?", [action_id]).fetchone()
        return _to_rule_action_model(row) if row else None
    finally:
        conn.close()


def list_rule_actions() -> list[PersonalRuleAction]:
    conn = _connect()
    try:
        rows = conn.execute("select * from personal_rule_actions order by created_at desc").fetchall()
        return [_to_rule_action_model(row) for row in rows]
    finally:
        conn.close()


def update_rule_action_status(action_id: str, status: DailyActionStatus) -> Optional[PersonalRuleAction]:
    action = get_rule_action(action_id)
    if action is None:
        return None

    conn = _connect()
    try:
        now = _now_iso()
        conn.execute(
            """
            update personal_rule_actions
            set status = ?, updated_at = ?
            where id = ?
            """,
            [status, now, action_id],
        )
        conn.commit()
    finally:
        conn.close()

    return get_rule_action(action_id)


def update_rule_action_draft(
    action_id: str,
    *,
    draft_message: str,
    edited_by: str,
    source: DraftRevisionSource,
) -> Optional[PersonalRuleAction]:
    action = get_rule_action(action_id)
    if action is None:
        return None

    conn = _connect()
    try:
        now = _now_iso()
        conn.execute(
            """
            update personal_rule_actions
            set suggested_message = ?, edited_by = ?, edited_at = ?, draft_source = ?, updated_at = ?
            where id = ?
            """,
            [draft_message, edited_by, now, source, now, action_id],
        )
        conn.commit()
    finally:
        conn.close()

    return get_rule_action(action_id)


def add_rule_action_revision(
    action_id: str,
    *,
    draft_message: str,
    short_version: Optional[str],
    source: DraftRevisionSource,
    confidence_label: Optional[str],
    risks_or_gaps: list[str],
    review_notes: list[str],
    created_by: str,
) -> ActionDraftRevision:
    revision = ActionDraftRevision(
        id=f"rev_{uuid4().hex[:12]}",
        action_id=action_id,
        draft_message=draft_message,
        short_version=short_version,
        source=source,
        confidence_label=confidence_label,
        risks_or_gaps=risks_or_gaps,
        review_notes=review_notes,
        created_at=_now_iso(),
        created_by=created_by,
    )

    conn = _connect()
    try:
        conn.execute(
            """
            insert into personal_rule_action_revisions (
                id, action_id, draft_message, short_version, source, confidence_label,
                risks_or_gaps, review_notes, created_at, created_by
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                revision.id,
                revision.action_id,
                revision.draft_message,
                revision.short_version,
                revision.source,
                revision.confidence_label,
                json.dumps(revision.risks_or_gaps),
                json.dumps(revision.review_notes),
                revision.created_at,
                revision.created_by,
            ],
        )
        conn.commit()
    finally:
        conn.close()

    return revision


def list_rule_action_revisions(action_id: str) -> list[ActionDraftRevision]:
    conn = _connect()
    try:
        rows = conn.execute(
            """
            select *
            from personal_rule_action_revisions
            where action_id = ?
            order by created_at desc
            """,
            [action_id],
        ).fetchall()
        return [_to_rule_action_revision_model(row) for row in rows]
    finally:
        conn.close()


def _to_rule_action_approval_model(row: sqlite3.Row):
    return {
        "id": row["id"],
        "action_id": row["action_id"],
        "approved_by": row["approved_by"],
        "approved_at": row["approved_at"],
        "note": row["note"],
    }


def get_rule_action_approval(action_id: str):
    conn = _connect()
    try:
        row = conn.execute(
            "select * from personal_rule_action_approvals where action_id = ?",
            [action_id],
        ).fetchone()
        return _to_rule_action_approval_model(row) if row else None
    finally:
        conn.close()


def list_rule_action_approvals():
    conn = _connect()
    try:
        rows = conn.execute(
            "select * from personal_rule_action_approvals order by approved_at desc"
        ).fetchall()
        return [_to_rule_action_approval_model(row) for row in rows]
    finally:
        conn.close()


def record_rule_action_approval(action_id: str, approved_by: str, note: Optional[str] = None):
    existing = get_rule_action_approval(action_id)
    if existing is not None:
        return existing

    now = _now_iso()
    approval = {
        "id": f"approval_{uuid4().hex[:12]}",
        "action_id": action_id,
        "approved_by": approved_by,
        "approved_at": now,
        "note": note,
    }

    conn = _connect()
    try:
        conn.execute(
            """
            insert into personal_rule_action_approvals (
                id, action_id, approved_by, approved_at, note
            ) values (?, ?, ?, ?, ?)
            """,
            [
                approval["id"],
                approval["action_id"],
                approval["approved_by"],
                approval["approved_at"],
                approval["note"],
            ],
        )
        conn.commit()
    finally:
        conn.close()

    return approval


def has_rule_action_approval(action_id: str) -> bool:
    return get_rule_action_approval(action_id) is not None


def list_rule_actions_for_date(date: str) -> list[PersonalRuleAction]:
    conn = _connect()
    try:
        rows = conn.execute(
            """
            select *
            from personal_rule_actions
            where substr(created_at, 1, 10) = ?
            order by created_at desc
            """,
            [date],
        ).fetchall()
        return [_to_rule_action_model(row) for row in rows]
    finally:
        conn.close()


def create_rule_action(
    *,
    source_lead_id: str,
    channel: ActionChannel,
    action_type: str,
    suggested_action: str,
    suggested_message: str,
    rationale: str,
    proof_to_reference: str,
    status: DailyActionStatus,
    approval_required: bool,
    follow_up_date: Optional[str] = None,
) -> PersonalRuleAction:
    now = _now_iso()
    action = PersonalRuleAction(
        id=f"pra_{uuid4().hex[:12]}",
        source_lead_id=source_lead_id,
        channel=channel,
        action_type=action_type,
        suggested_action=suggested_action,
        suggested_message=suggested_message,
        rationale=rationale,
        proof_to_reference=proof_to_reference,
        status=status,
        approval_required=approval_required,
        follow_up_date=follow_up_date,
        edited_by=None,
        edited_at=None,
        draft_source=None,
        created_at=now,
        updated_at=now,
    )

    conn = _connect()
    try:
        conn.execute(
            """
            insert into personal_rule_actions (
                id, source_lead_id, channel, action_type, suggested_action, suggested_message,
                rationale, proof_to_reference, status, approval_required, follow_up_date,
                edited_by, edited_at, draft_source, created_at, updated_at
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                action.id,
                action.source_lead_id,
                action.channel,
                action.action_type,
                action.suggested_action,
                action.suggested_message,
                action.rationale,
                action.proof_to_reference,
                action.status,
                1 if action.approval_required else 0,
                action.follow_up_date,
                action.edited_by,
                action.edited_at,
                action.draft_source,
                action.created_at,
                action.updated_at,
            ],
        )
        conn.commit()
        return action
    finally:
        conn.close()


def list_rule_actions_for_lead(lead_id: str) -> list[PersonalRuleAction]:
    conn = _connect()
    try:
        rows = conn.execute(
            """
            select *
            from personal_rule_actions
            where source_lead_id = ?
            order by created_at desc
            """,
            [lead_id],
        ).fetchall()
        return [_to_rule_action_model(row) for row in rows]
    finally:
        conn.close()


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()
    

