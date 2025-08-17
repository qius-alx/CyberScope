# tests/test_core/test_validators.py
import pytest
from osint.core.validators import validate_domain, validate_ip, validate_email

@pytest.mark.parametrize("domain, expected", [
    ("example.com", True),
    ("sub.example.co.uk", True),
    ("example.io", True),
    ("a-domain.net", True),
    ("123.com", True),
    ("not a domain", False),
    ("example-.com", False),
    ("-example.com", False),
    ("example.com-", False),
    ("localhost", False), # Custom rule
    (None, False),
    (123, False),
])
def test_validate_domain(domain, expected):
    assert validate_domain(domain) == expected

@pytest.mark.parametrize("ip, expected", [
    ("8.8.8.8", True),
    ("192.168.1.1", True),
    ("2001:0db8:85a3:0000:0000:8a2e:0370:7334", True),
    ("::1", True),
    ("256.0.0.1", False),
    ("not an ip", False),
    ("8.8.8", False),
    (None, False),
])
def test_validate_ip(ip, expected):
    assert validate_ip(ip) == expected

@pytest.mark.parametrize("email, expected", [
    ("test@example.com", True),
    ("user.name+tag@gmail.com", True),
    ("test@sub.domain.co.uk", True),
    ("not-an-email", False),
    ("test@.com", False),
    ("test@domain", False),
    ("@domain.com", False),
    (None, False),
])
def test_validate_email(email, expected):
    assert validate_email(email) == expected
