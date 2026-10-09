def calculate_priority(urgency, affected_users):
    if urgency == "high" and affected_users >= 10:
        return "critical"
    elif urgency == "high" or affected_users >= 10:
        return "high"
    elif urgency == "medium" or affected_users >= 3:
        return "medium"
    else:
        return "low"


def validate_title(title):
    if not isinstance(title, str):
        raise ValueError("Title must be a string")

    title = title.strip()

    if not title:
        raise ValueError("Title cannot be blank")

    return title

def validate_category(category):
    normalized = category.strip().lower()
    allowed = ["network", "hardware", "software", "other"]
    if normalized not in allowed:
        raise ValidationError(f"Category must be one of {allowed}")
    return normalized.capitalize() #save as "Network"

def validate_urgency(urgency):
        normalized = urgency.strip().lower()
        if normalized not in ["low", "medium", "high"]:
            return normalized

def validate_affected_users(value):
        #value arrives as a STRING from input()
        try:
            n = int(value)
        except ValueError:
                raise ValidationError("affected_users must be a whole number")
                if n <= 0:
                    raise ValidationError("affected_users must be positive")
                return n 