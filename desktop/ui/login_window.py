"""
Login Window for Desktop Application

Embeds the actual frontend authentication UI using QWebEngineView.
This ensures 100% visual and functional parity with the web frontend.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from PyQt5.QtWebChannel import QWebChannel
from services.api_client import APIClient
import json


class WebBridge(QWidget):
    """Bridge for communication between web page and desktop app"""
    
    login_successful = pyqtSignal(dict)
    
    @pyqtSlot(str)
    def onAuthSuccess(self, data_str):
        """Called from JavaScript when authentication succeeds"""
        try:
            data = json.loads(data_str)
            self.login_successful.emit(data)
        except Exception as e:
            print(f"Error processing auth data: {e}")
    
    @pyqtSlot(str)
    def logMessage(self, message):
        """Debug logging from web page"""
        print(f"[WebPage]: {message}")


class LoginWindow(QWidget):
    """
    Desktop login window that embeds the frontend authentication page.
    
    This approach ensures:
    - Identical UI/UX to frontend
    - Reuses all frontend components, styles, and logic
    - No code duplication
    - Same authentication flow
    - Same validation and error handling
    """
    
    login_successful = pyqtSignal(object)
    
    def __init__(self, frontend_url="http://localhost:3000"):
        super().__init__()
        self.frontend_url = frontend_url
        self.api_client = APIClient()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the web view that displays frontend authentication"""
        self.setWindowTitle('EquipSense - Authentication')
        self.setMinimumSize(900, 750)
        self.center_window()
        
        # Set up layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create web engine view
        self.web_view = QWebEngineView()
        self.web_page = CustomWebPage()
        self.web_view.setPage(self.web_page)
        
        # Configure web settings for Google OAuth
        self.configure_web_settings()
        
        # Set up web channel for communication with JavaScript
        self.channel = QWebChannel()
        self.bridge = WebBridge()
        self.bridge.login_successful.connect(self.handle_auth_success)
        self.channel.registerObject('desktopBridge', self.bridge)
        self.web_page.setWebChannel(self.channel)
        
        # Load the frontend authentication page
        self.web_view.setUrl(QUrl(self.frontend_url))
        
        # Handle page load finished
        self.web_view.loadFinished.connect(self.on_page_loaded)
        
        layout.addWidget(self.web_view)
        self.setLayout(layout)
    
    def configure_web_settings(self):
        """Configure web engine settings to enable Google OAuth"""
        # Get the profile and settings
        profile = self.web_page.profile()
        settings = self.web_page.settings()
        
        # Enable necessary features for Google OAuth
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, False)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.XSSAuditingEnabled, True)
        settings.setAttribute(QWebEngineSettings.SpatialNavigationEnabled, False)
        settings.setAttribute(QWebEngineSettings.HyperlinkAuditingEnabled, False)
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        
        # Enable local storage path
        profile.setPersistentStoragePath(profile.persistentStoragePath())
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        
        # Set user agent to avoid Google OAuth blocking
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        profile.setHttpUserAgent(user_agent)
        
        print("[WebEngine] Google OAuth support enabled")
        print(f"[WebEngine] User Agent: {profile.httpUserAgent()}")
        print(f"[WebEngine] Persistent Storage: {profile.persistentStoragePath()}")
    
    def center_window(self):
        """Center the window on screen"""
        from PyQt5.QtWidgets import QDesktopWidget
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def on_page_loaded(self, ok):
        """Called when the web page finishes loading"""
        if ok:
            # Inject JavaScript bridge for desktop integration
            self.inject_desktop_bridge()
        else:
            self.show_connection_error()
    
    def inject_desktop_bridge(self):
        """Inject JavaScript to enable desktop-web communication"""
        js_code = """
        (function() {
            // Wait for QWebChannel to be available
            if (typeof QWebChannel === 'undefined') {
                setTimeout(arguments.callee, 100);
                return;
            }
            
            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.desktopBridge = channel.objects.desktopBridge;
                
                // Intercept localStorage to detect authentication
                const originalSetItem = localStorage.setItem;
                localStorage.setItem = function(key, value) {
                    originalSetItem.apply(this, arguments);
                    
                    // Check if auth token was set
                    if (key === 'token' || key === 'access_token' || key === 'auth_token') {
                        try {
                            const userData = {
                                token: value,
                                user: JSON.parse(localStorage.getItem('user') || '{}')
                            };
                            window.desktopBridge.onAuthSuccess(JSON.stringify(userData));
                            window.desktopBridge.logMessage('Authentication detected');
                        } catch (e) {
                            window.desktopBridge.logMessage('Error: ' + e.message);
                        }
                    }
                };
                
                window.desktopBridge.logMessage('Desktop bridge initialized');
            });
        })();
        """
        self.web_page.runJavaScript(js_code)
    
    def handle_auth_success(self, auth_data):
        """Handle successful authentication from web page"""
        try:
            # Store token in API client
            if 'token' in auth_data:
                self.api_client.set_token(auth_data['token'])
            
            # Store user data
            if 'user' in auth_data:
                self.api_client.user = auth_data['user']
            
            # Emit signal and open dashboard
            self.login_successful.emit(auth_data)
            self.open_dashboard()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                'Error',
                f'Authentication succeeded but failed to open dashboard:\n{str(e)}'
            )
    
    def open_dashboard(self):
        """Open the dashboard window"""
        try:
            from ui.dashboard_window import DashboardWindow
            self.dashboard = DashboardWindow(self.api_client)
            self.dashboard.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(
                self,
                'Error',
                f'Could not open dashboard:\n{str(e)}\n\nPlease check that the backend is running.'
            )
    
    def show_connection_error(self):
        """Show error when frontend cannot be loaded"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle('Connection Error')
        msg.setText('Cannot connect to frontend server')
        msg.setInformativeText(
            f'Make sure the frontend is running at:\n{self.frontend_url}\n\n'
            'Run: cd frontend && npm run dev'
        )
        msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Close)
        
        result = msg.exec_()
        if result == QMessageBox.Retry:
            self.web_view.reload()
        else:
            self.close()


class CustomWebPage(QWebEnginePage):
    """Custom web page to handle console messages, popups, and OAuth"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.popup_windows = []
    
    def javaScriptConsoleMessage(self, level, message, line, source):
        """Log JavaScript console messages for debugging"""
        # Filter out noise, show important messages
        if 'error' in message.lower() or 'failed' in message.lower():
            print(f'[JS Error] {message} (line {line})')
        elif 'google' in message.lower() or 'oauth' in message.lower() or 'auth' in message.lower():
            print(f'[JS Auth] {message}')
        else:
            # Debug mode: uncomment to see all console messages
            # print(f'[JS Console] {message} (line {line})')
            pass
    
    def createWindow(self, window_type):
        """Handle popup windows (required for Google OAuth)"""
        print(f"[WebEngine] Creating popup window for OAuth (type: {window_type})")
        
        # Create a new web page for the popup
        popup_page = QWebEnginePage(self.profile(), self)
        popup_view = QWebEngineView()
        popup_view.setPage(popup_page)
        
        # Configure popup settings
        popup_settings = popup_page.settings()
        popup_settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        popup_settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        
        # Show popup window
        popup_view.setWindowTitle("Google Sign In")
        popup_view.resize(500, 600)
        popup_view.show()
        
        # Store reference to prevent garbage collection
        self.popup_windows.append(popup_view)
        
        # Clean up when popup closes
        popup_view.destroyed.connect(lambda: self.popup_windows.remove(popup_view) if popup_view in self.popup_windows else None)
        
        # Return the popup page (Qt will handle showing it)
        return popup_page
    
    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        """Handle navigation - allow frontend routes but detect dashboard access"""
        url_str = url.toString()
        
        # Log navigation for debugging OAuth flow
        if 'google' in url_str.lower() or 'oauth' in url_str.lower():
            print(f"[WebEngine] OAuth navigation: {url_str}")
        
        # Allow navigation within the frontend app
        if '/dashboard' in url_str or '/app' in url_str:
            # User successfully logged in and navigated to dashboard
            # The bridge will handle the token detection
            print(f"[WebEngine] Dashboard access detected: {url_str}")
        
        return True

