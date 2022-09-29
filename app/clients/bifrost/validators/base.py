from app.exception import AppException
from dataclasses import dataclass

class ValidationResult:
    def __init__(self, is_valid_token, decoded_token, message=""):

        self.is_valid = is_valid_token
        self.token_data = decoded_token
        self.message = message

@dataclass
class TokenSubject:
    platform: str
    brand: str

    def parse(token_data: dict) -> 'TokenSubject':
        subject: str = token_data['sub']

        # example: urn:jarvis:bluehost
        (urn, platform, brand) = subject.split(':')

        if not platform:
            raise AppException(f"missing platform in token subject: {subject}", event="Auth.Token.Subject", status_code=401)
        
        if not brand:
            raise AppException(f"missing brand in token subject: {subject}", event="Auth.Token.Subject", status_code=401)

        return TokenSubject(platform, brand)
