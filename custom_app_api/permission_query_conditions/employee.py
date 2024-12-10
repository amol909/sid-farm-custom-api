import frappe

def get_permission_query_conditions(user):
    """
    Adds permission conditions based on employee hierarchy:
    1. Checks if user has an employee record
    2. If yes, returns all employees reporting to this user (direct + indirect reports)
    3. If no, returns default system permissions
    Returns: string - SQL condition
    """

    frappe.msgprint(f"Permission check for user: {user}")
    
    conditions = ["status = 'Active'"]
    
    # Skip for System Manager or Administrator
    if "System Manager" in frappe.get_roles(user) or user == "Administrator":
        return " and ".join(conditions)
    
    # Get employee record for logged-in user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    frappe.msgprint(f"Employee found: {employee}")
    if not employee:
        return " and ".join(conditions)  # Return default permissions if no employee record
    
    # Get all subordinates using MariaDB recursive query
    subordinates_query = """
        WITH RECURSIVE emp_hierarchy AS (
            /* Get direct subordinates first */
            SELECT name, reports_to, 1 as level
            FROM `tabEmployee`
            WHERE reports_to = %(employee)s

            UNION ALL
            
            /* Get subordinates of subordinates */
            SELECT e.name, e.reports_to, eh.level + 1
            FROM `tabEmployee` e
            INNER JOIN emp_hierarchy eh ON e.reports_to = eh.name
        )
        SELECT name FROM emp_hierarchy
    """
    subordinates = frappe.db.sql(subordinates_query, {"employee": employee}, as_dict=1)
    subordinate_names = [employee]  # Include self
    subordinate_names.extend([d.name for d in subordinates])
    
    frappe.msgprint(f"Subordinates: {subordinate_names}")
    
    # Add condition to show only subordinates - Fixed SQL syntax
    if subordinate_names:
        # Simple string join with single quotes
        names_str = "','".join(subordinate_names)
        conditions.append(f"name in ('{names_str}')")
    
    final_condition = " and ".join(conditions)
    frappe.msgprint(f"Final condition: {final_condition}")
    
    return final_condition
