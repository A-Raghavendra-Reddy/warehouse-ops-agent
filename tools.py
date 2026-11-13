from pathlib import Path
import pandas as pd
from langchain.tools import tool
from knowledge import search

DATA_PATH = Path(__file__).parent / "data" / "inventory.csv"
inventory = pd.read_csv(DATA_PATH)
tickets = []


def severity_for(system_qty, physical_qty):
    missing_pct = (system_qty - physical_qty) / system_qty * 100
    if missing_pct >= 100:
        return "CRITICAL"
    if missing_pct >= 10:
        return "MODERATE"
    return "LOW"


@tool
def get_location_inventory(location: str) -> str:
    """Get all items and quantities at a warehouse location, e.g. 'zone-a', 'zone-b', 'zone-c', 'yard'."""
    rows = inventory[inventory["location"] == location.lower()]
    if rows.empty:
        return f"No location called {location} found."
    return rows.to_string(index=False)


@tool
def find_discrepancies() -> str:
    """Find all items where system quantity does not match physical count,
    with the missing percentage and the official severity for each."""
    mismatched = inventory[inventory["system_qty"] != inventory["physical_qty"]].copy()
    if mismatched.empty:
        return "No discrepancies found."
    mismatched["difference"] = mismatched["physical_qty"] - mismatched["system_qty"]
    mismatched["missing_pct"] = ((mismatched["system_qty"] - mismatched["physical_qty"]) / mismatched["system_qty"] * 100).round(1)
    mismatched["severity"] = mismatched.apply(lambda r: severity_for(r["system_qty"], r["physical_qty"]), axis=1)
    return mismatched.to_string(index=False)


@tool
def create_ticket(asin: str, issue: str, severity: str) -> str:
    """Create an investigation ticket. severity must be LOW, MODERATE or CRITICAL."""
    ticket_id = f"WH-{1000 + len(tickets) + 1}"
    tickets.append({"id": ticket_id, "asin": asin, "issue": issue, "severity": severity})
    return f"Ticket {ticket_id} created for {asin} ({severity}): {issue}"


@tool
def search_sops(query: str) -> str:
    """Search the warehouse standard operating procedures (SOPs).
    Use this for any question about what process to follow or how to handle a situation."""
    docs = search(query)
    if not docs:
        return "No relevant SOP found."
    return "\n\n".join(doc.page_content for doc in docs)
