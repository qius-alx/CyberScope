# src/osint/core/validators.py
import validators

def validate_domain(domain_name: str) -> bool:
    """Validates if the given string is a valid domain name."""
    if not isinstance(domain_name, str):
        return False
    # The validators library considers 'localhost' a valid domain, which might not be desired
    # for an external OSINT tool. We can add a simple check for that.
    if domain_name.lower() == 'localhost':
        return False
    return validators.domain(domain_name) is True

def validate_ip(ip_address: str) -> bool:
    """Validates if the given string is a valid IP address (v4 or v6)."""
    if not isinstance(ip_address, str):
        return False
    return validators.ipv4(ip_address) is True or validators.ipv6(ip_address) is True

def validate_email(email_address: str) -> bool:
    """Validates if the given string is a valid email address."""
    if not isinstance(email_address, str):
        return False
    return validators.email(email_address) is True
