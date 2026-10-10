def find_ticket(tickets, ticket_id, staff_name):
  
    normalized_id = ticket_id.strip().upper()
    found_ticket = None
    for ticket in tickets:
        if ticket["id"] == normalized_id:
            found_ticket = ticket
            break
            
    if not found_ticket:
        raise ValueError("Ticket not found")

   
    clean_name = staff_name.strip()
    if clean_name == "":
        raise ValueError("Staff name cannot be blank")

  
    if found_ticket.get("status") == "resolved":
        raise ValueError("Reopen the ticket before modifying it")

    
    found_ticket["assigned_to"] = clean_name
    return found_ticket
