import re
from email_validator import validate_email as email_validate, EmailNotValidError

def validate_email(email):
    """Validate email format"""
    try:
        email_validate(email)
        return True
    except EmailNotValidError:
        return False

def validate_password(password):
    """
    Validate password according to requirements:
    - At least 8 characters long
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False
    
    # Check for at least one digit
    if not any(char.isdigit() for char in password):
        return False
    
    # Check for at least one special character (non-alphanumeric)
    if not any(not char.isalnum() for char in password):
        return False
    
    return True

def validate_country_code(country_code):
    """Validate ISO-3166-1 alpha-2 country code"""
    if not country_code:
        return True  # Allow empty country code
    return bool(re.match(r'^[A-Z]{2}$', country_code))

def validate_rating(rating):
    """Validate rating is between 1 and 10"""
    try:
        rating_int = int(rating)
        return 1 <= rating_int <= 10
    except (ValueError, TypeError):
        return False

def validate_year(year):
    """Validate movie year (must be >= 1888)"""
    try:
        year_int = int(year)
        return year_int >= 1888
    except (ValueError, TypeError):
        return False 