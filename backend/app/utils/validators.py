from typing import Dict, Any, List

def validate_persona_dict(data: Dict[str, Any]) -> bool:
    """
    Validates that a dictionary representing a persona has all required fields and valid types.
    Returns True if valid, raises ValueError if invalid.
    """
    if not isinstance(data, dict):
        raise ValueError("Persona data must be a dictionary")

    # Name check
    name = data.get("name")
    if not name or not isinstance(name, str) or not name.strip():
        raise ValueError("Persona 'name' is required and must be a non-empty string")

    # Age check
    age = data.get("age")
    if age is None or not isinstance(age, int) or age < 10 or age > 100:
        raise ValueError(f"Persona 'age' must be an integer between 10 and 100. Got {age}")

    # Occupation check
    occupation = data.get("occupation")
    if not occupation or not isinstance(occupation, str) or not occupation.strip():
        raise ValueError("Persona 'occupation' is required and must be a non-empty string")

    # Personality traits check
    traits = data.get("personality_traits")
    if not traits or not isinstance(traits, list) or len(traits) == 0:
        raise ValueError("Persona 'personality_traits' must be a non-empty list of strings")

    # Behavioral patterns check
    behaviors = data.get("behavioral_patterns")
    if not behaviors or not isinstance(behaviors, list) or len(behaviors) == 0:
        raise ValueError("Persona 'behavioral_patterns' must be a non-empty list of strings")

    # Psychological profile check
    psy_profile = data.get("psychological_profile")
    if not psy_profile or not isinstance(psy_profile, dict):
        raise ValueError("Persona 'psychological_profile' must be a non-empty dictionary")

    return True

def validate_personas_list(personas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validates a list of personas. Returns list of valid personas.
    Raises ValueError if list is empty or any persona fails validation.
    """
    if not isinstance(personas, list) or len(personas) == 0:
        raise ValueError("Personas list cannot be empty")
    
    validated = []
    for idx, p in enumerate(personas):
        try:
            validate_persona_dict(p)
            validated.append(p)
        except ValueError as e:
            raise ValueError(f"Persona at index {idx} failed validation: {str(e)}")
            
    return validated
