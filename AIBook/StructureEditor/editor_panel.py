"""
Base editor panel class for the Interactive Book Editor.
This class provides the foundation for specialized property editors.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

class EditorPanel(QWidget):
    """
    Base class for editor panels.
    
    Provides common functionality and structure for specialized editors
    to display and edit properties of selected items.
    """
    
    def __init__(self, parent=None):
        """Initialize a new EditorPanel instance."""
        super().__init__(parent)
        
        # Set up the basic layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
    def update_for_item(self, item):
        """
        Update the panel for the selected item.
        
        Args:
            item: The selected item
        """
        # To be implemented by subclasses
        pass
    
    def clear_panel(self):
        """Clear the panel."""
        # To be implemented by subclasses
        pass


class TabbedEditorPanel(EditorPanel):
    """
    Editor panel with a tabbed interface.
    
    Contains multiple tabs for different property categories.
    """
    
    def __init__(self, parent=None):
        """Initialize a new TabbedEditorPanel instance."""
        super().__init__(parent)
        
        # Create the tab widget
        self.tab_widget = QTabWidget(self)
        self.layout.addWidget(self.tab_widget)
        
    def add_tab(self, widget, title):
        """
        Add a tab to the panel.
        
        Args:
            widget (QWidget): Widget to add as a tab
            title (str): Title for the tab
        """
        self.tab_widget.addTab(widget, title)
        
    def clear_panel(self):
        """Clear all tabs from the panel."""
        while self.tab_widget.count() > 0:
            self.tab_widget.removeTab(0)
