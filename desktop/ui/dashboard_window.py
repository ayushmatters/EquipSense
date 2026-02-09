"""
Dashboard Window for Desktop Application

Main application window showing equipment data and analytics.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
                             QFileDialog, QTabWidget, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from charts.matplotlib_charts import PieChartCanvas, BarChartCanvas, LineChartCanvas


class DataFetchThread(QThread):
    """Thread for fetching data from API"""
    data_fetched = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
    
    def run(self):
        try:
            summary = self.api_client.get_summary()
            type_dist = self.api_client.get_type_distribution()
            history = self.api_client.get_history()
            
            data = {
                'summary': summary,
                'type_distribution': type_dist.get('type_distribution', {}),
                'history': history
            }
            self.data_fetched.emit(data)
        except Exception as e:
            self.error_occurred.emit(str(e))


class DashboardWindow(QMainWindow):
    """Main dashboard window"""
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('EquipSense - Dashboard')
        self.setGeometry(100, 100, 1400, 900)
        
        # Set modern style
        self.setStyleSheet("""
            QMainWindow {
                background: #f0f2f5;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5568d3, stop:1 #6c3e8c);
            }
            QTableWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            QFrame {
                background: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel('⚗️ Dashboard')
        title_font = QFont('Segoe UI', 24, QFont.Bold)
        title_label.setFont(title_font)
        
        # Action buttons
        upload_btn = QPushButton('📤 Upload CSV')
        upload_btn.clicked.connect(self.open_upload_dialog)
        
        history_btn = QPushButton('📜 History')
        history_btn.clicked.connect(self.show_history)
        
        refresh_btn = QPushButton('🔄 Refresh')
        refresh_btn.clicked.connect(self.load_data)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(upload_btn)
        header_layout.addWidget(history_btn)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Statistics cards
        self.stats_layout = QHBoxLayout()
        self.create_stats_cards()
        main_layout.addLayout(self.stats_layout)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Charts tab
        charts_tab = QWidget()
        charts_layout = QHBoxLayout()
        
        self.pie_chart = PieChartCanvas(self, width=6, height=4)
        self.bar_chart = BarChartCanvas(self, width=6, height=4)
        
        charts_layout.addWidget(self.pie_chart)
        charts_layout.addWidget(self.bar_chart)
        charts_tab.setLayout(charts_layout)
        
        # Data table tab
        table_tab = QWidget()
        table_layout = QVBoxLayout()
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(['Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'])
        self.data_table.horizontalHeader().setStretchLastSection(True)
        
        table_layout.addWidget(self.data_table)
        table_tab.setLayout(table_layout)
        
        # Line chart tab
        line_tab = QWidget()
        line_layout = QVBoxLayout()
        
        self.line_chart = LineChartCanvas(self, width=10, height=6)
        line_layout.addWidget(self.line_chart)
        line_tab.setLayout(line_layout)
        
        self.tab_widget.addTab(charts_tab, 'Charts')
        self.tab_widget.addTab(table_tab, 'Data Table')
        self.tab_widget.addTab(line_tab, 'Trends')
        
        main_layout.addWidget(self.tab_widget)
        
        central_widget.setLayout(main_layout)
    
    def create_stats_cards(self):
        """Create statistics summary cards"""
        self.stats_cards = []
        
        stats = [
            ('Total Equipment', '0', '#3b82f6'),
            ('Avg Flowrate', '0.00', '#a855f7'),
            ('Avg Pressure', '0.00', '#ec4899'),
            ('Avg Temperature', '0.00', '#f97316')
        ]
        
        for title, value, color in stats:
            card = QFrame()
            card.setFixedHeight(120)
            card.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border-left: 5px solid {color};
                    border-radius: 10px;
                    padding: 15px;
                }}
            """)
            
            card_layout = QVBoxLayout()
            
            title_label = QLabel(title)
            title_label.setStyleSheet('color: #666; font-size: 12px;')
            
            value_label = QLabel(value)
            value_label.setStyleSheet(f'color: {color}; font-size: 32px; font-weight: bold;')
            
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            card_layout.addStretch()
            
            card.setLayout(card_layout)
            self.stats_layout.addWidget(card)
            self.stats_cards.append((card, value_label))
    
    def load_data(self):
        """Load data from API"""
        self.thread = DataFetchThread(self.api_client)
        self.thread.data_fetched.connect(self.update_ui)
        self.thread.error_occurred.connect(self.show_error)
        self.thread.start()
    
    def update_ui(self, data):
        """Update UI with fetched data"""
        summary = data['summary']
        stats = summary.get('statistics', {})
        equipment_list = summary.get('equipment_list', [])
        type_distribution = data['type_distribution']
        
        # Update statistics cards
        if self.stats_cards:
            self.stats_cards[0][1].setText(str(stats.get('total_equipment', 0)))
            self.stats_cards[1][1].setText(f"{stats.get('avg_flowrate', 0):.2f}")
            self.stats_cards[2][1].setText(f"{stats.get('avg_pressure', 0):.2f}")
            self.stats_cards[3][1].setText(f"{stats.get('avg_temperature', 0):.2f}")
        
        # Update charts
        self.pie_chart.plot(type_distribution)
        self.bar_chart.plot(stats)
        self.line_chart.plot(equipment_list)
        
        # Update table
        self.data_table.setRowCount(len(equipment_list))
        for i, item in enumerate(equipment_list):
            self.data_table.setItem(i, 0, QTableWidgetItem(str(item.get('Equipment Name', item.get('name', '')))))
            self.data_table.setItem(i, 1, QTableWidgetItem(str(item.get('Type', item.get('type', '')))))
            self.data_table.setItem(i, 2, QTableWidgetItem(f"{item.get('Flowrate', item.get('flowrate', 0)):.2f}"))
            self.data_table.setItem(i, 3, QTableWidgetItem(f"{item.get('Pressure', item.get('pressure', 0)):.2f}"))
            self.data_table.setItem(i, 4, QTableWidgetItem(f"{item.get('Temperature', item.get('temperature', 0)):.2f}"))
    
    def show_error(self, error_message):
        """Show error message"""
        QMessageBox.critical(self, 'Error', f'Failed to load data: {error_message}')
    
    def open_upload_dialog(self):
        """Open file upload dialog"""
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select CSV File', '', 'CSV Files (*.csv)')
        
        if file_path:
            try:
                result = self.api_client.upload_csv(file_path)
                QMessageBox.information(self, 'Success', 'File uploaded successfully!')
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, 'Upload Failed', f'Error: {str(e)}')
    
    def show_history(self):
        """Show upload history"""
        try:
            history_data = self.api_client.get_history()
            datasets = history_data.get('datasets', [])
            
            if not datasets:
                QMessageBox.information(self, 'History', 'No upload history found.')
                return
            
            # Create history dialog
            from ui.upload_window import HistoryDialog
            dialog = HistoryDialog(self.api_client, datasets, self)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load history: {str(e)}')
