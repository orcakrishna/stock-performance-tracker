"""
Security Enhancement Functions
Quick fixes for identified security vulnerabilities
"""

import html
import secrets
import hmac
import hashlib
from datetime import datetime, timedelta
import streamlit as st


# =====================================================
# FIX 1: HTML Sanitization (XSS Prevention)
# =====================================================

def sanitize_html(text):
    """
    Escape HTML characters to prevent XSS attacks.
    Use this when displaying any user-provided data with unsafe_allow_html=True
    
    Example:
        safe_name = sanitize_html(user_input)
        st.markdown(f"<div>{safe_name}</div>", unsafe_allow_html=True)
    """
    if text is None:
        return ""
    return html.escape(str(text))


def sanitize_dict_for_html(data_dict):
    """
    Sanitize all string values in a dictionary for HTML display
    
    Example:
        safe_data = sanitize_dict_for_html(stock_data)
    """
    return {
        key: sanitize_html(value) if isinstance(value, str) else value
        for key, value in data_dict.items()
    }


# =====================================================
# FIX 2: Timing-Safe Password Comparison
# =====================================================

def secure_password_compare(input_password, stored_password):
    """
    Timing-safe password comparison to prevent timing attacks.
    Use this instead of direct string comparison (==)
    
    Example:
        if secure_password_compare(pwd, ADMIN_PASSWORD):
            # Grant access
    """
    if not input_password or not stored_password:
        return False
    return secrets.compare_digest(input_password.strip(), stored_password.strip())


# =====================================================
# FIX 3: Rate Limiting for Login Attempts
# =====================================================

class LoginRateLimiter:
    """
    Rate limiter for admin login to prevent brute force attacks
    
    Usage:
        limiter = LoginRateLimiter()
        
        if limiter.is_locked_out():
            st.error("Too many failed attempts. Try again later.")
            return
        
        if password_correct:
            limiter.reset()
        else:
            limiter.record_failure()
    """
    
    def __init__(self, max_attempts=5, lockout_minutes=15):
        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes
        
        # Initialize session state
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0
        if 'lockout_until' not in st.session_state:
            st.session_state.lockout_until = None
        if 'last_attempt_ip' not in st.session_state:
            st.session_state.last_attempt_ip = None
    
    def is_locked_out(self):
        """Check if account is currently locked out"""
        if st.session_state.lockout_until:
            if datetime.now() < st.session_state.lockout_until:
                remaining = (st.session_state.lockout_until - datetime.now()).seconds // 60
                return True, remaining
            else:
                # Lockout expired, reset
                st.session_state.lockout_until = None
                st.session_state.login_attempts = 0
        return False, 0
    
    def record_failure(self):
        """Record a failed login attempt"""
        st.session_state.login_attempts += 1
        
        if st.session_state.login_attempts >= self.max_attempts:
            st.session_state.lockout_until = datetime.now() + timedelta(minutes=self.lockout_minutes)
            return True  # Now locked out
        return False
    
    def reset(self):
        """Reset login attempts after successful login"""
        st.session_state.login_attempts = 0
        st.session_state.lockout_until = None
    
    def get_remaining_attempts(self):
        """Get number of remaining login attempts"""
        return max(0, self.max_attempts - st.session_state.login_attempts)


# =====================================================
# FIX 4: CSV Formula Injection Prevention
# =====================================================

def sanitize_csv_field(field):
    """
    Prevent CSV formula injection by escaping dangerous characters.
    Excel/Sheets interpret =, +, -, @, \t, \r as formula starts.
    
    IMPORTANT: Negative numbers are safe and should NOT be escaped.
    
    Example:
        df = df.applymap(sanitize_csv_field)
        csv_data = df.to_csv(index=False)
    """
    field_str = str(field)
    
    # Empty field is safe
    if not field_str:
        return field
    
    first_char = field_str[0]
    
    # Check if field starts with dangerous characters
    if first_char in ('=', '+', '-', '@', '\t', '\r'):
        # EXCEPTION: Negative numbers are safe (e.g., "-0.4", "-123.45")
        if first_char == '-':
            # Try to parse as number
            try:
                float(field_str)
                return field  # It's a valid negative number, safe!
            except (ValueError, TypeError):
                # Not a number, could be formula like "-1+1"
                pass
        
        # Prefix with single quote to force text interpretation
        return "'" + field_str
    
    return field


def sanitize_dataframe_for_csv(df):
    """
    Sanitize entire DataFrame before CSV export
    
    Example:
        safe_df = sanitize_dataframe_for_csv(export_df)
        csv_data = safe_df.to_csv(index=False)
    """
    # Use map() for pandas 2.0+ (applymap is deprecated)
    try:
        return df.map(sanitize_csv_field)
    except AttributeError:
        # Fallback for older pandas versions
        return df.applymap(sanitize_csv_field)


# =====================================================
# FIX 5: Pickle Integrity Checks
# =====================================================

def create_pickle_with_integrity(data, secret_key):
    """
    Create a pickle with HMAC signature for integrity verification
    
    Args:
        data: Data to pickle
        secret_key: Secret key for HMAC (should be from environment variable)
    
    Returns:
        bytes: Signed pickle data (signature + pickled_data)
    """
    import pickle
    
    # Serialize data
    pickled_data = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    
    # Create HMAC signature
    signature = hmac.new(
        secret_key.encode() if isinstance(secret_key, str) else secret_key,
        pickled_data,
        hashlib.sha256
    ).digest()
    
    # Return signature + data
    return signature + pickled_data


def load_pickle_with_integrity(data, secret_key):
    """
    Load and verify pickle integrity using HMAC
    
    Args:
        data: Signed pickle data (signature + pickled_data)
        secret_key: Secret key for HMAC verification
    
    Returns:
        Unpickled data if signature is valid
    
    Raises:
        ValueError: If signature verification fails
    """
    import pickle
    
    # Extract signature and data (SHA256 = 32 bytes)
    signature = data[:32]
    pickled_data = data[32:]
    
    # Verify signature
    expected_signature = hmac.new(
        secret_key.encode() if isinstance(secret_key, str) else secret_key,
        pickled_data,
        hashlib.sha256
    ).digest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("Cache integrity check failed! Data may be corrupted or tampered with.")
    
    # Signature valid, unpickle data
    return pickle.loads(pickled_data)


# =====================================================
# FIX 6: Secure Configuration Helper
# =====================================================

def get_secure_config(key, default=None, required=False):
    """
    Securely load configuration from environment/secrets
    
    Args:
        key: Configuration key name
        default: Default value if not found
        required: If True, raises error if not found
    
    Returns:
        Configuration value
    """
    import os
    
    # Try environment variable first
    value = os.environ.get(key)
    if value:
        return value.strip()
    
    # Try Streamlit secrets
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key].strip()
    except Exception:
        pass
    
    # Not found
    if required:
        raise ValueError(f"Required configuration '{key}' not found in environment or secrets")
    
    return default


# =====================================================
# USAGE EXAMPLES
# =====================================================

"""
EXAMPLE 1: Update Admin Login in app.py

# Old code (line 250-258):
pwd = st.text_input("Password", type="password", key="admin_pass_input")
if st.button("Login", key="admin_login_btn"):
    if pwd == ADMIN_PASSWORD:
        st.session_state.admin_authenticated = True
        st.session_state.admin_mode = True
        st.success("Admin access granted!")
        trigger_rerun()
    else:
        st.error("Incorrect password")

# New secure code:
from security_fixes import secure_password_compare, LoginRateLimiter

limiter = LoginRateLimiter(max_attempts=5, lockout_minutes=15)

# Check lockout status
is_locked, remaining_mins = limiter.is_locked_out()
if is_locked:
    st.error(f"🔒 Too many failed attempts. Try again in {remaining_mins} minutes.")
else:
    pwd = st.text_input("Password", type="password", key="admin_pass_input")
    remaining = limiter.get_remaining_attempts()
    if remaining < 5:
        st.warning(f"⚠️ {remaining} attempts remaining before lockout")
    
    if st.button("Login", key="admin_login_btn"):
        if secure_password_compare(pwd, ADMIN_PASSWORD):
            limiter.reset()
            st.session_state.admin_authenticated = True
            st.session_state.admin_mode = True
            st.success("Admin access granted!")
            trigger_rerun()
        else:
            if limiter.record_failure():
                st.error("🔒 Account locked for 15 minutes due to failed attempts")
            else:
                st.error("Incorrect password")


EXAMPLE 2: Sanitize HTML Output in ui_components.py

# Old code:
st.markdown(f"<div>{stock_name}</div>", unsafe_allow_html=True)

# New secure code:
from security_fixes import sanitize_html

safe_name = sanitize_html(stock_name)
st.markdown(f"<div>{safe_name}</div>", unsafe_allow_html=True)


EXAMPLE 3: Secure CSV Export in app.py

# Old code (line 502-503):
export_df = filtered_df.drop(columns=["Ticker", "sparkline_data"], errors="ignore")
csv_data = export_df.to_csv(index=False).encode('utf-8')

# New secure code:
from security_fixes import sanitize_dataframe_for_csv

export_df = filtered_df.drop(columns=["Ticker", "sparkline_data"], errors="ignore")
safe_df = sanitize_dataframe_for_csv(export_df)
csv_data = safe_df.to_csv(index=False).encode('utf-8')


EXAMPLE 4: Use Pickle with Integrity in cache_manager.py

# Add at top:
from security_fixes import create_pickle_with_integrity, load_pickle_with_integrity, get_secure_config

# Get signing key (add to .env: CACHE_SIGNING_KEY=your-random-secret-key)
CACHE_SIGNING_KEY = get_secure_config('CACHE_SIGNING_KEY', 'default-dev-key-change-in-prod')

# Update _save_cache_file() function (line 249-255):
def _save_cache_file(cache_data: dict) -> None:
    ensure_cache_dir()
    cache_data['version'] = CACHE_VERSION
    
    with open(CACHE_FILE, 'wb') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            signed_data = create_pickle_with_integrity(cache_data, CACHE_SIGNING_KEY)
            f.write(signed_data)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

# Update _load_cache_file() function (line 221-235):
def _load_cache_file() -> dict:
    default_cache = {
        'version': CACHE_VERSION,
        'stocks': {},
        'last_updated': datetime.now(UTC)
    }
    
    if not os.path.exists(CACHE_FILE):
        return default_cache
    
    try:
        with open(CACHE_FILE, 'rb') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                signed_data = f.read()
                data = load_pickle_with_integrity(signed_data, CACHE_SIGNING_KEY)
                
                if data.get('version', 1) != CACHE_VERSION:
                    print(f"WARNING: Cache version mismatch. Resetting cache.")
                    return default_cache
                
                return data
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except ValueError as e:
        print(f"ERROR: Cache integrity check failed: {e}")
        print("Resetting cache for security.")
        return default_cache
    except Exception as e:
        print(f"ERROR: Failed to load cache: {e}")
        return default_cache
"""


# =====================================================
# RECOMMENDED .env ADDITIONS
# =====================================================

"""
Add to .env file:

# Security
ADMIN_PASSWORD=your-secure-password-here
CACHE_SIGNING_KEY=your-random-secret-key-minimum-32-chars

# Optional: Session security
SESSION_SECRET_KEY=another-random-secret-for-sessions
"""
