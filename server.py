import json
import os
import uuid
from datetime import date
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP
from pydantic import Field

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

_DATA_PATH = Path(__file__).parent / "data" / "steelhead.json"
_db: dict = json.loads(_DATA_PATH.read_text())


def _match(record: dict, field: str, value: str) -> bool:
    """Case-insensitive substring match on a field."""
    return value.lower() in str(record.get(field, "")).lower()


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="steelhead-mock",
    version="1.0.0",
    instructions=(
        "Mock Steelhead ERP for Apex Metal Finishing — a contract metal finishing company "
        "in Grand Rapids MI. Query jobs, work orders, production schedule, inventory, quality "
        "holds, quotes, customers, vendors, and financial summary. Use get_daily_briefing for "
        "the morning operations report. Key processes: zinc plating, electroless nickel, "
        "anodizing, powder coating, chrome plating."
    ),
)

# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

@mcp.tool()
def get_customers(
    id: Optional[str] = Field(default=None, description="Filter by customer ID, e.g. CUST-001"),
    name: Optional[str] = Field(default=None, description="Filter by customer name (partial match)"),
    industry: Optional[str] = Field(default=None, description="Filter by industry (partial match), e.g. Automotive, Aerospace, Defense"),
    status: Optional[str] = Field(default=None, description="Filter by status: active | inactive"),
    account_manager: Optional[str] = Field(default=None, description="Filter by account manager name (partial match)"),
) -> list[dict]:
    """List customers. Optionally filter by ID, name, industry, status, or account manager."""
    results = _db["customers"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if industry:
        results = [r for r in results if _match(r, "industry", industry)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if account_manager:
        results = [r for r in results if _match(r, "account_manager", account_manager)]
    return results


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

@mcp.tool()
def get_jobs(
    id: Optional[str] = Field(default=None, description="Filter by job ID, e.g. JOB-001"),
    job_number: Optional[str] = Field(default=None, description="Filter by job number, e.g. JOB-2026-0841"),
    customer_id: Optional[str] = Field(default=None, description="Filter by customer ID, e.g. CUST-001"),
    customer_name: Optional[str] = Field(default=None, description="Filter by customer name (partial match)"),
    process_type: Optional[str] = Field(default=None, description="Filter by process type: zinc_plating | electroless_nickel | anodizing | powder_coating | chrome_plating | black_oxide | passivation"),
    status: Optional[str] = Field(default=None, description="Filter by status: quote | scheduled | in_process | quality_hold | completed | shipped | invoiced"),
    priority: Optional[str] = Field(default=None, description="Filter by priority: standard | rush | critical"),
    due_date_before: Optional[str] = Field(default=None, description="Return jobs with due_date on or before this date (YYYY-MM-DD)"),
    due_date_after: Optional[str] = Field(default=None, description="Return jobs with due_date on or after this date (YYYY-MM-DD)"),
) -> list[dict]:
    """List production jobs. Filter by ID, job number, customer, process type, status, priority, or due date range."""
    results = _db["jobs"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if job_number:
        results = [r for r in results if _match(r, "job_number", job_number)]
    if customer_id:
        results = [r for r in results if r["customer_id"].upper() == customer_id.upper()]
    if customer_name:
        results = [r for r in results if _match(r, "customer_name", customer_name)]
    if process_type:
        results = [r for r in results if _match(r, "process_type", process_type)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if priority:
        results = [r for r in results if _match(r, "priority", priority)]
    if due_date_before:
        results = [r for r in results if r.get("due_date") and r["due_date"] <= due_date_before]
    if due_date_after:
        results = [r for r in results if r.get("due_date") and r["due_date"] >= due_date_after]
    return results


# ---------------------------------------------------------------------------
# Work Orders
# ---------------------------------------------------------------------------

@mcp.tool()
def get_work_orders(
    id: Optional[str] = Field(default=None, description="Filter by work order ID, e.g. WO-001"),
    wo_number: Optional[str] = Field(default=None, description="Filter by WO number, e.g. WO-2026-1041"),
    job_id: Optional[str] = Field(default=None, description="Filter by linked job ID, e.g. JOB-001"),
    workstation: Optional[str] = Field(default=None, description="Filter by workstation name (partial match), e.g. Zinc Line 1, Anodize Tank A"),
    operator: Optional[str] = Field(default=None, description="Filter by operator name (partial match)"),
    status: Optional[str] = Field(default=None, description="Filter by status: open | in_progress | paused | completed | on_hold"),
    process_type: Optional[str] = Field(default=None, description="Filter by process type (partial match)"),
) -> list[dict]:
    """List work orders. Filter by ID, WO number, job, workstation, operator, status, or process type."""
    results = _db["work_orders"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if wo_number:
        results = [r for r in results if _match(r, "wo_number", wo_number)]
    if job_id:
        results = [r for r in results if r["job_id"].upper() == job_id.upper()]
    if workstation:
        results = [r for r in results if _match(r, "workstation", workstation)]
    if operator:
        results = [r for r in results if _match(r, "operator", operator)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if process_type:
        results = [r for r in results if _match(r, "process_type", process_type)]
    return results


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

@mcp.tool()
def get_inventory(
    id: Optional[str] = Field(default=None, description="Filter by inventory item ID, e.g. INV-001"),
    item_name: Optional[str] = Field(default=None, description="Filter by item name (partial match)"),
    category: Optional[str] = Field(default=None, description="Filter by category: chemicals | anodes | racking | packaging | ppe | equipment_parts"),
    status: Optional[str] = Field(default=None, description="Filter by stock status: ok | low | critical | overstock"),
    low_stock: bool = Field(default=False, description="If true, return only items where status is low or critical"),
    hazmat: Optional[bool] = Field(default=None, description="If true, return only hazmat items; if false, return only non-hazmat items"),
) -> list[dict]:
    """List inventory items. Filter by ID, name, category, status, low-stock flag, or hazmat flag."""
    results = _db["inventory"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if item_name:
        results = [r for r in results if _match(r, "item_name", item_name)]
    if category:
        results = [r for r in results if _match(r, "category", category)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if low_stock:
        results = [r for r in results if r.get("status") in ("low", "critical")]
    if hazmat is not None:
        results = [r for r in results if r.get("hazmat") == hazmat]
    return results


# ---------------------------------------------------------------------------
# Purchase Orders
# ---------------------------------------------------------------------------

@mcp.tool()
def get_purchase_orders(
    id: Optional[str] = Field(default=None, description="Filter by PO ID, e.g. PO-001"),
    po_number: Optional[str] = Field(default=None, description="Filter by PO number, e.g. PO-2026-0085"),
    vendor_id: Optional[str] = Field(default=None, description="Filter by vendor ID, e.g. VEND-001"),
    vendor_name: Optional[str] = Field(default=None, description="Filter by vendor name (partial match)"),
    status: Optional[str] = Field(default=None, description="Filter by status: open | partially_received | received | closed"),
) -> list[dict]:
    """List purchase orders. Filter by ID, PO number, vendor, or status."""
    results = _db["purchase_orders"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if po_number:
        results = [r for r in results if _match(r, "po_number", po_number)]
    if vendor_id:
        results = [r for r in results if r["vendor_id"].upper() == vendor_id.upper()]
    if vendor_name:
        results = [r for r in results if _match(r, "vendor_name", vendor_name)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    return results


# ---------------------------------------------------------------------------
# Vendors
# ---------------------------------------------------------------------------

@mcp.tool()
def get_vendors(
    id: Optional[str] = Field(default=None, description="Filter by vendor ID, e.g. VEND-001"),
    name: Optional[str] = Field(default=None, description="Filter by vendor name (partial match)"),
    vendor_type: Optional[str] = Field(default=None, description="Filter by vendor type: chemical_supplier | equipment | consumables | logistics"),
    status: Optional[str] = Field(default=None, description="Filter by status: active | inactive"),
) -> list[dict]:
    """List vendors. Filter by ID, name, vendor type, or status."""
    results = _db["vendors"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if vendor_type:
        results = [r for r in results if _match(r, "vendor_type", vendor_type)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    return results


# ---------------------------------------------------------------------------
# Quotes
# ---------------------------------------------------------------------------

@mcp.tool()
def get_quotes(
    id: Optional[str] = Field(default=None, description="Filter by quote ID, e.g. QT-001"),
    quote_number: Optional[str] = Field(default=None, description="Filter by quote number, e.g. QT-2026-0201"),
    customer_id: Optional[str] = Field(default=None, description="Filter by customer ID, e.g. CUST-001"),
    customer_name: Optional[str] = Field(default=None, description="Filter by customer name (partial match)"),
    process_type: Optional[str] = Field(default=None, description="Filter by process type (partial match)"),
    status: Optional[str] = Field(default=None, description="Filter by status: draft | sent | approved | declined | expired"),
) -> list[dict]:
    """List quotes. Filter by ID, quote number, customer, process type, or status."""
    results = _db["quotes"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if quote_number:
        results = [r for r in results if _match(r, "quote_number", quote_number)]
    if customer_id:
        results = [r for r in results if r["customer_id"].upper() == customer_id.upper()]
    if customer_name:
        results = [r for r in results if _match(r, "customer_name", customer_name)]
    if process_type:
        results = [r for r in results if _match(r, "process_type", process_type)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    return results


# ---------------------------------------------------------------------------
# Quality Holds
# ---------------------------------------------------------------------------

@mcp.tool()
def get_quality_holds(
    id: Optional[str] = Field(default=None, description="Filter by quality hold ID, e.g. QH-001"),
    job_id: Optional[str] = Field(default=None, description="Filter by linked job ID, e.g. JOB-003"),
    customer_name: Optional[str] = Field(default=None, description="Filter by customer name (partial match)"),
    process_type: Optional[str] = Field(default=None, description="Filter by process type (partial match)"),
    severity: Optional[str] = Field(default=None, description="Filter by severity: minor | major | critical"),
    status: Optional[str] = Field(default=None, description="Filter by status: open | under_review | disposition_pending | resolved"),
) -> list[dict]:
    """List quality holds. Filter by ID, job, customer, process type, severity, or status."""
    results = _db["quality_holds"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if job_id:
        results = [r for r in results if r["job_id"].upper() == job_id.upper()]
    if customer_name:
        results = [r for r in results if _match(r, "customer_name", customer_name)]
    if process_type:
        results = [r for r in results if _match(r, "process_type", process_type)]
    if severity:
        results = [r for r in results if _match(r, "severity", severity)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    return results


# ---------------------------------------------------------------------------
# Production Schedule
# ---------------------------------------------------------------------------

@mcp.tool()
def get_production_schedule(
    date: Optional[str] = Field(default=None, description="Filter by date (YYYY-MM-DD), e.g. 2026-10-19"),
    workstation: Optional[str] = Field(default=None, description="Filter by workstation name (partial match)"),
    process_type: Optional[str] = Field(default=None, description="Filter by process type (partial match)"),
    status: Optional[str] = Field(default=None, description="Filter by status: scheduled | in_progress | completed | delayed"),
    operator: Optional[str] = Field(default=None, description="Filter by operator name (partial match)"),
) -> list[dict]:
    """List production schedule entries. Filter by date, workstation, process type, status, or operator."""
    results = _db["production_schedule"]
    if date:
        results = [r for r in results if r.get("date") == date]
    if workstation:
        results = [r for r in results if _match(r, "workstation", workstation)]
    if process_type:
        results = [r for r in results if _match(r, "process_type", process_type)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if operator:
        results = [r for r in results if _match(r, "operator", operator)]
    return results


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

@mcp.tool()
def get_invoices(
    id: Optional[str] = Field(default=None, description="Filter by invoice ID, e.g. INV-001"),
    invoice_number: Optional[str] = Field(default=None, description="Filter by invoice number, e.g. INV-2026-0095"),
    customer_id: Optional[str] = Field(default=None, description="Filter by customer ID, e.g. CUST-001"),
    customer_name: Optional[str] = Field(default=None, description="Filter by customer name (partial match)"),
    status: Optional[str] = Field(default=None, description="Filter by status: open | paid | overdue | partial"),
) -> list[dict]:
    """List invoices. Filter by ID, invoice number, customer, or status."""
    results = _db["invoices"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if invoice_number:
        results = [r for r in results if _match(r, "invoice_number", invoice_number)]
    if customer_id:
        results = [r for r in results if r["customer_id"].upper() == customer_id.upper()]
    if customer_name:
        results = [r for r in results if _match(r, "customer_name", customer_name)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    return results


# ---------------------------------------------------------------------------
# Financial Summary
# ---------------------------------------------------------------------------

@mcp.tool()
def get_financial_summary() -> dict:
    """Return the financial summary for the last 30 days — revenue, margin, on-time delivery, quality yield, AR aging."""
    return _db["financial_summary"]


# ---------------------------------------------------------------------------
# Daily Briefing
# ---------------------------------------------------------------------------

@mcp.tool()
def get_daily_briefing() -> dict:
    """
    Return a structured morning operations briefing for Apex Metal Finishing.
    Includes: jobs in_process, jobs on quality_hold, critical-priority jobs,
    low/critical inventory items, open quality holds, and today's production schedule.
    Use this tool to power the daily operations report.
    """
    today = "2026-10-19"

    jobs_in_process = [j for j in _db["jobs"] if j["status"] == "in_process"]
    jobs_on_hold = [j for j in _db["jobs"] if j["status"] == "quality_hold"]
    critical_jobs = [j for j in _db["jobs"] if j["priority"] == "critical"]
    low_inventory = [i for i in _db["inventory"] if i.get("status") in ("low", "critical")]
    open_holds = [q for q in _db["quality_holds"] if q["status"] != "resolved"]
    todays_schedule = [s for s in _db["production_schedule"] if s.get("date") == today]

    return {
        "briefing_date": today,
        "company": _db["company"]["name"],
        "jobs_in_process": jobs_in_process,
        "jobs_on_quality_hold": jobs_on_hold,
        "critical_priority_jobs": critical_jobs,
        "low_and_critical_inventory": low_inventory,
        "open_quality_holds": open_holds,
        "todays_production_schedule": todays_schedule,
        "summary": {
            "active_jobs_count": len(jobs_in_process),
            "quality_holds_count": len(jobs_on_hold),
            "critical_jobs_count": len(critical_jobs),
            "low_inventory_items_count": len(low_inventory),
            "open_quality_holds_count": len(open_holds),
            "todays_scheduled_entries_count": len(todays_schedule),
        },
    }


# ---------------------------------------------------------------------------
# Update Job Status
# ---------------------------------------------------------------------------

@mcp.tool()
def update_job_status(
    id: str = Field(description="The job ID to update, e.g. JOB-001"),
    status: str = Field(description="New status: quote | scheduled | in_process | quality_hold | completed | shipped | invoiced"),
    notes: Optional[str] = Field(default=None, description="Optional notes to append to the job"),
) -> dict:
    """Update the status of a production job. Optionally append notes."""
    valid_statuses = {"quote", "scheduled", "in_process", "quality_hold", "completed", "shipped", "invoiced"}
    if status not in valid_statuses:
        return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(sorted(valid_statuses))}"}

    for job in _db["jobs"]:
        if job["id"].upper() == id.upper():
            old_status = job["status"]
            job["status"] = status
            if notes:
                existing = job.get("notes", "")
                job["notes"] = f"{existing}\n[Status update {status}]: {notes}".strip()
            return {
                "success": True,
                "id": job["id"],
                "job_number": job["job_number"],
                "old_status": old_status,
                "new_status": status,
                "notes": job.get("notes"),
            }

    return {"error": f"Job '{id}' not found."}


# ---------------------------------------------------------------------------
# Create Quality Hold
# ---------------------------------------------------------------------------

@mcp.tool()
def create_quality_hold(
    job_id: str = Field(description="The job ID to place on hold, e.g. JOB-001"),
    hold_reason: str = Field(description="Reason for the hold: thickness_out_of_spec | adhesion_failure | surface_defect | contamination | customer_rejection"),
    quantity_held: int = Field(description="Number of pieces being held"),
    severity: str = Field(description="Severity of the hold: minor | major | critical"),
    notes: str = Field(description="Description of the issue and observed defect"),
    assigned_to: str = Field(description="Name of the person responsible for resolving the hold"),
) -> dict:
    """Create a new quality hold record for a job and set the job status to quality_hold."""
    valid_reasons = {"thickness_out_of_spec", "adhesion_failure", "surface_defect", "contamination", "customer_rejection"}
    valid_severities = {"minor", "major", "critical"}

    if hold_reason not in valid_reasons:
        return {"error": f"Invalid hold_reason '{hold_reason}'. Must be one of: {', '.join(sorted(valid_reasons))}"}
    if severity not in valid_severities:
        return {"error": f"Invalid severity '{severity}'. Must be one of: {', '.join(sorted(valid_severities))}"}

    # Find the linked job
    job = next((j for j in _db["jobs"] if j["id"].upper() == job_id.upper()), None)
    if not job:
        return {"error": f"Job '{job_id}' not found."}

    # Generate new hold ID
    existing_ids = [q["id"] for q in _db["quality_holds"]]
    next_num = len(existing_ids) + 1
    new_id = f"QH-{str(next_num).zfill(3)}"

    new_hold = {
        "id": new_id,
        "job_id": job["id"],
        "job_number": job["job_number"],
        "customer_name": job["customer_name"],
        "process_type": job["process_type"],
        "hold_reason": hold_reason,
        "quantity_held": quantity_held,
        "severity": severity,
        "created_date": "2026-10-19",
        "assigned_to": assigned_to,
        "status": "open",
        "disposition": None,
        "notes": notes,
        "resolution": None,
    }

    _db["quality_holds"].append(new_hold)

    # Update job status to quality_hold
    job["status"] = "quality_hold"

    return {
        "success": True,
        "quality_hold": new_hold,
        "job_status_updated_to": "quality_hold",
    }


# ---------------------------------------------------------------------------
# Update Quality Hold
# ---------------------------------------------------------------------------

@mcp.tool()
def update_quality_hold(
    id: str = Field(description="The quality hold ID to update, e.g. QH-001"),
    status: Optional[str] = Field(default=None, description="New status: open | under_review | disposition_pending | resolved"),
    disposition: Optional[str] = Field(default=None, description="Disposition decision: rework | scrap | customer_waiver | accept_as_is"),
    resolution: Optional[str] = Field(default=None, description="Resolution notes describing how the hold was closed"),
) -> dict:
    """Update the status, disposition, and/or resolution of a quality hold."""
    valid_statuses = {"open", "under_review", "disposition_pending", "resolved"}
    valid_dispositions = {"rework", "scrap", "customer_waiver", "accept_as_is"}

    if status and status not in valid_statuses:
        return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(sorted(valid_statuses))}"}
    if disposition and disposition not in valid_dispositions:
        return {"error": f"Invalid disposition '{disposition}'. Must be one of: {', '.join(sorted(valid_dispositions))}"}

    for hold in _db["quality_holds"]:
        if hold["id"].upper() == id.upper():
            if status:
                hold["status"] = status
            if disposition:
                hold["disposition"] = disposition
            if resolution:
                hold["resolution"] = resolution
            return {
                "success": True,
                "id": hold["id"],
                "job_number": hold["job_number"],
                "status": hold["status"],
                "disposition": hold["disposition"],
                "resolution": hold["resolution"],
            }

    return {"error": f"Quality hold '{id}' not found."}


# ---------------------------------------------------------------------------
# Create Quote
# ---------------------------------------------------------------------------

@mcp.tool()
def create_quote(
    customer_id: str = Field(description="Customer ID, e.g. CUST-001"),
    process_type: str = Field(description="Process type: zinc_plating | electroless_nickel | anodizing | powder_coating | chrome_plating | black_oxide | passivation"),
    part_number: str = Field(description="Customer part number"),
    part_description: str = Field(description="Description of the part and finish specification"),
    quantity: int = Field(description="Quantity to be processed"),
    quoted_price_usd: float = Field(description="Total quoted price in USD"),
    cost_estimate_usd: float = Field(description="Estimated internal cost in USD"),
    valid_until: str = Field(description="Quote expiration date (YYYY-MM-DD)"),
    notes: Optional[str] = Field(default=None, description="Optional notes or special requirements"),
) -> dict:
    """Create a new quote for a customer. Returns the created quote record."""
    valid_processes = {"zinc_plating", "electroless_nickel", "anodizing", "powder_coating", "chrome_plating", "black_oxide", "passivation"}
    if process_type not in valid_processes:
        return {"error": f"Invalid process_type '{process_type}'. Must be one of: {', '.join(sorted(valid_processes))}"}

    customer = next((c for c in _db["customers"] if c["id"].upper() == customer_id.upper()), None)
    if not customer:
        return {"error": f"Customer '{customer_id}' not found."}

    # Generate new quote number and ID
    existing_nums = [int(q["quote_number"].split("-")[-1]) for q in _db["quotes"] if q["quote_number"].startswith("QT-2026-")]
    next_num = max(existing_nums) + 1 if existing_nums else 201
    new_id = f"QT-{str(len(_db['quotes']) + 1).zfill(3)}"
    new_number = f"QT-2026-{str(next_num).zfill(4)}"

    margin_pct = round(((quoted_price_usd - cost_estimate_usd) / quoted_price_usd) * 100, 1) if quoted_price_usd else 0.0

    new_quote = {
        "id": new_id,
        "quote_number": new_number,
        "customer_id": customer["id"],
        "customer_name": customer["name"],
        "process_type": process_type,
        "part_number": part_number,
        "part_description": part_description,
        "quantity": quantity,
        "quoted_price_usd": quoted_price_usd,
        "cost_estimate_usd": cost_estimate_usd,
        "margin_pct": margin_pct,
        "status": "draft",
        "valid_until": valid_until,
        "notes": notes or "",
        "created_date": "2026-10-19",
    }

    _db["quotes"].append(new_quote)

    return {
        "success": True,
        "quote": new_quote,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
