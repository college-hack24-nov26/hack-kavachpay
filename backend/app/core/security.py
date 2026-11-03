import bcrypt
import hmac
import hashlib
import base64
import json
import time
from typing import Optional, Dict, Any
from backend.app.core.config import settings

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_session_token(data: Dict[str, Any], expires_in_seconds: Optional[int] = None) -> str:
    """Creates a signed tamper-proof session token without external jwt dependency issues."""
    if expires_in_seconds is None:
        expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    payload = data.copy()
    payload["exp"] = int(time.time()) + expires_in_seconds
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    encoded_payload = base64.urlsafe_b64encode(payload_bytes).decode('utf-8').rstrip('=')
    
    signature = hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        encoded_payload.encode('utf-8'),
        hashlib.sha256
    ).digest()
    encoded_sig = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    return f"{encoded_payload}.{encoded_sig}"

def verify_session_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies and decodes a signed session token."""
    try:
        parts = token.split('.')
        if len(parts) != 2:
            return None
        
        encoded_payload, encoded_sig = parts
        
        # Verify HMAC
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            encoded_payload.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Pad base64 for decoding
        sig_pad = encoded_sig + '=' * (-len(encoded_sig) % 4)
        received_sig = base64.urlsafe_b64decode(sig_pad)
        
        if not hmac.compare_digest(expected_sig, received_sig):
            return None
            
        payload_pad = encoded_payload + '=' * (-len(encoded_payload) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_pad)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        if payload.get("exp", 0) < time.time():
            return None
            
        return payload
    except Exception:
        return None

