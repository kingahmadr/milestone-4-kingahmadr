from email_validator import validate_email, EmailNotValidError
from flask import jsonify

class Validator:
    def email_validation(email_request):
        try:
            # Check that the email address is valid
            emailinfo = validate_email(email_request, check_deliverability=False)

            # Get the normalized form of the email address
            normalized_email = emailinfo.normalized

            # print(f'{normalized_email}')

            return jsonify({"email": normalized_email}), 200

        except EmailNotValidError as e:
            # Handle invalid email input with a specific error message
            # print(str(e))
            return jsonify({"error": "Invalid email", "message": str(e)}), 400