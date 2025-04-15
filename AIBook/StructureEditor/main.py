"""
Main entry point for the Interactive Book Editor application.
"""

import sys
from PyQt5.QtWidgets import QApplication
# This is the line causing the error if MainWindow isn't defined yet
from main_window import MainWindow 

def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Interactive Book Editor")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    # Add a print statement for debugging import order
    print("Running main.py...") 
    main()
