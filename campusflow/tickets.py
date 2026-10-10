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
    if not isinstance(category, str):
        raise ValueError("Category must be a string")

    normalized = category.strip().lower()

    allowed = ["network", "hardware", "software", "other"]

    if normalized not in allowed:
        raise ValueError(
            f"Category must be one of: {allowed}"
        )

    return normalized.capitalize()

def validate_urgency(urgency):
    if not isinstance(urgency, str):
        raise ValueError("Urgency must be a string")

    normalized = urgency.strip().lower()

    if normalized not in ["low", "medium", "high"]:
        raise ValueError(
            "Urgency must be low, medium, or high"
        )

    return normalized
    normalized = urgency.strip().lower()
    if normalized not in ["low", "medium", "high"]:
        return normalized

def validate_affected_users(value):
    if isinstance(value, bool):
        raise ValueError(
            "Affected users must be a positive whole number"
        )

    if isinstance(value, int):
        number = value

    elif isinstance(value, str):
        value = value.strip()

        try:
            number = int(value)
        except ValueError:
            raise ValueError(
                "Affected users must be a whole number"
            )

    else:
        raise ValueError(
            "Affected users must be a whole number"
        )

    if number <= 0:
        raise ValueError(
            "Affected users must be positive"
        )

    return number
        #value arrives as a STRING from input()
    try:
        n = int(value)
    except ValueError:
        raise ValidationError("affected_users must be a whole number")
        if n <= 0:
            raise ValidationError("affected_users must be positive")
            return n 