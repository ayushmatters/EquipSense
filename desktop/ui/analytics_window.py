"""
Native Analytics Window

Standalone PyQt5 window for CSV data analytics using Matplotlib.
Provides data upload, visualization, and statistical analysis.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QTabWidget, QComboBox, QScrollArea, QGroupBox,
    QGridLayout, QMessageBox, QProgressBar, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from services.csv_processor import CSVProcessor
from charts.matplotlib_charts import (
    LineChartCanvas, BarChartCanvas, HistogramCanvas, 
    ScatterPlotCanvas, PieChartCanvas
)
import os


class DataLoadThread(QThread):
    """Background thread for loading CSV files"""
    
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)
    
    def __init__(self, processor, file_path):
        super().__init__()
        self.processor = processor
        self.file_path = file_path
    
    def run(self):
        """Load CSV in background"""
        self.progress.emit(30)
        success, message = self.processor.load_csv(self.file_path)
        self.progress.emit(100)
        self.finished.emit(success, message)


class AnalyticsWindow(QWidget):
    """
    Native analytics window with CSV upload and Matplotlib visualizations.
    
    Features:
    - CSV file upload
    - Multiple chart types (line, bar, histogram, scatter, pie)
    - Statistical summary
    - Data table view
    - Export capabilities
    """
    
    def __init__(self, session_handler=None):
        super().__init__()
        self.session_handler = session_handler
        self.processor = CSVProcessor()
        self.current_data = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('EquipSense - Native Analytics Module')
        self.setMinimumSize(1200, 800)
        self.center_window()
        
        # Apply modern stylesheet
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #1d4ed8);
            }
            QPushButton:pressed {
                background: #1e40af;
            }
            QPushButton:disabled {
                background: #9ca3af;
            }
            QLabel {
                color: #1f2937;
                font-size: 13px;
            }
            QTabWidget::pane {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #e5e7eb;
                color: #374151;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background: white;
                color: #3b82f6;
            }
            QComboBox {
                background: white;
                border: 2px solid #d1d5db;
                border-radius: 6px;
                padding: 8px;
                color: #1f2937;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 2px solid #3b82f6;
            }
            QGroupBox {
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 10px;
                font-weight: 600;
                color: #1f2937;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QProgressBar {
                border: 2px solid #d1d5db;
                border-radius: 5px;
                text-align: center;
                background: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #2563eb);
                border-radius: 3px;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header Section
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Progress Bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(8)
        main_layout.addWidget(self.progress_bar)
        
        # Control Panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Main Content Area with Tabs
        self.tab_widget = QTabWidget()
        
        # Tab 1: Charts
        charts_tab = self.create_charts_tab()
        self.tab_widget.addTab(charts_tab, "📊 Visualizations")
        
        # Tab 2: Statistics
        stats_tab = self.create_statistics_tab()
        self.tab_widget.addTab(stats_tab, "📈 Statistics")
        
        # Tab 3: Data Table
        data_tab = self.create_data_tab()
        self.tab_widget.addTab(data_tab, "📋 Data Table")
        
        main_layout.addWidget(self.tab_widget)
        
        self.setLayout(main_layout)
    
    def create_header(self):
        """Create header section"""
        header = QWidget()
        layout = QHBoxLayout()
        
        # Title
        title_label = QLabel('⚗️ Native Analytics Module')
        title_font = QFont('Segoe UI', 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1f2937;")
        
        layout.addWidget(title_label)
        layout.addStretch()
        
        # User info (if authenticated)
        if self.session_handler and self.session_handler.is_authenticated():
            user_label = QLabel(f"👤 {self.session_handler.get_username()}")
            user_label.setStyleSheet("""
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 20px;
                padding: 8px 16px;
                color: #374151;
                font-weight: 500;
            """)
            layout.addWidget(user_label)
        
        header.setLayout(layout)
        return header
    
    def create_control_panel(self):
        """Create control panel with upload and chart type selection"""
        panel = QGroupBox("Data Controls")
        layout = QHBoxLayout()
        
        # Upload Button
        self.upload_btn = QPushButton("📁 Upload CSV")
        self.upload_btn.clicked.connect(self.upload_csv)
        self.upload_btn.setMinimumWidth(150)
        layout.addWidget(self.upload_btn)
        
        # File Info Label
        self.file_info_label = QLabel("No file loaded")
        self.file_info_label.setStyleSheet("""
            background: white;
            padding: 8px 12px;
            border-radius: 6px;
            color: #6b7280;
        """)
        layout.addWidget(self.file_info_label)
        
        layout.addStretch()
        
        # Chart Type Selection
        chart_type_label = QLabel("Chart Type:")
        chart_type_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(chart_type_label)
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems([
            "Line Chart", "Bar Chart", "Histogram", 
            "Scatter Plot", "Pie Chart"
        ])
        self.chart_type_combo.currentIndexChanged.connect(self.update_chart)
        self.chart_type_combo.setMinimumWidth(150)
        self.chart_type_combo.setEnabled(False)
        layout.addWidget(self.chart_type_combo)
        
        # Refresh Button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.update_chart)
        self.refresh_btn.setEnabled(False)
        layout.addWidget(self.refresh_btn)
        
        panel.setLayout(layout)
        return panel
    
    def create_charts_tab(self):
        """Create charts visualization tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Column selection
        selection_layout = QHBoxLayout()
        
        selection_layout.addWidget(QLabel("Select Columns:"))
        
        self.column_combo1 = QComboBox()
        self.column_combo1.setMinimumWidth(200)
        self.column_combo1.currentIndexChanged.connect(self.update_chart)
        selection_layout.addWidget(self.column_combo1)
        
        self.column_combo2 = QComboBox()
        self.column_combo2.setMinimumWidth(200)
        self.column_combo2.currentIndexChanged.connect(self.update_chart)
        self.column_combo2.setVisible(False)  # For scatter plots
        selection_layout.addWidget(self.column_combo2)
        
        selection_layout.addStretch()
        layout.addLayout(selection_layout)
        
        # Chart Canvas Area
        self.chart_canvas = LineChartCanvas(self, width=10, height=6)
        layout.addWidget(self.chart_canvas)
        
        tab.setLayout(layout)
        return tab
    
    def create_statistics_tab(self):
        """Create statistics summary tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Scroll area for statistics
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.stats_container = QWidget()
        self.stats_layout = QVBoxLayout()
        self.stats_container.setLayout(self.stats_layout)
        
        # Placeholder
        placeholder = QLabel("📊 Upload a CSV file to view statistics")
        placeholder.setStyleSheet("""
            font-size: 16px;
            color: #9ca3af;
            padding: 50px;
        """)
        placeholder.setAlignment(Qt.AlignCenter)
        self.stats_layout.addWidget(placeholder)
        
        scroll.setWidget(self.stats_container)
        layout.addWidget(scroll)
        
        tab.setLayout(layout)
        return tab
    
    def create_data_tab(self):
        """Create data table view tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Data preview label
        self.data_preview_label = QLabel("📋 Upload a CSV file to view data")
        self.data_preview_label.setStyleSheet("""
            font-size: 16px;
            color: #9ca3af;
            padding: 50px;
            background: white;
            border-radius: 8px;
        """)
        self.data_preview_label.setAlignment(Qt.AlignCenter)
        self.data_preview_label.setWordWrap(True)
        
        layout.addWidget(self.data_preview_label)
        
        tab.setLayout(layout)
        return tab
    
    def center_window(self):
        """Center window on screen"""
        from PyQt5.QtWidgets import QDesktopWidget
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def upload_csv(self):
        """Handle CSV file upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.upload_btn.setEnabled(False)
        
        # Load in background thread
        self.load_thread = DataLoadThread(self.processor, file_path)
        self.load_thread.progress.connect(self.progress_bar.setValue)
        self.load_thread.finished.connect(self.on_data_loaded)
        self.load_thread.start()
    
    def on_data_loaded(self, success, message):
        """Handle data loading completion"""
        self.progress_bar.setVisible(False)
        self.upload_btn.setEnabled(True)
        
        if success:
            # Update UI with loaded data
            self.file_info_label.setText(f"✓ {os.path.basename(self.processor.file_path)}")
            self.file_info_label.setStyleSheet("""
                background: #d1fae5;
                padding: 8px 12px;
                border-radius: 6px;
                color: #065f46;
                font-weight: 500;
            """)
            
            # Populate column combos
            self.column_combo1.clear()
            self.column_combo2.clear()
            self.column_combo1.addItems(self.processor.numeric_columns)
            self.column_combo2.addItems(self.processor.numeric_columns)
            
            # Enable controls
            self.chart_type_combo.setEnabled(True)
            self.refresh_btn.setEnabled(True)
            
            # Update displays
            self.update_statistics()
            self.update_data_table()
            self.update_chart()
            
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
            self.file_info_label.setText("❌ Failed to load")
            self.file_info_label.setStyleSheet("""
                background: #fee2e2;
                padding: 8px 12px;
                border-radius: 6px;
                color: #991b1b;
            """)
    
    def update_chart(self):
        """Update chart based on selected type and data"""
        if not self.processor.df is not None:
            return
        
        chart_type = self.chart_type_combo.currentText()
        
        # Handle visibility of second column selector
        self.column_combo2.setVisible(chart_type == "Scatter Plot")
        
        try:
            if chart_type == "Line Chart":
                self.show_line_chart()
            elif chart_type == "Bar Chart":
                self.show_bar_chart()
            elif chart_type == "Histogram":
                self.show_histogram()
            elif chart_type == "Scatter Plot":
                self.show_scatter_plot()
            elif chart_type == "Pie Chart":
                self.show_pie_chart()
        except Exception as e:
            QMessageBox.warning(self, "Chart Error", f"Could not generate chart: {str(e)}")
    
    def show_line_chart(self):
        """Display line chart"""
        data = self.processor.get_numeric_columns_data()
        if self.chart_canvas.__class__.__name__ != "LineChartCanvas":
            self.replace_chart_canvas(LineChartCanvas)
        self.chart_canvas.plot(data, title="Line Chart - All Numeric Columns", 
                               xlabel="Index", ylabel="Values")
    
    def show_bar_chart(self):
        """Display bar chart"""
        col = self.column_combo1.currentText()
        if col:
            data_list = self.processor.get_column_data(col)
            # Aggregate top 10 values
            data = {f"Row {i+1}": v for i, v in enumerate(data_list[:10])}
            if self.chart_canvas.__class__.__name__ != "BarChartCanvas":
                self.replace_chart_canvas(BarChartCanvas)
            self.chart_canvas.plot(data, title=f"Bar Chart - {col}", 
                                  xlabel="Rows", ylabel=col)
    
    def show_histogram(self):
        """Display histogram"""
        col = self.column_combo1.currentText()
        if col:
            data = self.processor.get_column_data(col)
            if self.chart_canvas.__class__.__name__ != "HistogramCanvas":
                self.replace_chart_canvas(HistogramCanvas)
            self.chart_canvas.plot(data, title=f"Histogram - {col}", xlabel=col)
    
    def show_scatter_plot(self):
        """Display scatter plot"""
        col1 = self.column_combo1.currentText()
        col2 = self.column_combo2.currentText()
        if col1 and col2:
            x_data = self.processor.get_column_data(col1)
            y_data = self.processor.get_column_data(col2)
            if self.chart_canvas.__class__.__name__ != "ScatterPlotCanvas":
                self.replace_chart_canvas(ScatterPlotCanvas)
            self.chart_canvas.plot(x_data, y_data, 
                                  title=f"Scatter Plot: {col1} vs {col2}",
                                  xlabel=col1, ylabel=col2)
    
    def show_pie_chart(self):
        """Display pie chart"""
        col = self.column_combo1.currentText()
        if col:
            data_list = self.processor.get_column_data(col)
            # Aggregate top 5 values
            data = {f"Group {i+1}": v for i, v in enumerate(data_list[:5])}
            if self.chart_canvas.__class__.__name__ != "PieChartCanvas":
                self.replace_chart_canvas(PieChartCanvas)
            self.chart_canvas.plot(data, title=f"Pie Chart - {col}")
    
    def replace_chart_canvas(self, canvas_class):
        """Replace chart canvas with different type"""
        layout = self.chart_canvas.parent().layout()
        layout.removeWidget(self.chart_canvas)
        self.chart_canvas.deleteLater()
        self.chart_canvas = canvas_class(self, width=10, height=6)
        layout.addWidget(self.chart_canvas)
    
    def update_statistics(self):
        """Update statistics display"""
        stats = self.processor.get_summary_statistics()
        
        # Clear previous stats
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Overall stats
        overall_group = QGroupBox("📊 Dataset Overview")
        overall_layout = QGridLayout()
        
        overall_layout.addWidget(QLabel("Total Rows:"), 0, 0)
        overall_layout.addWidget(QLabel(f"<b>{stats['total_rows']}</b>"), 0, 1)
        
        overall_layout.addWidget(QLabel("Total Columns:"), 1, 0)
        overall_layout.addWidget(QLabel(f"<b>{stats['total_columns']}</b>"), 1, 1)
        
        overall_layout.addWidget(QLabel("Numeric Columns:"), 2, 0)
        overall_layout.addWidget(QLabel(f"<b>{stats['numeric_columns']}</b>"), 2, 1)
        
        overall_layout.addWidget(QLabel("Missing Values:"), 3, 0)
        overall_layout.addWidget(QLabel(f"<b>{stats['missing_values']}</b>"), 3, 1)
        
        overall_group.setLayout(overall_layout)
        self.stats_layout.addWidget(overall_group)
        
        # Column statistics
        for col_name, col_stats in stats.get('column_stats', {}).items():
            col_group = QGroupBox(f"📈 {col_name}")
            col_layout = QGridLayout()
            
            row = 0
            for stat_name, stat_value in col_stats.items():
                col_layout.addWidget(QLabel(f"{stat_name.capitalize()}:"), row, 0)
                col_layout.addWidget(QLabel(f"<b>{stat_value:.2f}</b>"), row, 1)
                row += 1
            
            col_group.setLayout(col_layout)
            self.stats_layout.addWidget(col_group)
        
        self.stats_layout.addStretch()
    
    def update_data_table(self):
        """Update data table preview"""
        df_head = self.processor.get_top_n_rows(10)
        if df_head is not None:
            # Create simple text representation
            table_text = f"<h3>First 10 Rows:</h3><pre>{df_head.to_string()}</pre>"
            self.data_preview_label.setText(table_text)
            self.data_preview_label.setStyleSheet("""
                font-family: 'Courier New', monospace;
                font-size: 11px;
                color: #1f2937;
                padding: 20px;
                background: white;
                border-radius: 8px;
            """)
            self.data_preview_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
