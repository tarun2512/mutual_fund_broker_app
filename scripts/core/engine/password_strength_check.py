import re

from scripts.logging import logger


def validate_password_strength(password):
    """
    This method is to validate the password strength
    """
    try:
        logger.info("Validate password strength")

        conditions = [
            len(password) > 7,
            len(password) < 65,
            re.search("[a-z]", password) is not None,
            re.search(r"\d", password) is not None,
            re.search("[A-Z]", password) is not None,
            re.search("[!@#$%^&*]", password) is not None,
            not re.search("\\s", password),
        ]

        password_validation_status = all(conditions)
    except Exception as e:
        logger.error(
            f"Error occurred while validating the password strength : {str(e)}"
        )
        password_validation_status = False

    return password_validation_status
