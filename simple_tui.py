#!/usr/bin/env python3
"""
VoidLink Simple Terminal User Interface

A simplified text-based user interface for VoidLink that runs in the terminal.
"""

import os
import sys
import time
import curses
import logging
from curses import panel

# Add the current directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('voidlink_tui')

# Try to import VoidLink modules
try:
    import simple_authentication as authentication
    import simple_encryption as encryption
    import simple_file_security as file_security
    import simple_file_transfer as file_transfer
    VOIDLINK_MODULES_LOADED = True
    logger.info("VoidLink modules loaded successfully")
except ImportError as e:
    logger.warning(f"Some VoidLink modules could not be imported: {e}")
    logger.warning("Running in demo mode")
    VOIDLINK_MODULES_LOADED = False

# Constants
VERSION = "1.0.0"
DEMO_FILES = [
    {"name": "Project_Proposal.pdf", "size": "1.2 MB", "date": "2023-03-15", "type": "PDF"},
    {"name": "Vacation_Photo.jpg", "size": "3.5 MB", "date": "2023-03-14", "type": "Image"},
    {"name": "Meeting_Notes.docx", "size": "245 KB", "date": "2023-03-12", "type": "Document"},
    {"name": "Budget_2023.xlsx", "size": "1.8 MB", "date": "2023-03-08", "type": "Spreadsheet"},
    {"name": "Presentation.pptx", "size": "5.2 MB", "date": "2023-03-05", "type": "Presentation"},
    {"name": "Source_Code.zip", "size": "10.1 MB", "date": "2023-03-01", "type": "Archive"},
]

class SimpleMenu:
    """Simple menu class for the TUI"""
    
    def __init__(self, items, title="Menu"):
        """Initialize the menu"""
        self.window = None
        self.panel = None
        self.title = title
        self.items = items
        self.position = 0
    
    def init_window(self, height, width, y, x):
        """Initialize the window"""
        self.window = curses.newwin(height, width, y, x)
        self.window.keypad(True)
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()
    
    def navigate(self, key):
        """Navigate the menu"""
        if key == curses.KEY_UP:
            self.position = max(0, self.position - 1)
        elif key == curses.KEY_DOWN:
            self.position = min(len(self.items) - 1, self.position + 1)
    
    def display(self):
        """Display the menu"""
        self.panel.top()
        self.panel.show()
        self.window.clear()
        
        # Draw border and title
        self.window.box()
        self.window.addstr(0, 2, f" {self.title} ")
        
        # Draw menu items
        for i, item in enumerate(self.items):
            if i == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            
            self.window.addstr(i + 1, 2, item, mode)
        
        self.window.refresh()
        panel.update_panels()
        curses.doupdate()
    
    def hide(self):
        """Hide the menu"""
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()

class SimpleDialog:
    """Simple dialog class for the TUI"""
    
    def __init__(self, title="Dialog", message=""):
        """Initialize the dialog"""
        self.window = None
        self.panel = None
        self.title = title
        self.message = message
    
    def init_window(self, height, width, y, x):
        """Initialize the window"""
        self.window = curses.newwin(height, width, y, x)
        self.window.keypad(True)
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()
    
    def display(self):
        """Display the dialog"""
        self.panel.top()
        self.panel.show()
        self.window.clear()
        
        # Draw border and title
        self.window.box()
        self.window.addstr(0, 2, f" {self.title} ")
        
        # Draw message
        lines = self.message.split("\n")
        for i, line in enumerate(lines):
            self.window.addstr(i + 1, 2, line)
        
        # Draw footer
        self.window.addstr(self.window.getmaxyx()[0] - 2, 2, "Press any key to continue...")
        
        self.window.refresh()
        panel.update_panels()
        curses.doupdate()
    
    def wait_for_key(self):
        """Wait for a key press"""
        self.window.getch()
    
    def hide(self):
        """Hide the dialog"""
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()

class SimpleForm:
    """Simple form class for the TUI"""
    
    def __init__(self, fields, title="Form"):
        """Initialize the form"""
        self.window = None
        self.panel = None
        self.title = title
        self.fields = fields
        self.values = [""] * len(fields)
        self.position = 0
    
    def init_window(self, height, width, y, x):
        """Initialize the window"""
        self.window = curses.newwin(height, width, y, x)
        self.window.keypad(True)
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()
    
    def navigate(self, key):
        """Navigate the form"""
        if key == curses.KEY_UP:
            self.position = max(0, self.position - 1)
        elif key == curses.KEY_DOWN:
            self.position = min(len(self.fields) - 1, self.position + 1)
    
    def edit_field(self):
        """Edit the current field"""
        curses.echo()
        self.window.move(self.position + 1, len(self.fields[self.position]) + 4)
        self.values[self.position] = self.window.getstr().decode('utf-8')
        curses.noecho()
    
    def display(self):
        """Display the form"""
        self.panel.top()
        self.panel.show()
        self.window.clear()
        
        # Draw border and title
        self.window.box()
        self.window.addstr(0, 2, f" {self.title} ")
        
        # Draw form fields
        for i, field in enumerate(self.fields):
            if i == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            
            self.window.addstr(i + 1, 2, field, mode)
            self.window.addstr(i + 1, len(field) + 4, self.values[i])
        
        # Draw footer
        self.window.addstr(self.window.getmaxyx()[0] - 2, 2, "Enter: Edit field | Esc: Cancel | F10: Submit")
        
        self.window.refresh()
        panel.update_panels()
        curses.doupdate()
    
    def hide(self):
        """Hide the form"""
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()

class SimpleTable:
    """Simple table class for the TUI"""
    
    def __init__(self, headers, data, title="Table"):
        """Initialize the table"""
        self.window = None
        self.panel = None
        self.title = title
        self.headers = headers
        self.data = data
        self.position = 0
        self.offset = 0
        self.max_rows = 0
    
    def init_window(self, height, width, y, x):
        """Initialize the window"""
        self.window = curses.newwin(height, width, y, x)
        self.window.keypad(True)
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()
        self.max_rows = height - 4  # Subtract border, header, and footer
    
    def navigate(self, key):
        """Navigate the table"""
        if key == curses.KEY_UP:
            if self.position > 0:
                self.position -= 1
                if self.position < self.offset:
                    self.offset = self.position
        elif key == curses.KEY_DOWN:
            if self.position < len(self.data) - 1:
                self.position += 1
                if self.position >= self.offset + self.max_rows:
                    self.offset = self.position - self.max_rows + 1
    
    def display(self):
        """Display the table"""
        self.panel.top()
        self.panel.show()
        self.window.clear()
        
        # Draw border and title
        self.window.box()
        self.window.addstr(0, 2, f" {self.title} ")
        
        # Calculate column widths
        width = self.window.getmaxyx()[1] - 4
        col_width = width // len(self.headers)
        
        # Draw headers
        for i, header in enumerate(self.headers):
            self.window.addstr(1, 2 + i * col_width, header[:col_width - 1])
        
        # Draw separator
        self.window.hline(2, 1, curses.ACS_HLINE, width + 2)
        
        # Draw data
        for i in range(min(self.max_rows, len(self.data) - self.offset)):
            row = self.data[i + self.offset]
            for j, cell in enumerate(row):
                if i + self.offset == self.position:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL
                
                self.window.addstr(i + 3, 2 + j * col_width, str(cell)[:col_width - 1], mode)
        
        # Draw footer
        self.window.addstr(self.window.getmaxyx()[0] - 2, 2, f"Item {self.position + 1} of {len(self.data)}")
        
        self.window.refresh()
        panel.update_panels()
        curses.doupdate()
    
    def hide(self):
        """Hide the table"""
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()

class SimpleTUI:
    """Simple Terminal User Interface for VoidLink"""
    
    def __init__(self):
        """Initialize the TUI"""
        self.screen = None
        self.username = None
        self.current_menu = None
        self.running = True
    
    def init_curses(self):
        """Initialize curses"""
        self.screen = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)
        self.screen.bkgd(curses.color_pair(1))
    
    def cleanup_curses(self):
        """Clean up curses"""
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()
    
    def draw_header(self):
        """Draw the header"""
        height, width = self.screen.getmaxyx()
        header = f"VoidLink v{VERSION}"
        if self.username:
            header += f" - Logged in as {self.username}"
        
        self.screen.addstr(0, 0, header.center(width))
        self.screen.hline(1, 0, curses.ACS_HLINE, width)
    
    def draw_footer(self):
        """Draw the footer"""
        height, width = self.screen.getmaxyx()
        footer = "Press 'q' to quit"
        
        self.screen.hline(height - 2, 0, curses.ACS_HLINE, width)
        self.screen.addstr(height - 1, 0, footer.center(width))
    
    def show_message(self, title, message):
        """Show a message dialog"""
        height, width = self.screen.getmaxyx()
        dialog = SimpleDialog(title, message)
        dialog.init_window(10, 40, (height - 10) // 2, (width - 40) // 2)
        dialog.display()
        dialog.wait_for_key()
        dialog.hide()
    
    def show_login_form(self):
        """Show the login form"""
        height, width = self.screen.getmaxyx()
        form = SimpleForm(["Username:", "Password:"], "Login")
        form.init_window(8, 40, (height - 8) // 2, (width - 40) // 2)
        
        while True:
            form.display()
            key = form.window.getch()
            
            if key == 27:  # Esc
                form.hide()
                return None, None
            elif key == curses.KEY_F10:
                form.hide()
                return form.values[0], form.values[1]
            elif key == 10:  # Enter
                form.edit_field()
            else:
                form.navigate(key)
    
    def show_main_menu(self):
        """Show the main menu"""
        height, width = self.screen.getmaxyx()
        menu_items = [
            "Login",
            "Exit"
        ]
        
        menu = SimpleMenu(menu_items, "Main Menu")
        menu.init_window(len(menu_items) + 2, 20, (height - len(menu_items) - 2) // 2, (width - 20) // 2)
        
        while True:
            menu.display()
            key = menu.window.getch()
            
            if key == 27:  # Esc
                menu.hide()
                return None
            elif key == 10:  # Enter
                menu.hide()
                return menu.position
            else:
                menu.navigate(key)
    
    def show_user_menu(self):
        """Show the user menu"""
        height, width = self.screen.getmaxyx()
        menu_items = [
            "List Files",
            "Upload File",
            "Download File",
            "Share File",
            "Delete File",
            "Logout"
        ]
        
        menu = SimpleMenu(menu_items, "User Menu")
        menu.init_window(len(menu_items) + 2, 20, (height - len(menu_items) - 2) // 2, (width - 20) // 2)
        
        while True:
            menu.display()
            key = menu.window.getch()
            
            if key == 27:  # Esc
                menu.hide()
                return None
            elif key == 10:  # Enter
                menu.hide()
                return menu.position
            else:
                menu.navigate(key)
    
    def show_file_list(self):
        """Show the file list"""
        height, width = self.screen.getmaxyx()
        
        # Get files
        if VOIDLINK_MODULES_LOADED:
            try:
                files = file_transfer.get_file_list(self.username)
                if not files:
                    self.show_message("Files", "No files found.")
                    return None
                
                headers = ["Name", "Size", "Date", "Type"]
                data = [[f["name"], f["size"], f["date"], f["type"]] for f in files]
            except Exception as e:
                self.show_message("Error", f"Error listing files: {str(e)}")
                return None
        else:
            # Demo mode
            headers = ["Name", "Size", "Date", "Type"]
            data = [[f["name"], f["size"], f["date"], f["type"]] for f in DEMO_FILES]
        
        table = SimpleTable(headers, data, "Files")
        table.init_window(min(len(data) + 5, height - 4), width - 4, 2, 2)
        
        while True:
            table.display()
            key = table.window.getch()
            
            if key == 27:  # Esc
                table.hide()
                return None
            elif key == 10:  # Enter
                table.hide()
                return table.position
            else:
                table.navigate(key)
    
    def login(self):
        """Log in to the system"""
        username, password = self.show_login_form()
        if not username or not password:
            return False
        
        # Authenticate
        if VOIDLINK_MODULES_LOADED:
            try:
                success = authentication.authenticate_user(username, password)
                if success:
                    self.username = username
                    self.show_message("Login", f"Welcome, {username}!")
                    return True
                else:
                    self.show_message("Login Failed", "Invalid username or password.")
                    return False
            except Exception as e:
                self.show_message("Error", f"Authentication error: {str(e)}")
                return False
        else:
            # Demo mode
            if username == "admin" and password == "admin123":
                self.username = username
                self.show_message("Login", f"Welcome, {username}!")
                return True
            elif username == "user" and password == "user123":
                self.username = username
                self.show_message("Login", f"Welcome, {username}!")
                return True
            elif username == "demo" and password == "password":
                self.username = username
                self.show_message("Login", f"Welcome, {username}!")
                return True
            else:
                self.show_message("Login Failed", "Invalid username or password.")
                return False
    
    def logout(self):
        """Log out of the system"""
        self.username = None
        self.show_message("Logout", "You have been logged out.")
    
    def run(self):
        """Run the TUI"""
        try:
            self.init_curses()
            
            while self.running:
                self.screen.clear()
                self.draw_header()
                self.draw_footer()
                self.screen.refresh()
                
                if not self.username:
                    # Show main menu
                    choice = self.show_main_menu()
                    if choice == 0:  # Login
                        self.login()
                    elif choice == 1:  # Exit
                        self.running = False
                else:
                    # Show user menu
                    choice = self.show_user_menu()
                    if choice == 0:  # List Files
                        self.show_file_list()
                    elif choice == 1:  # Upload File
                        self.show_message("Upload File", "This feature is not implemented in the simple TUI.")
                    elif choice == 2:  # Download File
                        self.show_message("Download File", "This feature is not implemented in the simple TUI.")
                    elif choice == 3:  # Share File
                        self.show_message("Share File", "This feature is not implemented in the simple TUI.")
                    elif choice == 4:  # Delete File
                        self.show_message("Delete File", "This feature is not implemented in the simple TUI.")
                    elif choice == 5:  # Logout
                        self.logout()
        
        except Exception as e:
            self.cleanup_curses()
            print(f"Error: {str(e)}")
            return 1
        
        finally:
            self.cleanup_curses()
        
        return 0

def main():
    """Main function"""
    tui = SimpleTUI()
    return tui.run()

if __name__ == "__main__":
    sys.exit(main())