"""
WebView Container Window

Main window that embeds the frontend UI and provides menu access to native analytics.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMenuBar, QAction,
    QMessageBox, QLabel, QStatusBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont
from ui.login_window import LoginWindow
from ui.analytics_window import AnalyticsWindow
from services.auth_session_handler import get_session


class WebViewContainer(QMainWindow):
    """
    Main container window for the hybrid desktop application.
    
    Features:
    - Embeds frontend UI via QWebEngineView
    - Provides menu bar for native features
    - Manages navigation between web and native modules
    - Handles authentication session
    """
    
    def __init__(self):
        super().__init__()
        self.session = get_session()
        self.login_window = None
        self.analytics_window = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the main window UI"""
        self.setWindowTitle('EquipSense Desktop')
        self.setMinimumSize(1000, 750)
        self.center_window()
        
        # Apply window stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            QMenuBar {
                background: #1f2937;
                color: white;
                padding: 5px;
                font-size: 13px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: #374151;
            }
            QMenu {
                background: #1f2937;
                color: white;
                border: 1px solid #374151;
            }
            QMenu::item:selected {
                background: #3b82f6;
            }
            QStatusBar {
                background: #1f2937;
                color: white;
                font-size: 12px;
            }
        """)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("Ready")
        
        # Central widget - will hold the login window initially
        self.show_login_window()
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('File')
        
        open_analytics_action = QAction('📊 Open Native Analytics', self)
        open_analytics_action.setStatusTip('Open native CSV analytics module')
        open_analytics_action.triggered.connect(self.open_analytics)
        file_menu.addAction(open_analytics_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View Menu
        view_menu = menubar.addMenu('View')
        
        reload_action = QAction('🔄 Reload Frontend', self)
        reload_action.setStatusTip('Reload the frontend UI')
        reload_action.triggered.connect(self.reload_frontend)
        view_menu.addAction(reload_action)
        
        fullscreen_action = QAction('Fullscreen', self)
        fullscreen_action.setStatusTip('Toggle fullscreen mode')
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Session Menu
        session_menu = menubar.addMenu('Session')
        
        session_info_action = QAction('Session Info', self)
        session_info_action.setStatusTip('View session information')
        session_info_action.triggered.connect(self.show_session_info)
        session_menu.addAction(session_info_action)
        
        logout_action = QAction('Logout', self)
        logout_action.setStatusTip('Logout and return to login')
        logout_action.triggered.connect(self.logout)
        session_menu.addAction(logout_action)
        
        # Help Menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.setStatusTip('About EquipSense')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        docs_action = QAction('Documentation', self)
        docs_action.setStatusTip('Open documentation')
        docs_action.triggered.connect(self.open_documentation)
        help_menu.addAction(docs_action)
    
    def show_login_window(self):
        """Show login window with embedded frontend"""
        if self.login_window is None:
            self.login_window = LoginWindow()
            self.login_window.login_successful.connect(self.on_login_success)
        
        # Set as central widget
        self.setCentralWidget(self.login_window)
        self.update_status("Please login to continue")
    
    def on_login_success(self, auth_data):
        """Handle successful login"""
        # Update session
        self.session.set_authenticated(auth_data)
        self.update_status(f"Logged in as {self.session.get_username()}")
        
        QMessageBox.information(
            self,
            "Login Successful",
            f"Welcome, {self.session.get_username()}!\n\n"
            "You can now:\n"
            "• Use the web dashboard\n"
            "• Access native analytics (File → Open Native Analytics)"
        )
    
    def open_analytics(self):
        """Open native analytics window"""
        # Check authentication
        if not self.session.is_authenticated():
            reply = QMessageBox.question(
                self,
                "Authentication Required",
                "You must be logged in to access analytics.\n\n"
                "Would you like to login now?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.show_login_window()
            return
        
        # Create or show analytics window
        if self.analytics_window is None or not self.analytics_window.isVisible():
            self.analytics_window = AnalyticsWindow(self.session)
            self.analytics_window.show()
            self.update_status("Native analytics module opened")
        else:
            self.analytics_window.activateWindow()
            self.analytics_window.raise_()
    
    def reload_frontend(self):
        """Reload the frontend web view"""
        if self.login_window and hasattr(self.login_window, 'web_view'):
            self.login_window.web_view.reload()
            self.update_status("Frontend reloaded")
    
    def toggle_fullscreen(self, checked):
        """Toggle fullscreen mode"""
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()
    
    def show_session_info(self):
        """Display session information"""
        info = self.session.get_session_info()
        
        message = f"""
        <h3>Session Information</h3>
        <table style="width:100%; border-collapse: collapse;">
            <tr><td><b>Status:</b></td><td>{'🟢 Authenticated' if info['authenticated'] else '🔴 Not Authenticated'}</td></tr>
            <tr><td><b>Username:</b></td><td>{info['username'] or 'N/A'}</td></tr>
            <tr><td><b>Email:</b></td><td>{info['email'] or 'N/A'}</td></tr>
            <tr><td><b>User ID:</b></td><td>{info['user_id'] or 'N/A'}</td></tr>
            <tr><td><b>Access Token:</b></td><td>{'✓ Present' if info['has_access_token'] else '✗ Missing'}</td></tr>
            <tr><td><b>Refresh Token:</b></td><td>{'✓ Present' if info['has_refresh_token'] else '✗ Missing'}</td></tr>
        </table>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Session Information")
        msg.setTextFormat(Qt.RichText)
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def logout(self):
        """Logout user"""
        if not self.session.is_authenticated():
            QMessageBox.information(self, "Info", "You are not logged in.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.session.clear_session()
            
            # Close analytics if open
            if self.analytics_window:
                self.analytics_window.close()
                self.analytics_window = None
            
            # Return to login
            self.show_login_window()
            self.update_status("Logged out")
            
            QMessageBox.information(self, "Logged Out", "You have been logged out successfully.")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>⚗️ EquipSense Desktop</h2>
        <p><b>Version:</b> 2.0.0 (Hybrid Architecture)</p>
        <p><b>Description:</b> Chemical Equipment Parameter Visualizer</p>
        <br>
        <p><b>Features:</b></p>
        <ul>
            <li>✓ Web-based authentication and dashboard</li>
            <li>✓ Native CSV analytics with Matplotlib</li>
            <li>✓ Real-time data visualization</li>
            <li>✓ Statistical analysis</li>
        </ul>
        <br>
        <p><b>Technology Stack:</b></p>
        <ul>
            <li>PyQt5 + QtWebEngine</li>
            <li>React Frontend</li>
            <li>Django REST API</li>
            <li>Matplotlib + Pandas</li>
        </ul>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("About EquipSense")
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def open_documentation(self):
        """Open documentation"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Documentation")
        msg.setText(
            "📚 Documentation\n\n"
            "Please refer to:\n"
            "• README.md\n"
            "• DESKTOP_WEB_INTEGRATION.md\n"
            "• docs/QUICKSTART.md\n\n"
            "For complete setup and usage instructions."
        )
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.showMessage(message)
    
    def center_window(self):
        """Center window on screen"""
        from PyQt5.QtWidgets import QDesktopWidget
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            "ConfirmExit",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clean up
            if self.analytics_window:
                self.analytics_window.close()
            event.accept()
        else:
            event.ignore()
