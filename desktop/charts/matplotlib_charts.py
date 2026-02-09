"""
Matplotlib Chart Generation for Desktop Application

Creates charts for equipment data visualization and CSV analytics.
Supports line charts, bar charts, histograms, scatter plots, and more.
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from typing import Dict, List, Optional


class ChartCanvas(FigureCanvas):
    """Base class for matplotlib charts in PyQt5"""
    
    def __init__(self, parent=None, width=10, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#f8f9fa')
        self.axes = self.fig.add_subplot(111)
        super(ChartCanvas, self).__init__(self.fig)
        self.setParent(parent)
        
        # Set modern style
        plt.style.use('seaborn-v0_8-whitegrid')
        self.fig.patch.set_facecolor('#f8f9fa')
        self.axes.set_facecolor('#ffffff')
        
    def clear_plot(self):
        """Clear the current plot"""
        self.axes.clear()
        self.axes.set_facecolor('#ffffff')


class LineChartCanvas(ChartCanvas):
    """Line chart for time series and continuous data"""
    
    def plot(self, data: Dict[str, List], title: str = "Line Chart", 
             xlabel: str = "X-Axis", ylabel: str = "Y-Axis"):
        """
        Plot line chart with multiple series.
        
        Args:
            data: Dictionary mapping series names to their data points
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
        """
        self.clear_plot()
        
        if not data:
            self.axes.text(0.5, 0.5, 'No data available', 
                          horizontalalignment='center',
                          verticalalignment='center',
                          fontsize=14, color='#6b7280')
            self.draw()
            return
        
        # Color palette
        colors = ['#3b82f6', '#a855f7', '#ec4899', '#22c55e', '#fb923c', '#0ea5e9']
        
        for idx, (label, values) in enumerate(data.items()):
            color = colors[idx % len(colors)]
            self.axes.plot(values, label=label, color=color, 
                          linewidth=2.5, marker='o', markersize=5, alpha=0.8)
        
        self.axes.set_title(title, fontsize=16, fontweight='bold', pad=20, color='#1f2937')
        self.axes.set_xlabel(xlabel, fontsize=12, fontweight='500', color='#374151')
        self.axes.set_ylabel(ylabel, fontsize=12, fontweight='500', color='#374151')
        self.axes.legend(loc='best', framealpha=0.9, fontsize=10)
        self.axes.grid(True, alpha=0.3, linestyle='--')
        
        self.fig.tight_layout()
        self.draw()


class BarChartCanvas(ChartCanvas):
    """Bar chart for categorical comparisons"""
    
    def plot(self, data: Dict[str, float], title: str = "Bar Chart", 
             xlabel: str = "Categories", ylabel: str = "Values", 
             orientation: str = 'vertical'):
        """
        Plot bar chart.
        
        Args:
            data: Dictionary mapping categories to values
            title: Chart title
            xlabel: X-axis label  
            ylabel: Y-axis label
            orientation: 'vertical' or 'horizontal'
        """
        self.clear_plot()
        
        if not data:
            self.axes.text(0.5, 0.5, 'No data available',
                          horizontalalignment='center',
                          verticalalignment='center',
                          fontsize=14, color='#6b7280')
            self.draw()
            return
        
        labels = list(data.keys())
        values = list(data.values())
        
        # Gradient colors
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(labels)))
        
        if orientation == 'horizontal':
            bars = self.axes.barh(labels, values, color=colors, edgecolor='#1f2937', linewidth=0.8)
            self.axes.set_xlabel(ylabel, fontsize=12, fontweight='500', color='#374151')
            self.axes.set_ylabel(xlabel, fontsize=12, fontweight='500', color='#374151')
        else:
            bars = self.axes.bar(labels, values, color=colors, edgecolor='#1f2937', linewidth=0.8)
            self.axes.set_xlabel(xlabel, fontsize=12, fontweight='500', color='#374151')
            self.axes.set_ylabel(ylabel, fontsize=12, fontweight='500', color='#374151')
            
            # Rotate x-axis labels if needed
            if len(labels) > 5:
                plt.setp(self.axes.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        self.axes.set_title(title, fontsize=16, fontweight='bold', pad=20, color='#1f2937')
        self.axes.grid(True, alpha=0.3, linestyle='--', axis='y' if orientation == 'vertical' else 'x')
        
        # Add value labels on bars
        if orientation == 'horizontal':
            for bar in bars:
                width = bar.get_width()
                self.axes.text(width, bar.get_y() + bar.get_height()/2, 
                              f'{width:.2f}',
                              ha='left', va='center', fontsize=9, color='#374151')
        else:
            for bar in bars:
                height = bar.get_height()
                self.axes.text(bar.get_x() + bar.get_width()/2, height,
                              f'{height:.2f}',
                              ha='center', va='bottom', fontsize=9, color='#374151')
        
        self.fig.tight_layout()
        self.draw()


class HistogramCanvas(ChartCanvas):
    """Histogram for distribution analysis"""
    
    def plot(self, data: List[float], bins: int = 20, 
             title: str = "Histogram", xlabel: str = "Values", ylabel: str = "Frequency"):
        """
        Plot histogram.
        
        Args:
            data: List of numeric values
            bins: Number of bins
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
        """
        self.clear_plot()
        
        if not data or len(data) == 0:
            self.axes.text(0.5, 0.5, 'No data available',
                          horizontalalignment='center',
                          verticalalignment='center',
                          fontsize=14, color='#6b7280')
            self.draw()
            return
        
        n, bins_edges, patches = self.axes.hist(data, bins=bins, 
                                                  color='#3b82f6',
                                                  alpha=0.7,
                                                  edgecolor='#1f2937',
                                                  linewidth=1.2)
        
        # Color gradient
        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(patches)))
        for patch, color in zip(patches, colors):
            patch.set_facecolor(color)
        
        self.axes.set_title(title, fontsize=16, fontweight='bold', pad=20, color='#1f2937')
        self.axes.set_xlabel(xlabel, fontsize=12, fontweight='500', color='#374151')
        self.axes.set_ylabel(ylabel, fontsize=12, fontweight='500', color='#374151')
        self.axes.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # Add mean line
        mean_val = np.mean(data)
        self.axes.axvline(mean_val, color='#dc2626', linestyle='--', 
                         linewidth=2, label=f'Mean: {mean_val:.2f}')
        self.axes.legend(fontsize=10)
        
        self.fig.tight_layout()
        self.draw()


class ScatterPlotCanvas(ChartCanvas):
    """Scatter plot for correlation analysis"""
    
    def plot(self, x_data: List[float], y_data: List[float],
             title: str = "Scatter Plot", xlabel: str = "X-Axis", ylabel: str = "Y-Axis"):
        """
        Plot scatter plot.
        
        Args:
            x_data: X-axis values
            y_data: Y-axis values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
        """
        self.clear_plot()
        
        if not x_data or not y_data or len(x_data) != len(y_data):
            self.axes.text(0.5, 0.5, 'Invalid or missing data',
                          horizontalalignment='center',
                          verticalalignment='center',
                          fontsize=14, color='#6b7280')
            self.draw()
            return
        
        self.axes.scatter(x_data, y_data, 
                         c='#3b82f6', 
                         s=50, 
                         alpha=0.6,
                         edgecolors='#1f2937',
                         linewidth=0.5)
        
        # Add trend line
        z = np.polyfit(x_data, y_data, 1)
        p = np.poly1d(z)
        self.axes.plot(x_data, p(x_data), 
                      color='#dc2626', 
                      linestyle='--',
                      linewidth=2,
                      label=f'Trend: y={z[0]:.2f}x+{z[1]:.2f}')
        
        self.axes.set_title(title, fontsize=16, fontweight='bold', pad=20, color='#1f2937')
        self.axes.set_xlabel(xlabel, fontsize=12, fontweight='500', color='#374151')
        self.axes.set_ylabel(ylabel, fontsize=12, fontweight='500', color='#374151')
        self.axes.legend(fontsize=10)
        self.axes.grid(True, alpha=0.3, linestyle='--')
        
        self.fig.tight_layout()
        self.draw()


class PieChartCanvas(ChartCanvas):
    """Pie chart for equipment type distribution"""
    
    def plot(self, type_distribution: Dict[str, float], title: str = "Distribution"):
        """
        Plot equipment type distribution
        
        Args:
            type_distribution: Dictionary mapping type to count/value
            title: Chart title
        """
        self.clear_plot()
        
        if not type_distribution:
            self.axes.text(0.5, 0.5, 'No data available', 
                          horizontalalignment='center',
                          verticalalignment='center',
                          fontsize=14, color='#6b7280')
            self.draw()
            return
        
        labels = list(type_distribution.keys())
        sizes = list(type_distribution.values())
        
        colors = ['#3b82f6', '#a855f7', '#ec4899', '#22c55e', '#fb923c', '#0ea5e9']
        explode = [0.05] * len(labels)  # Explode all slices slightly
        
        wedges, texts, autotexts = self.axes.pie(
            sizes, 
           explode=explode,
            labels=labels,
            colors=colors[:len(labels)],
            autopct='%1.1f%%',
            shadow=True,
            startangle=90,
            textprops={'fontsize': 10, 'color': '#1f2937'}
        )
        
        # Enhance text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        self.axes.set_title(title, fontsize=16, fontweight='bold', pad=20, color='#1f2937')
        self.axes.axis('equal')
        
        self.fig.tight_layout()
        self.draw()
        
        self.axes.pie(sizes, explode=explode, labels=labels, colors=colors,
                     autopct='%1.1f%%', shadow=True, startangle=90)
        self.axes.axis('equal')
        self.axes.set_title('Equipment Type Distribution', fontsize=14, fontweight='bold')
        
        self.draw()


class BarChartCanvas(ChartCanvas):
    """Bar chart for parameter averages"""
    
    def plot(self, statistics):
        """
        Plot parameter averages
        
        Args:
            statistics: Dictionary with avg_flowrate, avg_pressure, avg_temperature
        """
        self.axes.clear()
        
        if not statistics:
            self.axes.text(0.5, 0.5, 'No data available', 
                          horizontalalignment='center',
                          verticalalignment='center',
                          fontsize=14)
            self.draw()
            return
        
        parameters = ['Flowrate', 'Pressure', 'Temperature']
        values = [
            statistics.get('avg_flowrate', 0),
            statistics.get('avg_pressure', 0),
            statistics.get('avg_temperature', 0)
        ]
        
        colors = ['#3b82f6', '#a855f7', '#ec4899']
        
        bars = self.axes.bar(parameters, values, color=colors, alpha=0.8, edgecolor='black')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            self.axes.text(bar.get_x() + bar.get_width()/2., height,
                          f'{height:.2f}',
                          ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        self.axes.set_ylabel('Average Value', fontsize=12, fontweight='bold')
        self.axes.set_title('Parameter Averages', fontsize=14, fontweight='bold')
        self.axes.grid(True, alpha=0.3)
        
        self.draw()


class LineChartCanvas(ChartCanvas):
    """Line chart for equipment parameters"""
    
    def plot(self, equipment_list):
        """
        Plot equipment parameters as line chart
        
        Args:
            equipment_list: List of equipment dictionaries
        """
        self.axes.clear()
        
        if not equipment_list:
            self.axes.text(0.5, 0.5, 'No data available', 
                          horizontalalignment='center',
                          verticalalignment='center',
                          fontsize=14)
            self.draw()
            return
        
        # Limit to first 20 items for readability
        data = equipment_list[:20]
        
        indices = range(len(data))
        flowrates = [item.get('Flowrate', item.get('flowrate', 0)) for item in data]
        pressures = [item.get('Pressure', item.get('pressure', 0)) for item in data]
        temperatures = [item.get('Temperature', item.get('temperature', 0)) for item in data]
        
        self.axes.plot(indices, flowrates, 'o-', label='Flowrate', color='#3b82f6', linewidth=2)
        self.axes.plot(indices, pressures, 's-', label='Pressure', color='#a855f7', linewidth=2)
        self.axes.plot(indices, temperatures, '^-', label='Temperature', color='#ec4899', linewidth=2)
        
        self.axes.set_xlabel('Equipment Index', fontsize=12, fontweight='bold')
        self.axes.set_ylabel('Parameter Value', fontsize=12, fontweight='bold')
        self.axes.set_title('Equipment Parameters', fontsize=14, fontweight='bold')
        self.axes.legend(loc='best', fontsize=10)
        self.axes.grid(True, alpha=0.3)
        
        self.draw()
