"""
GraphView class for the Interactive Book Editor.
REVISED: Restored RubberBandDrag for left-click selection.
         Re-implemented custom middle-button panning logic.
         Ensured default cursor is ArrowCursor.
FIXED: Included complete implementations for all methods.
"""

import math 
import traceback # For debugging potential errors
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMenu, QAction, QInputDialog
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF, QLineF 
from PyQt5.QtGui import QPainter, QPen, QColor, QKeyEvent, QWheelEvent 

from graph_items import GraphNodeItem, GraphEdgeItem
from node import Edge # Assuming Edge class is in node.py

class GraphView(QGraphicsView):
    """
    Custom QGraphicsView for displaying and interacting with the book graph.
    Implements scroll-wheel zoom, middle-button panning, and left-click selection.
    """
    
    # Signals
    node_selected = pyqtSignal(object); edge_selected = pyqtSignal(object) 
    selection_cleared = pyqtSignal(); node_moved = pyqtSignal(object)  
    edge_created = pyqtSignal(object); edge_deleted = pyqtSignal(object) 
    
    def __init__(self, parent=None):
        """Initialize a new GraphView instance."""
        super().__init__(parent)
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # --- View Options ---
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setDragMode(QGraphicsView.RubberBandDrag) # Use RubberBandDrag for selection
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setBackgroundBrush(Qt.white)
        self.setInteractive(True) 
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded) # Default scrollbar policy
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCursor(Qt.ArrowCursor) # Default cursor

        # Initialize variables
        self.book_graph = None
        self.node_items = {}  
        self.edge_items = {}  
        
        # Panning state for middle-button
        self.is_panning = False
        self._last_pan_point = QPointF()
        
        # Edge creation state
        self.is_creating_edge = False
        self.edge_source_item = None
        self.temp_edge = None 
        self.edge_types = ["critical-path", "character-pov", "branch-point", "concept-sequence", "related-concept", "fiction-nonfiction", "default"]
        self.current_edge_type = "default" 

    # --- Graph Management Methods ---

    def set_book_graph(self, book_graph):
        """Set the book graph to display and refresh the view."""
        self.book_graph = book_graph
        self.refresh_graph()

    def refresh_graph(self):
        """Refresh the graph display based on the current book graph."""
        if not self.book_graph:
            print("GraphView: Cannot refresh, book_graph is not set.")
            self.scene.clear() 
            self.node_items.clear()
            self.edge_items.clear()
            return
        
        print("GraphView: Refreshing graph display...")
        try:
            current_transform = self.transform()
            selected_ids = [item.node.id for item in self.scene.selectedItems() if isinstance(item, GraphNodeItem)]
            positions = {node_id: item.pos() for node_id, item in self.node_items.items()}

            self.scene.clear()
            self.node_items.clear()
            self.edge_items.clear()
            
            nodes_added = 0
            all_nodes = self.book_graph.get_all_nodes() 
            for node in all_nodes:
                pos_data = node.position; initial_pos_tuple = (10.0, 10.0) # Default if error
                if isinstance(pos_data, (list, tuple)) and len(pos_data) == 2:
                     try: initial_pos_tuple = (float(pos_data[0]), float(pos_data[1]))
                     except (ValueError, TypeError): pass 
                
                initial_pos = positions.get(node.id, QPointF(*initial_pos_tuple)) 
                
                node_item = GraphNodeItem(node)
                node_item.setPos(initial_pos) 
                self.scene.addItem(node_item)
                self.node_items[node.id] = node_item
                nodes_added += 1
                
            edges_added = 0
            for edge in self.book_graph.get_all_edges(): 
                source_item = self.node_items.get(edge.source_id)
                target_item = self.node_items.get(edge.target_id)
                if source_item and target_item: 
                    edge_item = GraphEdgeItem(edge, source_item, target_item)
                    self.scene.addItem(edge_item)
                    self.edge_items[(edge.source_id, edge.target_id)] = edge_item
                    edges_added += 1
                else:
                     print(f"GraphView: Warning - Cannot draw edge {edge.source_id}->{edge.target_id}, node item missing.")

            for node_id in selected_ids:
                if node_id in self.node_items: 
                    self.node_items[node_id].setSelected(True)
                    
            self.setTransform(current_transform)
            print(f"GraphView: Graph refreshed. Added {nodes_added} nodes and {edges_added} edges.")
        except Exception as e:
             print(f"ERROR during GraphView.refresh_graph: {e}")
             traceback.print_exc()


    def update_node(self, node):
        """Update the visual appearance of a node."""
        node_item = self.node_items.get(node.id)
        if node_item: 
            try:
                node_item.node = node 
                node_item.update_appearance() 
                self.update_connected_edges(node_item) 
                # print(f"GraphView: Updated node item {node.id}") # Less verbose
            except Exception as e:
                 print(f"ERROR during GraphView.update_node for {node.id}: {e}")
                 traceback.print_exc()


    def update_edge(self, edge):
        """Update the visual appearance of an edge."""
        edge_key = (edge.source_id, edge.target_id)
        edge_item = self.edge_items.get(edge_key)
        if edge_item: 
            try:
                edge_item.edge = edge 
                edge_item.update_appearance() 
                # print(f"GraphView: Updated edge item {edge_key}") # Less verbose
            except Exception as e:
                 print(f"ERROR during GraphView.update_edge for {edge_key}: {e}")
                 traceback.print_exc()


    def update_connected_edges(self, node_item):
        """Helper to update paths of edges connected to a node."""
        if not node_item or not hasattr(node_item, 'node'): return
        node_id = node_item.node.id
        for edge_key, edge_item in self.edge_items.items():
            if node_id in edge_key: 
                try:
                    edge_item.update_path()
                except Exception as e:
                     print(f"ERROR during GraphView.update_connected_edges for edge {edge_key}: {e}")
                     traceback.print_exc()


    def add_node(self, node, position=None):
        """Add a new node visually to the graph view."""
        if not node or not hasattr(node, 'id'): print("GraphView: ERROR - Cannot add invalid node object."); return None
        if node.id in self.node_items: print(f"GraphView: Node item {node.id} already exists."); return self.node_items[node.id]
            
        try:
            node_item = GraphNodeItem(node)
            pos_tuple = (10.0, 10.0) # Default position
            
            pos_to_use = position if position else node.position
            if pos_to_use and isinstance(pos_to_use, (list, tuple)) and len(pos_to_use) == 2: 
                 try: pos_tuple = (float(pos_to_use[0]), float(pos_to_use[1]))
                 except (ValueError, TypeError): pass 
                 
            node_item.setPos(QPointF(*pos_tuple))
            if node.position != pos_tuple: node.position = pos_tuple 
                
            self.scene.addItem(node_item)
            self.node_items[node.id] = node_item
            print(f"GraphView: Added node item {node.id}")
            return node_item
        except Exception as e:
             print(f"ERROR during GraphView.add_node for {getattr(node, 'id', 'N/A')}: {e}")
             traceback.print_exc()
             return None


    def add_edge(self, edge):
        """Add a new edge visually to the graph view."""
        if not edge or not hasattr(edge, 'source_id') or not hasattr(edge, 'target_id'): print("GraphView: ERROR - Cannot add invalid edge object."); return None
        
        edge_key = (edge.source_id, edge.target_id)
        if edge_key in self.edge_items: print(f"GraphView: Edge item {edge_key} already exists."); return self.edge_items[edge_key]
            
        source_item = self.node_items.get(edge.source_id)
        target_item = self.node_items.get(edge.target_id)
        
        if source_item and target_item:
            try:
                edge_item = GraphEdgeItem(edge, source_item, target_item)
                self.scene.addItem(edge_item)
                self.edge_items[edge_key] = edge_item
                print(f"GraphView: Added edge item {edge_key}")
                return edge_item
            except Exception as e:
                 print(f"ERROR during GraphView.add_edge for {edge_key}: {e}")
                 traceback.print_exc()
                 return None
        else:
            print(f"GraphView: ERROR - Cannot add edge item {edge_key}, source or target node item not found.")
            return None

    def remove_node(self, node_id):
        """Remove a node and its connected edges visually from the graph view."""
        node_item = self.node_items.pop(node_id, None) 
        if node_item:
            try:
                edges_to_remove = []
                for edge_key in list(self.edge_items.keys()): 
                    if node_id in edge_key: 
                        edge_item = self.edge_items.pop(edge_key, None)
                        if edge_item: self.scene.removeItem(edge_item); edges_to_remove.append(edge_key) 
                self.scene.removeItem(node_item)
                print(f"GraphView: Removed node item {node_id} and {len(edges_to_remove)} edges.")
            except Exception as e:
                 print(f"ERROR during GraphView.remove_node for {node_id}: {e}")
                 traceback.print_exc()
                 # Attempt to restore item if removal failed partially? Complex.
        else:
             print(f"GraphView: Node item {node_id} not found for removal.")

    def remove_edge(self, source_id, target_id):
        """Remove an edge visually from the graph view."""
        edge_key = (source_id, target_id)
        edge_item = self.edge_items.pop(edge_key, None) 
        if edge_item:
            try:
                self.scene.removeItem(edge_item)
                print(f"GraphView: Removed edge item {edge_key}")
            except Exception as e:
                 print(f"ERROR during GraphView.remove_edge for {edge_key}: {e}")
                 traceback.print_exc()
                 # Add item back to dict if removal failed?
                 # self.edge_items[edge_key] = edge_item 
        else:
             print(f"GraphView: Edge item {edge_key} not found for removal.")

    def fit_in_view(self):
        """Fit all items in the view with padding."""
        try:
            if not self.scene.items(): return 
            rect = self.scene.itemsBoundingRect()
            rect.adjust(-50, -50, 50, 50) # Add padding
            self.fitInView(rect, Qt.KeepAspectRatio)
            print("GraphView: Fit content in view.")
        except Exception as e:
             print(f"ERROR during GraphView.fit_in_view: {e}")
             traceback.print_exc()


    # --- Edge Creation Methods ---

    def start_edge_creation(self, source_item, edge_type):
        """Initiate edge creation mode from a source node."""
        if not isinstance(source_item, GraphNodeItem): return
        try:
            self.is_creating_edge = True; self.edge_source_item = source_item; self.current_edge_type = edge_type
            color = GraphEdgeItem.TYPE_COLORS.get(edge_type, GraphEdgeItem.TYPE_COLORS["default"]); style = GraphEdgeItem.TYPE_STYLES.get(edge_type, GraphEdgeItem.TYPE_STYLES["default"]); pen = QPen(color, 2, style); pen.setCapStyle(Qt.RoundCap); pen.setJoinStyle(Qt.RoundJoin)
            start_pos = source_item.scenePos() + source_item.boundingRect().center(); self.temp_edge = self.scene.addLine(QLineF(start_pos, start_pos), pen); self.temp_edge.setZValue(-1) # Ensure edge is below nodes
            self.setCursor(Qt.CrossCursor); print(f"GraphView: Started edge creation from {source_item.node.id} (type: {edge_type})")
        except Exception as e:
             print(f"ERROR during GraphView.start_edge_creation: {e}")
             traceback.print_exc()
             self.cancel_edge_creation()


    def cancel_edge_creation(self):
        """Cancel the current edge creation process."""
        try:
            if self.is_creating_edge:
                if self.temp_edge: self.scene.removeItem(self.temp_edge); self.temp_edge = None
                self.is_creating_edge = False; self.edge_source_item = None; self.unsetCursor(); print("GraphView: Edge creation cancelled.")
        except Exception as e:
             print(f"ERROR during GraphView.cancel_edge_creation: {e}")
             traceback.print_exc()
             # Ensure state is reset even on error
             self.is_creating_edge = False; self.edge_source_item = None; self.temp_edge = None; self.unsetCursor(); 


    def finish_edge_creation(self, target_item):
        """Complete edge creation when a target node is clicked."""
        if not self.is_creating_edge or not self.edge_source_item or not target_item: print("GraphView: ERROR - Cannot finish edge creation, invalid state."); self.cancel_edge_creation(); return
        if not isinstance(target_item, GraphNodeItem): self.cancel_edge_creation(); return # Clicked on non-node
        if self.edge_source_item == target_item: print("GraphView: Cannot create self-loop."); self.cancel_edge_creation(); return
        
        try:
            if self.temp_edge: self.scene.removeItem(self.temp_edge); self.temp_edge = None
            self.is_creating_edge = False; self.unsetCursor()
            
            source_id = self.edge_source_item.node.id; target_id = target_item.node.id
            print(f"GraphView: Finishing edge creation: {source_id} -> {target_id} [{self.current_edge_type}]")
            
            if self.book_graph and self.book_graph.graph.has_edge(source_id, target_id): print(f"GraphView: Edge {source_id} -> {target_id} already exists."); return 
                
            edge = Edge(source_id=source_id, target_id=target_id, edge_type=self.current_edge_type)
            
            # Emit signal for DataManager to add edge to model first
            self.edge_created.emit(edge) 
            
            # Check if edge was successfully added to model before adding visually
            # Requires DataManager/MainWindow to potentially signal back or update graph synchronously
            # Simpler approach: Assume signal handler adds it, then add visually.
            # If model add fails, visual edge might appear temporarily until next refresh.
            if self.book_graph and self.book_graph.graph.has_edge(source_id, target_id):
                 self.add_edge(edge) # Add visually
                 print(f"GraphView: Edge created signal emitted and edge added visually.")
            else:
                 # This might happen if the signal handler didn't add it immediately
                 print(f"GraphView: Edge created signal emitted, but edge not found in model yet. Adding visually anyway.")
                 self.add_edge(edge) # Add visually anyway for responsiveness

        except Exception as e:
             print(f"ERROR during GraphView.finish_edge_creation: {e}")
             traceback.print_exc()
             self.cancel_edge_creation() # Ensure cleanup on error


    # --- Context Menu ---

    def contextMenuEvent(self, event):
        """Handle right-click context menu events."""
        try:
            scene_pos = self.mapToScene(event.pos())
            item = self.scene.itemAt(scene_pos, self.transform())
            menu = QMenu(self)
            
            if isinstance(item, GraphNodeItem):
                edit_action = QAction("Edit Node Properties", self, triggered=lambda: self.node_selected.emit(item.node))
                delete_action = QAction("Delete Node", self, triggered=lambda: self.delete_node(item.node)) 
                add_edge_menu = QMenu("Create Connection From Here", self)
                for edge_type in self.edge_types: 
                    action = QAction(edge_type.replace("-", " ").title(), self)
                    action.triggered.connect(lambda checked=False, src=item, type=edge_type: self.start_edge_creation(src, type))
                    add_edge_menu.addAction(action)
                menu.addAction(edit_action); menu.addMenu(add_edge_menu); menu.addSeparator(); menu.addAction(delete_action)
            elif isinstance(item, GraphEdgeItem):
                edit_action = QAction("Edit Connection Properties", self, triggered=lambda: self.edge_selected.emit(item.edge))
                delete_action = QAction("Delete Connection", self, triggered=lambda: self.delete_edge(item.edge)) 
                menu.addAction(edit_action); menu.addSeparator(); menu.addAction(delete_action)
            else: 
                add_node_action = QAction("Add Node Here", self) 
                # TODO: Implement add_node_at_pos if needed
                # add_node_action.triggered.connect(lambda: self.add_node_at_pos(scene_pos)) 
                menu.addAction(add_node_action); menu.addSeparator()
                fit_action = QAction("Fit in View", self, triggered=self.fit_in_view)
                menu.addAction(fit_action)

            menu.exec_(event.globalPos()) 
        except Exception as e:
             print(f"ERROR during GraphView.contextMenuEvent: {e}")
             traceback.print_exc()


    def delete_node(self, node):
        """Requests node deletion via parent."""
        try:
            print(f"GraphView: Requesting deletion of node {node.id}")
            # Trigger MainWindow's deletion logic
            if hasattr(self.parent(), 'on_delete_selected_node'): 
                self.scene.clearSelection() 
                node_item = self.node_items.get(node.id)
                if node_item: 
                    node_item.setSelected(True)
                    self.parent().on_delete_selected_node()
        except Exception as e:
             print(f"ERROR during GraphView.delete_node request for {getattr(node, 'id', 'N/A')}: {e}")
             traceback.print_exc()


    def delete_edge(self, edge):
        """Requests edge deletion via signal."""
        try:
            print(f"GraphView: Requesting deletion of edge {edge.source_id} -> {edge.target_id}")
            self.edge_deleted.emit(edge) # Signal MainWindow/DataManager
        except Exception as e:
             print(f"ERROR during GraphView.delete_edge request for {getattr(edge, 'source_id', 'N/A')}->{getattr(edge, 'target_id', 'N/A')}: {e}")
             traceback.print_exc()


    # --- Event Handling for Navigation and Interaction ---

    def mousePressEvent(self, event):
        """Handle mouse press events for selection and panning."""
        try:
            # --- Middle Button Panning Start ---
            if event.button() == Qt.MiddleButton:
                self.is_panning = True
                self._last_pan_point = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
                event.accept() 
                return 
            # --- End Middle Button ---
                
            if event.button() == Qt.LeftButton:
                 if self.is_creating_edge:
                      # Handle edge creation click
                      scene_pos = self.mapToScene(event.pos())
                      item = self.scene.itemAt(scene_pos, self.transform())
                      if isinstance(item, GraphNodeItem): self.finish_edge_creation(item)
                      else: self.cancel_edge_creation()
                      event.accept(); return
                 else: 
                     # Handle left-click selection (using RubberBandDrag)
                     super().mousePressEvent(event) # Let base class handle selection/drag start
                     selected_items = self.scene.selectedItems()
                     if len(selected_items) == 1:
                          item = selected_items[0]
                          if isinstance(item, GraphNodeItem): self.node_selected.emit(item.node)
                          elif isinstance(item, GraphEdgeItem): self.edge_selected.emit(item.edge)
                     elif len(selected_items) == 0 and self.itemAt(event.pos()) is None:
                          self.selection_cleared.emit() 
                     # Don't accept yet, super() might start a drag
                     return

            # Handle other buttons (Right for context menu)
            super().mousePressEvent(event) 
        except Exception as e:
             print(f"ERROR during GraphView.mousePressEvent: {e}")
             traceback.print_exc()

    def mouseMoveEvent(self, event):
        """Handle mouse move events for panning and edge creation."""
        try:
            # --- Middle Button Panning Move ---
            if self.is_panning:
                delta = event.pos() - self._last_pan_point
                h_bar = self.horizontalScrollBar(); v_bar = self.verticalScrollBar()
                h_bar.setValue(h_bar.value() - delta.x())
                v_bar.setValue(v_bar.value() - delta.y())
                self._last_pan_point = event.pos()
                event.accept() 
                return 
            # --- End Middle Button ---
                
            if self.is_creating_edge and self.temp_edge and self.edge_source_item:
                start_pos = self.edge_source_item.scenePos() + self.edge_source_item.boundingRect().center()
                end_pos = self.mapToScene(event.pos())
                self.temp_edge.setLine(QLineF(start_pos, end_pos)) 
                event.accept(); return
                
            # Let base class handle other movements (drag selection box or item drag)
            super().mouseMoveEvent(event)
            
            # Update connected edges if an item is being dragged by the base class
            if event.buttons() & Qt.LeftButton and self.dragMode() == QGraphicsView.RubberBandDrag:
                selected_nodes = [item for item in self.scene.selectedItems() if isinstance(item, GraphNodeItem)]
                if selected_nodes:
                     for node_item in selected_nodes:
                          self.update_connected_edges(node_item)
        except Exception as e:
             print(f"ERROR during GraphView.mouseMoveEvent: {e}")
             traceback.print_exc()


    def mouseReleaseEvent(self, event):
        """Handle mouse release events for panning and node movement signals."""
        try:
            # --- Middle Button Panning End ---
            if event.button() == Qt.MiddleButton and self.is_panning:
                self.is_panning = False
                self.setCursor(Qt.ArrowCursor) # Restore cursor
                event.accept() 
                return 
            # --- End Middle Button ---
                
            # Let base class handle release first
            super().mouseReleaseEvent(event)

            # Emit node_moved signal after left button release if nodes were moved
            if event.button() == Qt.LeftButton and not self.is_creating_edge: 
                 moved_items = [item for item in self.scene.selectedItems() if isinstance(item, GraphNodeItem)]
                 # Check if node position actually changed (more complex)
                 # Simplified: Emit for any selected node after left-release
                 if moved_items:
                      for item in moved_items:
                           self.update_connected_edges(item) # Ensure edges are updated
                           self.node_moved.emit(item.node) # Emit signal
                      if not event.isAccepted(): event.accept() # Accept if we handled it
                      return # Return after handling node move emission

            # Accept event if not already handled
            if not event.isAccepted():
                 event.accept()
        except Exception as e:
             print(f"ERROR during GraphView.mouseReleaseEvent: {e}")
             traceback.print_exc()


    def wheelEvent(self, event: QWheelEvent): 
        """Handle wheel events for zooming."""
        try:
            zoom_factor = 1.15
            if event.angleDelta().y() < 0:
                zoom_factor = 1.0 / zoom_factor
            
            # Anchor is set to AnchorUnderMouse in __init__
            self.scale(zoom_factor, zoom_factor)
            
            event.accept() # We handled the zoom
        except Exception as e:
             print(f"ERROR during GraphView.wheelEvent: {e}")
             traceback.print_exc()


    def keyPressEvent(self, event: QKeyEvent): 
        """Handle key press events."""
        try:
            if event.key() == Qt.Key_Escape and self.is_creating_edge:
                self.cancel_edge_creation(); event.accept(); return
                
            super().keyPressEvent(event) # Pass other keys to base class
        except Exception as e:
             print(f"ERROR during GraphView.keyPressEvent: {e}")
             traceback.print_exc()

