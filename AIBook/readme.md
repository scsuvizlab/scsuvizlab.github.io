# Interactive Book Editor

An application for creating and managing node-based interactive book structures. This tool allows authors to visualize and edit the complex relationships between different content nodes in an interactive book.

## Features

- Create and edit nodes representing different types of content (fiction scenes, non-fiction articles, character profiles, etc.)
- Define connections between nodes (critical path, character perspectives, related concepts, etc.)
- Visualize the book structure as an interactive graph
- Edit node and connection properties
- Organize nodes into chapters
- Import and export node content
- Save and load book structure projects

## Getting Started

### Prerequisites

- Python 3.6 or higher
- PyQt5
- NetworkX

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/interactive-book-editor.git
   cd interactive-book-editor
   ```

2. Install dependencies:
   ```
   pip install PyQt5 networkx
   ```

3. Run the application:
   ```
   python main.py
   ```

### Basic Usage

1. **Creating a new project**:
   - Select `File > New Project...` and choose a directory for your project
   - The application will create the necessary directory structure

2. **Opening an existing project**:
   - Select `File > Open Project...` and choose the project directory

3. **Adding nodes**:
   - Right-click on the graph area and select `Add Node`
   - Enter a unique ID, type, and title for the node

4. **Adding connections**:
   - Right-click on a node and select `Add Connection > [Connection Type]`
   - Click on the target node to complete the connection

5. **Editing properties**:
   - Select a node or connection to view and edit its properties in the Properties panel

6. **Saving your project**:
   - Select `File > Save` or press `Ctrl+S`

## Project Structure

The application uses a specific directory structure for projects:

```
project-root/
├── content/                  # All content files
│   ├── book-structure.json   # Main structure file
│   ├── fiction/
│   │   ├── critical_path/    # Main story nodes
│   │   └── character_povs/   # Character perspective nodes
│   ├── nonfiction/           # Educational content nodes
│   ├── characters/           # Character profile nodes
│   └── world/                # World entity nodes
```

## File Formats

### book-structure.json

This file contains the structure of the entire book, including nodes, connections, and metadata:

```json
{
  "title": "Book Title",
  "author": "Author Name",
  "version": "1.0",
  "defaultStartNode": "node-id",
  "defaultPOV": "Omniscient",
  "criticalPath": [
    {
      "id": "node-id",
      "title": "Node Title",
      "type": "fiction",
      "chapter": "chapter1",
      "nextNode": "next-node-id"
    },
    // More nodes...
  ],
  "chapters": [
    {
      "id": "chapter1",
      "title": "Chapter 1",
      "description": "Chapter description",
      "nodes": ["node-id", "another-node-id"]
    },
    // More chapters...
  ],
  "characterPOVs": {
    "base-node-id": [
      {
        "character": "Character Name",
        "nodeId": "character-pov-node-id",
        "filePath": "fiction/character_povs/character-pov-node-id.json"
      },
      // More POVs...
    ]
  },
  "relatedContent": {
    "fiction-node-id": ["nonfiction-node-id1", "nonfiction-node-id2"],
    // More relationships...
  },
  "node_positions": {
    "node-id": [x, y],
    // More positions...
  }
}
```

### Node Content Files

Each node has its own content file with the specific details for that node:

```json
{
  "nodeId": "node-id",
  "nodeType": "fiction",
  "data": {
    "label": "Node Title",
    "chapterTitle": "Chapter 1",
    "subtitle": "A New Beginning",
    "location": "Location Name",
    "timeline": "Timeline Info",
    "tags": ["tag1", "tag2"],
    "povCharacter": "Character Name",
    "content": "<p>HTML content goes here...</p>"
  },
  "metadata": {
    "author": "Author Name",
    "lastModified": "2023-08-15T12:34:56Z"
  },
  "navigation": {
    "next": "next-node-id",
    "previous": "previous-node-id",
    "alternateVersions": [
      {
        "povCharacter": "Another Character",
        "nodeId": "alternate-pov-node-id"
      }
    ],
    "relatedNonFiction": ["nonfiction-node-id1", "nonfiction-node-id2"]
  }
}
```

## Keyboard Shortcuts

- `Ctrl+N`: New Project
- `Ctrl+O`: Open Project
- `Ctrl+S`: Save Project
- `Ctrl+Shift+S`: Save Project As
- `Ctrl+Q`: Exit
- `Delete`: Delete Selected Node/Connection
- `Ctrl++`: Zoom In
- `Ctrl+-`: Zoom Out
- `Ctrl+0`: Fit to View

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with PyQt5 for the user interface
- Uses NetworkX for graph data structures
