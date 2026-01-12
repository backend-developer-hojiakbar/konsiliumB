"""
Validators for Analysis app.
"""
import re
from django.core.exceptions import ValidationError


def validate_patient_id(value):
    """Validate patient ID format."""
    if not value or not isinstance(value, str):
        raise ValidationError('Patient ID must be a non-empty string.')
    
    if len(value) > 255:
        raise ValidationError('Patient ID must be 255 characters or less.')
    
    # Allow alphanumeric, hyphens, underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', value):
        raise ValidationError('Patient ID can only contain alphanumeric characters, hyphens, and underscores.')


def validate_json_structure(data, required_keys=None, max_size_mb=5):
    """Validate JSON structure and size."""
    import json
    
    if not isinstance(data, dict):
        raise ValidationError('Data must be a dictionary.')
    
    # Check size (approximate)
    json_str = json.dumps(data)
    size_mb = len(json_str.encode('utf-8')) / (1024 * 1024)
    
    if size_mb > max_size_mb:
        raise ValidationError(f'Data size ({size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb} MB).')
    
    # Check required keys
    if required_keys:
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValidationError(f'Missing required keys: {", ".join(missing_keys)}')


def sanitize_text_input(text, max_length=10000):
    """Sanitize text input to prevent XSS and ensure reasonable length."""
    if not isinstance(text, str):
        return ''
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove null bytes and other problematic characters
    text = text.replace('\x00', '')
    
    return text.strip()
