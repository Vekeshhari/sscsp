import hashlib
import hmac
import os

KEY = os.getenv("SIGN_KEY", "demo-signing-key-do-not-use-in-prod").encode()


def sign(data: str) -> str:
    return hmac.new(KEY, data.encode(), hashlib.sha256).hexdigest()


def verify(data: str, signature: str) -> bool:
    return hmac.compare_digest(sign(data), signature)
