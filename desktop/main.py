"""
Chemical Equipment Visualizer - Desktop Application (Hybrid Architecture)
Main Entry Point

This desktop app uses a hybrid approach:
- Web UI: Embeds React frontend for authentication and dashboard
- Native UI: PyQt5 + Matplotlib for CSV analytics module

Requires PyQtWebEngine to display web content.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# Check for PyQtWebEngine
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
except ImportError:
    print("ERROR: PyQtWebEngine is not installed!")
    print("\nPlease install it by running:")
    print("  cd desktop")
    print("  pip install PyQtWebEngine==5.15.6")
    print("\nOr run the installation script:")
    print("  .\\install_webengine.ps1")
    sys.exit(1)

from ui.webview_container import WebViewContainer


def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Chemical Equipment Visualizer")
    app.setOrganizationName("EquipSense")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Display startup information
    print("=" * 60)
    print("🧪 EquipSense Desktop Application (Hybrid Architecture)")
    print("=" * 60)
    print("\n⚠️  IMPORTANT: Make sure these services are running:\n")
    print("  1. Backend API:  http://localhost:8000")
    print("     → cd backend && python manage.py runserver\n")
    print("  2. OTP Service:  http://localhost:3001")
    print("     → cd otp_service && npm start\n")
    print("  3. Frontend UI:  http://localhost:3000")
    print("     → cd frontend && npm run dev\n")
    print("=" * 60)
    print("\n📋 Application Features:")
    print("  • Web UI: Embedded React frontend for auth & dashboard")
    print("  • Native UI: PyQt5 + Matplotlib for CSV analytics")
    print("  • Menu: File → Open Native Analytics (after login)\n")
    print("=" * 60)
    print("\nStarting desktop application...")
    print("Loading main window with embedded frontend...\n")
    
    # Show main container window
    try:
        main_window = WebViewContainer()
        main_window.show()
    except Exception as e:
        print(f"\nERROR: Failed to create main window: {e}")
        import traceback
        traceback.print_exc()
        QMessageBox.critical(
            None,
            "Startup Error",
            f"Failed to start application:\n\n{str(e)}\n\n"
            "Make sure:\n"
            "1. PyQtWebEngine is installed\n"
            "2. Frontend is running at http://localhost:3000\n"
            "3. Backend is running at http://localhost:8000\n"
            "4. All dependencies are installed (pip install -r requirements.txt)"
        )
        sys.exit(1)
    
    # Run application
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
