Okay, creating a features document is a great way to solidify the vision for this tool, especially aiming for it to be general-purpose.

Here's a draft based on our conversation, outlining the intent, current state (based on the code skeletons we've defined), requested next steps, and potential future enhancements:

## **Interactive Book Editor \- Features Document**

### **1\. Application Purpose & Intent**

**Goal:** To provide a general-purpose, desktop-based graphical application (built in Python with PyQt5) for authors and designers to create, visualize, manage, and edit the structure of node-based interactive narratives or books.

**Core Function:** The application allows users to define different types of content nodes (scenes, non-fiction articles, character profiles, etc.), connect them using various relationship types (critical path, alternate perspectives, related concepts, branches), and manage associated metadata and content files. It operates primarily on a project folder containing a central book-structure.json file and associated content files within a content subdirectory. The visual graph interface provides an intuitive way to understand and manipulate the narrative flow.

### **2\. Core Features (MVP based on Code Skeletons)**

These are the core features which define an MVP

* **Project Loading:** Loads an existing project structure from a specified root directory containing content/book-structure.json. (BookGraph, DataManager, MainWindow)  
* **Data Modeling:** Represents the book structure internally using Node, Edge, and BookGraph classes, leveraging NetworkX for graph relationships.  
* **Graph Visualization:** Displays nodes and edges in a 2D view (GraphView, GraphNodeItem, GraphEdgeItem).  
  * Nodes are colored based on their node\_type.  
  * Edges are styled (color, line style) based on their edge\_type.  
  * Initial node positions are loaded from book-structure.json.  
* **Basic Interaction:**  
  * **Panning:** Dragging the background pans the view (GraphView).  
  * **Zooming:** Using the mouse wheel zooms the view (GraphView).  
  * **Node Selection:** Clicking a node selects it visually (GraphView).  
  * **Node Dragging:** Selected nodes can be dragged to new positions (GraphView, GraphNodeItem). Moved positions are updated in the data model (BookGraph).  
* **Property Viewing/Editing:** Displays properties of the selected node in a separate panel (PropertiesEditor).  
  * Shows Node ID, Type, Title, Content Path.  
  * Allows editing of Title and Content Path (basic implementation).  
  * Shows Edge Type, Source/Target IDs, and properties (as text) for selected edges.  
* **Project Saving:** Saves the current structure (including updated node positions and potentially modified node titles/paths) back to the book-structure.json file via a "File \> Save" action (MainWindow, BookGraph, DataManager).  
* **Basic UI:** Provides a main window with a menu bar, a central graph display area, and a dockable properties editor panel (MainWindow).  
* **Code Structure:** Organized into distinct classes following the provided style guide.

### **3\. Planned Features (Next Level \- User Requests)**

These are the features identified for the next stage of development:

* **User-Initiated Project Loading:** Implement "File \> Open Project..." allowing users to browse and select the project root directory, replacing any hardcoded initial loading (MainWindow).  
* **Import External Node:** Add functionality ("File \> Import Node...") to select an external JSON file, parse it, copy it into the project's content directory, create a corresponding Node object and visual item, and place it near a reference node on the graph (MainWindow, DataManager, BookGraph, GraphView).  
* **Visual Edge Creation:** Implement a mechanism (e.g., right-click on a source node \-\> select connection type \-\> click on a target node) to draw new connections between nodes directly on the graph (GraphView, MainWindow, BookGraph).  
* **Left-to-Right Connection Points:** Modify edge drawing logic so edges connect to the center-right side of the source node and the center-left side of the target node, enhancing visual flow (GraphView).  
* **Node Auto-Save:** Automatically save changes made to a node's *content file* (via the PropertiesEditor) back to its specific JSON file as the edits are made (PropertiesEditor, DataManager). *Note: This does not apply to the main book-structure.json.*  
* **Book Overview Table:** Replace the content preview in the PropertiesEditor with a new table view (likely in MainWindow) displaying a list of all nodes in the project (ID, Title, Type, Chapter, etc.).  
* **Synced Selection:** Link the graph view and the new table view so that selecting a node in one automatically selects and highlights the corresponding entry in the other (MainWindow, GraphView, Table Widget).  
* **Chapter Definition:** Formalize chapter management. While chapter data resides in book-structure.json, add UI elements to create/edit chapters and assign nodes to them.

### **4\. Potential Backlog Features (Quality of Life / Future Enhancements)**

These are additional features that would further enhance the tool's usability and capabilities:

* **Undo/Redo:** Implement an undo/redo stack for actions like node/edge creation, deletion, movement, and property changes.  
* **Automatic Layout Algorithms:** Integrate options (e.g., via buttons or menu actions) to apply graph layout algorithms (hierarchical, force-directed) to automatically arrange nodes.  
* **Search & Filter:** Add a search bar to find nodes by ID/title and options to filter the graph/table view (e.g., show only 'fiction' nodes, show only 'Chapter 2' nodes).  
* **Minimap:** Provide a small overview panel for navigating large graphs.  
* **Node Content Editor:** Implement a more robust editor for the main node content (potentially a pop-up window triggered from the PropertiesEditor or table, maybe with Markdown/rich text support).  
* **Validation & Error Reporting:** Add checks for structural integrity (e.g., disconnected critical path nodes, missing files) and provide clearer feedback to the user on errors.  
* **Visual Customization:** Allow users to configure default colors, node shapes, etc.  
* **Keyboard Shortcuts:** Define shortcuts for common operations.  
* **Grouping / Subgraphs:** Allow visual grouping of related nodes.  
* **Advanced Edge Editing:** Allow editing edge properties (like branch conditions) via the UI.  
* **Export Graph Image:** Add functionality to export the current graph view as a PNG or SVG file.

This document provides a comprehensive overview. We have a solid foundation with the MVP structure, a clear set of next steps based on your requirements, and a good list of potential future improvements to make this a powerful, general-purpose tool.