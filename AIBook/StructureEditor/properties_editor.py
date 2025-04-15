"""
PropertiesEditor class for the Interactive Book Editor.
ADDED: Print statements for debugging node display flow.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel
from PyQt5.QtCore import pyqtSignal

from node_editor import NodeEditorPanel
from edge_editor import EdgeEditorPanel
from book_editor import BookNodeEditor

class PropertiesEditor(QWidget):
    """
    Panel for viewing and editing properties of selected nodes and edges.
    Manages specialized editors for different types of items.
    """
    
    node_updated = pyqtSignal(object) 
    edge_updated = pyqtSignal(object) 
    chapters_updated = pyqtSignal(list) 
    
    def __init__(self, parent=None):
        """Initialize a new PropertiesEditor instance."""
        super().__init__(parent)
        self.current_node = None
        self.current_edge = None
        self.book_graph = None
        self.available_chapters = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        self.stacked_widget = QStackedWidget(self)
        layout.addWidget(self.stacked_widget)
        
        self.empty_widget = QWidget(self)
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.addWidget(QLabel("No item selected"))
        
        self.node_editor = NodeEditorPanel(self)
        self.edge_editor = EdgeEditorPanel(self)
        self.book_editor = BookNodeEditor(self)
        
        self.stacked_widget.addWidget(self.empty_widget) # Index 0
        self.stacked_widget.addWidget(self.node_editor)  # Index 1
        self.stacked_widget.addWidget(self.edge_editor)  # Index 2
        self.stacked_widget.addWidget(self.book_editor)  # Index 3
        
        self.stacked_widget.setCurrentWidget(self.empty_widget)
        
        self.node_editor.node_updated.connect(self.node_updated)
        self.edge_editor.edge_updated.connect(self.edge_updated)
        self.book_editor.node_updated.connect(self.node_updated)
        self.book_editor.chapters_updated.connect(self.chapters_updated)
    
    def set_book_graph(self, book_graph):
        """Set the book graph for the editors."""
        print("PropertiesEditor: Setting book graph.") # Debug
        self.book_graph = book_graph
        self.node_editor.set_book_graph(book_graph)
        self.book_editor.set_book_graph(book_graph)
    
    def set_available_chapters(self, chapters):
        """Set the available chapters for the chapter combo box."""
        print("PropertiesEditor: Setting available chapters.") # Debug
        self.available_chapters = chapters
        self.node_editor.set_available_chapters(chapters)
        # Assuming book editor also needs chapters if it manages them
        # self.book_editor.set_available_chapters(chapters) 
    
    def display_node(self, node):
        """Display the properties of a node."""
        print(f"\nPropertiesEditor: display_node called for node ID: {getattr(node, 'id', 'N/A')}") # Debug
        if not node:
             print("PropertiesEditor: Received None node, clearing display.")
             self.clear_display()
             return
             
        self.current_node = node
        self.current_edge = None
        
        print(f"PropertiesEditor: Node Type = {getattr(node, 'node_type', 'N/A')}") # Debug
        
        # Check if this is a book node
        if node.node_type == "book":
            print("PropertiesEditor: Displaying BookNodeEditor.") # Debug
            # Update the book editor
            self.book_editor.update_for_node(node)
            # Show the book editor
            self.stacked_widget.setCurrentWidget(self.book_editor)
        else:
            print("PropertiesEditor: Displaying NodeEditorPanel.") # Debug
            # Update the node editor
            self.node_editor.update_for_node(node)
            # Show the node editor
            self.stacked_widget.setCurrentWidget(self.node_editor)
            
        print(f"PropertiesEditor: Current stack index: {self.stacked_widget.currentIndex()}") # Debug

    def display_edge(self, edge):
        """Display the properties of an edge."""
        print(f"\nPropertiesEditor: display_edge called for edge: {getattr(edge, 'source_id', 'N/A')}->{getattr(edge, 'target_id', 'N/A')}") # Debug
        if not edge:
             print("PropertiesEditor: Received None edge, clearing display.")
             self.clear_display()
             return
             
        self.current_node = None
        self.current_edge = edge
        
        print("PropertiesEditor: Displaying EdgeEditorPanel.") # Debug
        self.edge_editor.update_for_edge(edge)
        self.stacked_widget.setCurrentWidget(self.edge_editor)
        print(f"PropertiesEditor: Current stack index: {self.stacked_widget.currentIndex()}") # Debug

    
    def clear_display(self):
        """Clear the display."""
        print("PropertiesEditor: Clearing display.") # Debug
        self.current_node = None
        self.current_edge = None
        
        # Clear the specific editors (optional, but good practice)
        # self.node_editor.clear_panel() 
        # self.edge_editor.clear_panel()
        # self.book_editor.clear_panel()
        
        # Show the empty widget
        self.stacked_widget.setCurrentWidget(self.empty_widget)
        print(f"PropertiesEditor: Current stack index set to empty: {self.stacked_widget.currentIndex()}") # Debug

