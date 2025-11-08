"""
Screenshot Protection Module
Prevents screenshots and screen recording on cloud deployments
"""

import streamlit as st


def is_local_environment():
    """Detect if the app is running locally or on cloud"""
    try:
        # Method 1: Check environment variable (most reliable)
        import os
        env_mode = os.environ.get('STREAMLIT_ENV', '').lower()
        if env_mode == 'local' or env_mode == 'development':
            return True
        
        # Method 2: Check Streamlit server address
        try:
            import streamlit.web.bootstrap as bootstrap
            # If server is bound to localhost/127.0.0.1, it's local
            server_address = os.environ.get('STREAMLIT_SERVER_ADDRESS', 'localhost')
            if server_address in ['localhost', '127.0.0.1', '0.0.0.0']:
                return True
        except:
            pass
        
        # Method 3: Check hostname
        import socket
        hostname = socket.gethostname().lower()
        
        # Local indicators in hostname
        local_keywords = ['local', 'desktop', 'laptop', 'macbook', 'imac', 'pc-', 'home']
        if any(keyword in hostname for keyword in local_keywords):
            return True
        
        # Method 4: Check if running on standard local ports
        try:
            port = os.environ.get('STREAMLIT_SERVER_PORT', '8501')
            # Standard local development ports
            if port in ['8501', '8502', '8503', '8504']:
                return True
        except:
            pass
            
        # Default to False (cloud) for security
        return False
    except:
        # Default to False (cloud) if detection fails for security
        return False


def apply_screenshot_protection():
    """Apply screenshot protection CSS and JavaScript for cloud deployments"""
    
    is_local = is_local_environment()
    
    if is_local:
        # Local environment - no screenshot protection
        st.markdown("""
        <style>
            /* Local environment - screenshots allowed */
            body::before {
                content: '🏠 Local Development Mode';
                position: fixed;
                bottom: 10px;
                right: 10px;
                background: rgba(0, 255, 0, 0.2);
                color: #00ff00;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 0.7rem;
                z-index: 999999;
                pointer-events: none;
            }
        </style>
        """, unsafe_allow_html=True)
        return "local"
    
    else:
        # Cloud environment - apply protection
        st.markdown("""
        <style>
            /* Prevent text selection and copying */
            * {
                -webkit-user-select: none !important;
                -moz-user-select: none !important;
                -ms-user-select: none !important;
                user-select: none !important;
            }
            
            /* Disable right-click */
            body {
                -webkit-touch-callout: none !important;
            }
            
            /* Add watermark overlay */
            body::after {
                content: 'CONFIDENTIAL - NSE Stock Dashboard';
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) rotate(-45deg);
                font-size: 4rem;
                color: rgba(255, 255, 255, 0.05);
                pointer-events: none;
                z-index: 999999;
                white-space: nowrap;
            }
            
            /* Cloud indicator */
            body::before {
                content: '☁️ Cloud Mode - Protected';
                position: fixed;
                bottom: 10px;
                right: 10px;
                background: rgba(255, 68, 68, 0.2);
                color: #ff4444;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 0.7rem;
                z-index: 999999;
                pointer-events: none;
            }
            
            /* Blur effect when window loses focus (screenshot attempt detection) */
            body.blurred {
                filter: blur(10px);
            }
        </style>
        
        <script>
            // Disable right-click
            document.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                return false;
            });
            
            // Detect common screenshot shortcuts
            document.addEventListener('keydown', function(e) {
                // Windows: PrtScn, Alt+PrtScn, Win+Shift+S
                // Mac: Cmd+Shift+3, Cmd+Shift+4, Cmd+Shift+5
                
                // Print Screen detection
                if (e.key === 'PrintScreen') {
                    e.preventDefault();
                    alert('Screenshots are disabled on cloud deployment for security reasons.');
                    return false;
                }
                
                // Mac screenshot shortcuts
                if (e.metaKey && e.shiftKey && (e.key === '3' || e.key === '4' || e.key === '5')) {
                    e.preventDefault();
                    alert('Screenshots are disabled on cloud deployment for security reasons.');
                    return false;
                }
                
                // Windows Snipping Tool (Win+Shift+S)
                if (e.metaKey && e.shiftKey && e.key === 's') {
                    e.preventDefault();
                    alert('Screenshots are disabled on cloud deployment for security reasons.');
                    return false;
                }
                
                // Disable Ctrl+P (Print)
                if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
                    e.preventDefault();
                    alert('Printing is disabled on cloud deployment.');
                    return false;
                }
                
                // Disable F12 (DevTools)
                if (e.key === 'F12') {
                    e.preventDefault();
                    return false;
                }
                
                // Disable Ctrl+Shift+I (DevTools)
                if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'I') {
                    e.preventDefault();
                    return false;
                }
            });
            
            // Detect when page loses focus (possible screenshot attempt)
            let blurTimeout;
            document.addEventListener('visibilitychange', function() {
                if (document.hidden) {
                    // Page is hidden - possible screenshot
                    document.body.classList.add('blurred');
                    blurTimeout = setTimeout(function() {
                        document.body.classList.remove('blurred');
                    }, 2000);
                } else {
                    // Page is visible again
                    clearTimeout(blurTimeout);
                    document.body.classList.remove('blurred');
                }
            });
            
            // Detect blur event (Alt+Tab, screenshot tools)
            window.addEventListener('blur', function() {
                document.body.classList.add('blurred');
                setTimeout(function() {
                    document.body.classList.remove('blurred');
                }, 2000);
            });
            
            window.addEventListener('focus', function() {
                document.body.classList.remove('blurred');
            });
            
            // Console warning
            console.log('%c⚠️ WARNING', 'color: red; font-size: 20px; font-weight: bold;');
            console.log('%cScreenshots and recording are disabled on this platform for security reasons.', 'color: orange; font-size: 14px;');
            console.log('%cUnauthorized capture of data may violate terms of service.', 'color: orange; font-size: 14px;');
        </script>
        """, unsafe_allow_html=True)
        return "cloud"


def apply_lite_screenshot_protection():
    """Apply lighter screenshot protection (watermark only, no blocking)"""
    
    is_local = is_local_environment()
    
    if not is_local:
        # Only add watermark on cloud
        st.markdown("""
        <style>
            /* Subtle watermark overlay */
            body::after {
                content: 'NSE Dashboard - Confidential';
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) rotate(-45deg);
                font-size: 3rem;
                color: rgba(255, 255, 255, 0.03);
                pointer-events: none;
                z-index: 999999;
                white-space: nowrap;
            }
        </style>
        """, unsafe_allow_html=True)
