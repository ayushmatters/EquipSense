"""
Upload Window and History Dialog for Desktop Application

Provides file upload interface and history viewing.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog,
                             QScrollArea, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime


class HistoryDialog(QDialog):
    """Dialog for viewing upload history"""
    
    def __init__(self, api_client, datasets, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.datasets = datasets
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Upload History')
        self.setGeometry(200, 200, 900, 600)
        
        self.setStyleSheet("""
            QDialog {
                background: #f0f2f5;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                padding: 8px 16px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5568d3, stop:1 #6c3e8c);
            }
            QFrame {
                background: white;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel('📜 Upload History')
        title_font = QFont('Segoe UI', 20, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel(f'Last {len(self.datasets)} uploads')
        subtitle_label.setStyleSheet('color: #666; font-size: 14px;')
        layout.addWidget(subtitle_label)
        
        # Scroll area for datasets
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')
        
        scroll_widget = QFrame()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(10)
        
        # Create card for each dataset
        for dataset in self.datasets:
            card = self.create_dataset_card(dataset)
            scroll_layout.addWidget(card)
        
        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        
        layout.addWidget(scroll)
        
        # Close button
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def create_dataset_card(self, dataset):
        """Create a card widget for a dataset"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                border: 2px solid #e0e0e0;
                padding: 15px;
            }
            QFrame:hover {
                border: 2px solid #667eea;
            }
        """)
        
        card_layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        filename_label = QLabel(f"📄 {dataset['filename']}")
        filename_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #333;')
        
        header_layout.addWidget(filename_label)
        header_layout.addStretch()
        
        # Download button
        download_btn = QPushButton('📥 Download PDF')
        download_btn.clicked.connect(lambda: self.download_report(dataset['id']))
        header_layout.addWidget(download_btn)
        
        card_layout.addLayout(header_layout)
        
        # Date
        date_str = self.format_date(dataset['uploaded_at'])
        date_label = QLabel(f'📅 {date_str}')
        date_label.setStyleSheet('color: #666; font-size: 12px;')
        card_layout.addWidget(date_label)
        
        # Statistics grid
        stats_layout = QHBoxLayout()
        
        stats = [
            ('Equipment', str(dataset['equipment_count']), '#3b82f6'),
            ('Flowrate', f"{dataset.get('avg_flowrate', 0):.2f}", '#a855f7'),
            ('Pressure', f"{dataset.get('avg_pressure', 0):.2f}", '#ec4899'),
            ('Temperature', f"{dataset.get('avg_temperature', 0):.2f}", '#f97316')
        ]
        
        for label, value, color in stats:
            stat_widget = QFrame()
            stat_widget.setStyleSheet(f"""
                QFrame {{
                    background: #f8f9fa;
                    border-radius: 6px;
                    padding: 8px;
                    border-left: 3px solid {color};
                }}
            """)
            
            stat_layout = QVBoxLayout()
            stat_layout.setSpacing(2)
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet('color: #666; font-size: 10px;')
            
            value_widget = QLabel(value)
            value_widget.setStyleSheet(f'color: {color}; font-size: 16px; font-weight: bold;')
            
            stat_layout.addWidget(label_widget)
            stat_layout.addWidget(value_widget)
            stat_widget.setLayout(stat_layout)
            
            stats_layout.addWidget(stat_widget)
        
        card_layout.addLayout(stats_layout)
        
        card.setLayout(card_layout)
        return card
    
    def format_date(self, date_string):
        """Format datetime string"""
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            return date_string
    
    def download_report(self, dataset_id):
        """Download PDF report for a dataset"""
        save_path, _ = QFileDialog.getSaveFileName(
            self, 'Save PDF Report', f'equipment_report_{dataset_id}.pdf', 'PDF Files (*.pdf)'
        )
        
        if save_path:
            try:
                self.api_client.download_report(dataset_id, save_path)
                QMessageBox.information(self, 'Success', 'Report downloaded successfully!')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to download report: {str(e)}')
