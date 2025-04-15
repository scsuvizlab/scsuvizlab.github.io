"""
GraphNodeItem and GraphEdgeItem classes for the Interactive Book Editor.
These classes handle the visual representation of nodes and edges in the graph view.
"""

import math
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QPainterPath, QFont

class GraphNodeItem(QGraphicsEllipseItem):
    """
    Visual representation of a node in the graph view.
    
    Displays a node as a colored circle with a label for the title.
    """
    
    # Node type color map
    TYPE_COLORS = {
        "book": QColor(255, 215, 0),  # Gold
        "fiction": QColor(110, 207, 246),  # Light blue
        "nonfiction": QColor(147, 112, 219),  # Medium purple
        "character": QColor(32, 178, 170),  # Light sea green
        "interactive": QColor(186, 85, 211),  # Medium orchid
        "world": QColor(205, 133, 63),  # Peru (brownish)
        "default": QColor(200, 200, 200)  # Light gray
    }
    
    def __init__(self, node, parent=None):
        """
        Initialize a new GraphNodeItem.
        
        Args:
            node (Node): The node to display
            parent (QGraphicsItem, optional): Parent item
        """
        # Use a different size for book nodes
        node_radius = 40 if node.node_type == "book" else 30
        
        # Create a circle with the appropriate radius
        super().__init__(-node_radius, -node_radius, node_radius * 2, node_radius * 2, parent)
        self.node = node
        
        # Ensure the item is selectable and movable
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        
        # Ensure the item receives context menu events
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        
        self.setZValue(1)  # Make sure nodes appear above edges
        
        # Set position from node data
        x, y = node.position
        self.setPos(x, y)
        
        # Set appearance based on node type
        node_type = node.node_type or "default"
        color = self.TYPE_COLORS.get(node_type, self.TYPE_COLORS["default"])
        self.setBrush(QBrush(color))
        
        # Use a thicker border for book nodes
        pen_width = 2 if node.node_type == "book" else 1
        self.setPen(QPen(Qt.black, pen_width))
        
        # Add title text
        self.title_item = QGraphicsTextItem(node.title, self)
        
        # Use bold font for book nodes
        font = QFont("Arial", 10)
        if node.node_type == "book":
            font.setBold(True)
        self.title_item.setFont(font)
        
        # Make text transparent to mouse events
        self.title_item.setFlag(QGraphicsItem.ItemIgnoresParentOpacity, False)
        self.title_item.setAcceptedMouseButtons(Qt.NoButton)
        
        # Center the text on the node
        text_width = self.title_item.boundingRect().width()
        text_height = self.title_item.boundingRect().height()
        self.title_item.setPos(-text_width/2, -text_height/2)
    
    def itemChange(self, change, value):
        """
        Handle changes to the item, particularly position changes.
        
        Args:
            change: Type of change
            value: New value
            
        Returns:
            Updated value
        """
        # When the position changes, update the node position in the data model
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            # Update the node position
            new_pos = value
            self.node.position = (new_pos.x(), new_pos.y())
        
        return super().itemChange(change, value)
    
    def update_appearance(self):
        """Update the appearance based on the current node data."""
        # Update position
        x, y = self.node.position
        self.setPos(x, y)
        
        # Update color based on node type
        node_type = self.node.node_type or "default"
        color = self.TYPE_COLORS.get(node_type, self.TYPE_COLORS["default"])
        self.setBrush(QBrush(color))
        
        # Update title
        self.title_item.setPlainText(self.node.title)
        
        # Re-center the text
        text_width = self.title_item.boundingRect().width()
        text_height = self.title_item.boundingRect().height()
        self.title_item.setPos(-text_width/2, -text_height/2)
        
        # Check if node type changed
        node_radius = 40 if self.node.node_type == "book" else 30
        current_radius = self.rect().width() / 2
        
        if node_radius != current_radius:
            # Update the circle size
            self.setRect(-node_radius, -node_radius, node_radius * 2, node_radius * 2)
            
            # Update the pen width
            pen_width = 2 if self.node.node_type == "book" else 1
            self.setPen(QPen(Qt.black, pen_width))
            
            # Update font
            font = QFont("Arial", 10)
            if self.node.node_type == "book":
                font.setBold(True)
            self.title_item.setFont(font)


class GraphEdgeItem(QGraphicsPathItem):
    """
    Visual representation of an edge in the graph view.
    
    Displays a connection between two nodes as a line with an arrow.
    """
    
    # Edge type color map
    TYPE_COLORS = {
        "critical-path": QColor(255, 215, 0),  # Gold
        "character-pov": QColor(110, 207, 246),  # Light blue
        "branch-point": QColor(255, 140, 0),  # Dark orange
        "concept-sequence": QColor(147, 112, 219),  # Medium purple
        "related-concept": QColor(60, 179, 113),  # Medium sea green
        "fiction-nonfiction": QColor(255, 105, 180),  # Hot pink
        "default": QColor(150, 150, 150)  # Gray
    }
    
    # Edge type line style
    TYPE_STYLES = {
        "critical-path": Qt.SolidLine,
        "character-pov": Qt.DashLine,
        "branch-point": Qt.SolidLine,
        "concept-sequence": Qt.DotLine,
        "related-concept": Qt.DashDotLine,
        "fiction-nonfiction": Qt.DashDotDotLine,
        "default": Qt.SolidLine
    }
    
    def __init__(self, edge, source_item, target_item, parent=None):
        """
        Initialize a new GraphEdgeItem.
        
        Args:
            edge (Edge): The edge to display
            source_item (GraphNodeItem): Source node item
            target_item (GraphNodeItem): Target node item
            parent (QGraphicsItem, optional): Parent item
        """
        super().__init__(parent)
        self.edge = edge
        self.source_item = source_item
        self.target_item = target_item
        self.setZValue(0)  # Make sure edges appear below nodes
        
        # Set appearance based on edge type
        self.update_appearance()
    
    def update_path(self):
        """Update the edge path based on source and target positions."""
        # Get the circles representing the nodes
        source_rect = self.source_item.rect()
        target_rect = self.target_item.rect()
        
        # Get the center points of the nodes
        source_center = self.source_item.pos()
        target_center = self.target_item.pos()
        
        # Calculate the angle between the nodes
        dx = target_center.x() - source_center.x()
        dy = target_center.y() - source_center.y()
        angle = math.atan2(dy, dx)
        
        # Get the radius of the nodes (assuming they're circles)
        source_radius = source_rect.width() / 2
        target_radius = target_rect.width() / 2
        
        # Calculate connection points on the perimeter of the circles
        source_x = source_center.x() + source_radius * math.cos(angle)
        source_y = source_center.y() + source_radius * math.sin(angle)
        
        target_x = target_center.x() - target_radius * math.cos(angle)
        target_y = target_center.y() - target_radius * math.sin(angle)
        
        # Draw the path
        path = QPainterPath()
        path.moveTo(source_x, source_y)
        path.lineTo(target_x, target_y)
        
        # Add arrowhead at the target end
        arrow_size = 10
        arrow_angle = math.pi / 6  # 30 degrees
        
        # Calculate arrowhead points
        angle1 = angle + math.pi - arrow_angle
        angle2 = angle + math.pi + arrow_angle
        
        arrow_p1 = QPointF(
            target_x + arrow_size * math.cos(angle1),
            target_y + arrow_size * math.sin(angle1)
        )
        
        arrow_p2 = QPointF(
            target_x + arrow_size * math.cos(angle2),
            target_y + arrow_size * math.sin(angle2)
        )
        
        # Add the arrowhead to the path
        path.moveTo(target_x, target_y)
        path.lineTo(arrow_p1.x(), arrow_p1.y())
        path.moveTo(target_x, target_y)
        path.lineTo(arrow_p2.x(), arrow_p2.y())
        
        self.setPath(path)
    
    def update_appearance(self):
        """Update the appearance based on the current edge data."""
        # Update the path
        self.update_path()
        
        # Set color and style based on edge type
        edge_type = self.edge.edge_type or "default"
        color = self.TYPE_COLORS.get(edge_type, self.TYPE_COLORS["default"])
        style = self.TYPE_STYLES.get(edge_type, self.TYPE_STYLES["default"])
        
        pen = QPen(color, 2, style)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(pen)