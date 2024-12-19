import frappe
from frappe.utils import now_datetime

def after_insert(doc, method):
    try:
        # Skip default routes
        if "default" in doc.route_name.lower():
            return

        job_opening = frappe.get_doc({
            "doctype": "Job Opening",
            "job_title": f"Vacancy for {doc.name}",
            "designation": "Delivery Partner",
            "status": "Open",
            "posted_on": now_datetime(),
            "company": "SIDS FARM PRIVATE LIMITED",
            "custom_travel_route": doc.name,
            "location": doc.branch,
            "route": f"jobs/sids_farm_private_limited/{doc.name.lower()}"
        })

        job_opening.insert(ignore_permissions=True)
        frappe.db.commit()

    except Exception as e:
        frappe.log_error(
            message=f"Error creating job opening for new route:\n{frappe.get_traceback()}",
            title=f"New Route Job Opening Creation Error - {doc.name}"
        )
