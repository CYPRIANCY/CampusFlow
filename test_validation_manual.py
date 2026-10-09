from campusflow.tickets import validate_title

# Test a valid title
print(validate_title("Wi-Fi is down"))

# Test a title with surrounding spaces
print(validate_title("  Projector is broken  "))

# Try a blank title and observe the error
print(validate_title("   "))