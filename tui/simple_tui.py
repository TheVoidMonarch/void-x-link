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
    import authentication
    import encryption
    import file_security
    import file_transfer
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
        self.items = items
        self.title = title
        self.position = 0
    
    def display(self, stdscr):
        """Display the menu"""
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        # Draw title
        title = f" {self.title} "
        try:
            stdscr.addstr(1, (w - len(title)) // 2, title)
            stdscr.addstr(2, 2, "=" * (w - 4))
        except curses.error:
            pass
        
        # Draw menu items
        for idx, item in enumerate(self.items):
            y = 4 + idx
            if y < h - 2:
                try:
                    if idx == self.position:
                        stdscr.addstr(y, 4, f"> {item}", curses.A_BOLD)
                    else:
                        stdscr.addstr(y, 4, f"  {item}")
                except curses.error:
                    pass
        
        # Draw footer
        try:
            stdscr.addstr(h - 2, 2, "=" * (w - 4))
            footer = "↑/↓: Navigate | Enter: Select | q: Quit"
            stdscr.addstr(h - 1, (w - len(footer)) // 2, footer)
        except curses.error:
            pass
        
        stdscr.refresh()
    
    def handle_input(self, key):
        """Handle user input"""
        if key == curses.KEY_UP and self.position > 0:
            self.position -= 1
        elif key == curses.KEY_DOWN and self.position < len(self.items) - 1:
            self.position += 1
        
        return self.position

class SimpleFileList:
    """Simple file list class for the TUI"""
    def __init__(self, files, title="Files"):
        self.files = files
        self.title = title
        self.position = 0
        self.offset = 0
    
    def display(self, stdscr):
        """Display the file list"""
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        # Draw title
        title = f" {self.title} "
        try:
            stdscr.addstr(1, (w - len(title)) // 2, title)
            stdscr.addstr(2, 2, "=" * (w - 4))
        except curses.error:
            pass
        
        # Draw column headers
        try:
            stdscr.addstr(4, 4, "Name")
            stdscr.addstr(4, w - 30, "Size")
            stdscr.addstr(4, w - 20, "Date")
            stdscr.addstr(4, w - 10, "Type")
            stdscr.addstr(5, 2, "-" * (w - 4))
        except curses.error:
            pass
        
        # Calculate visible range
        visible_lines = h - 9
        end_idx = min(self.offset + visible_lines, len(self.files))
        
        # Draw files
        for idx in range(self.offset, end_idx):
            file = self.files[idx]
            y = 6 + (idx - self.offset)
            
            if y < h - 3:
                try:
                    # Highlight selected item
                    attr = curses.A_BOLD if idx == self.position else curses.A_NORMAL
                    
                    # Name (truncated if needed)
                    name = file["name"]
                    if len(name) > w - 35:
                        name = name[:w - 38] + "..."
                    stdscr.addstr(y, 4, name, attr)
                    
                    # Size, date, type
                    stdscr.addstr(y, w - 30, file["size"], attr)
                    stdscr.addstr(y, w - 20, file["date"], attr)
                    stdscr.addstr(y, w - 10, file["type"], attr)
                except curses.error:
                    pass
        
        # Draw footer
        try:
            stdscr.addstr(h - 2, 2, "=" * (w - 4))
            footer = "↑/↓: Navigate | Enter: Select | q: Back"
            stdscr.addstr(h - 1, (w - len(footer)) // 2, footer)
        except curses.error:
            pass
        
        stdscr.refresh()
    
    def handle_input(self, key):
        """Handle user input"""
        if key == curses.KEY_UP and self.position > 0:
            self.position -= 1
            # Adjust offset if needed
            if self.position < self.offset:
                self.offset = self.position
        elif key == curses.KEY_DOWN and self.position < len(self.files) - 1:
            self.position += 1
            # Adjust offset if needed
            h, w = curses.stdscr.getmaxyx()
            visible_lines = h - 9
            if self.position >= self.offset + visible_lines:
                self.offset = self.position - visible_lines + 1
        
        return self.position

class SimpleMessage:
    """Simple message display class for the TUI"""
    def __init__(self, message, title="Message"):
        self.message = message
        self.title = title
    
    def display(self, stdscr):
        """Display the message"""
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        # Draw title
        title = f" {self.title} "
        try:
            stdscr.addstr(1, (w - len(title)) // 2, title)
            stdscr.addstr(2, 2, "=" * (w - 4))
        except curses.error:
            pass
        
        # Draw message (handle multi-line)
        lines = self.message.split('\n')
        for idx, line in enumerate(lines):
            y = 4 + idx
            if y < h - 3 and line:
                try:
                    stdscr.addstr(y, 4, line[:w - 8])
                except curses.error:
                    pass
        
        # Draw footer
        try:
            stdscr.addstr(h - 2, 2, "=" * (w - 4))
            footer = "Press any key to continue"
            stdscr.addstr(h - 1, (w - len(footer)) // 2, footer)
        except curses.error:
            pass
        
        stdscr.refresh()

class SimpleInput:
    """Simple input class for the TUI"""
    def __init__(self, prompt, title="Input"):
        self.prompt = prompt
        self.title = title
        self.value = ""
    
    def display(self, stdscr):
        """Display the input prompt"""
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        # Draw title
        title = f" {self.title} "
        try:
            stdscr.addstr(1, (w - len(title)) // 2, title)
            stdscr.addstr(2, 2, "=" * (w - 4))
        except curses.error:
            pass
        
        # Draw prompt
        try:
            stdscr.addstr(4, 4, self.prompt)
        except curses.error:
            pass
        
        # Draw input field
        try:
            field_width = w - 10
            stdscr.addstr(6, 4, "[" + " " * field_width + "]")
            
            # Draw current value
            if len(self.value) > field_width:
                display_value = self.value[-field_width:]
            else:
                display_value = self.value
            
            stdscr.addstr(6, 5, display_value)
            
            # Draw cursor
            stdscr.addstr(6, 5 + len(display_value), " ", curses.A_REVERSE)
        except curses.error:
            pass
        
        # Draw footer
        try:
            stdscr.addstr(h - 2, 2, "=" * (w - 4))
            footer = "Enter: Confirm | Esc: Cancel"
            stdscr.addstr(h - 1, (w - len(footer)) // 2, footer)
        except curses.error:
            pass
        
        stdscr.refresh()
    
    def get_input(self, stdscr):
        """Get input from the user"""
        curses.curs_set(0)  # Hide cursor
        self.display(stdscr)
        
        while True:
            key = stdscr.getch()
            
            if key == 27:  # Escape
                return None
            elif key == 10:  # Enter
                return self.value
            elif key == 127 or key == 8 or key == curses.KEY_BACKSPACE:  # Backspace
                self.value = self.value[:-1]
            elif key == curses.KEY_DC:  # Delete
                self.value = self.value[:-1]
            elif 32 <= key <= 126:  # Printable characters
                self.value += chr(key)
            
            self.display(stdscr)

def show_main_menu(stdscr):
    """Show the main menu"""
    menu_items = [
        "Login",
        "View Files",
        "Upload File",
        "Download File",
        "Share File",
        "Settings",
        "About",
        "Exit"
    ]
    
    menu = SimpleMenu(menu_items, "VoidLink Main Menu")
    
    while True:
        menu.display(stdscr)
        key = stdscr.getch()
        
        if key == ord('q'):
            return "EXIT"
        
        position = menu.handle_input(key)
        
        if key == 10:  # Enter key
            if position == 0:  # Login
                result = login(stdscr)
                if result == "EXIT":
                    return "EXIT"
            elif position == 1:  # View Files
                result = view_files(stdscr)
                if result == "EXIT":
                    return "EXIT"
            elif position == 2:  # Upload File
                result = upload_file(stdscr)
                if result == "EXIT":
                    return "EXIT"
            elif position == 3:  # Download File
                result = download_file(stdscr)
                if result == "EXIT":
                    return "EXIT"
            elif position == 4:  # Share File
                result = share_file(stdscr)
                if result == "EXIT":
                    return "EXIT"
            elif position == 5:  # Settings
                result = show_settings(stdscr)
                if result == "EXIT":
                    return "EXIT"
            elif position == 6:  # About
                show_about(stdscr)
            elif position == 7:  # Exit
                return "EXIT"

def login(stdscr):
    """Handle user login"""
    # Get username
    username_input = SimpleInput("Enter username:", "Login")
    username = username_input.get_input(stdscr)
    
    if username is None:
        return
    
    # Get password
    password_input = SimpleInput("Enter password:", "Login")
    password = password_input.get_input(stdscr)
    
    if password is None:
        return
    
    # Authenticate
    if VOIDLINK_MODULES_LOADED:
        try:
            success = authentication.authenticate_user(username, password)
            if success:
                message = SimpleMessage(f"Welcome, {username}!\n\nYou have successfully logged in.", "Login Successful")
                message.display(stdscr)
                stdscr.getch()
                return username
            else:
                message = SimpleMessage("Invalid username or password.\nPlease try again.", "Login Failed")
                message.display(stdscr)
                stdscr.getch()
                return None
        except Exception as e:
            message = SimpleMessage(f"Authentication error: {str(e)}", "Error")
            message.display(stdscr)
            stdscr.getch()
            return None
    else:
        # Demo mode - accept any login
        message = SimpleMessage(f"Welcome, {username}!\n\nYou have successfully logged in.\n\n(Demo Mode)", "Login Successful")
        message.display(stdscr)
        stdscr.getch()
        return username

def view_files(stdscr):
    """Show file list"""
    file_list = SimpleFileList(DEMO_FILES, "VoidLink Files")
    
    while True:
        file_list.display(stdscr)
        key = stdscr.getch()
        
        if key == ord('q'):
            return
        
        position = file_list.handle_input(key)
        
        if key == 10:  # Enter key
            selected_file = DEMO_FILES[position]
            result = show_file_actions(stdscr, selected_file)
            if result == "EXIT":
                return "EXIT"

def show_file_actions(stdscr, file):
    """Show actions for a selected file"""
    menu_items = [
        f"Download {file['name']}",
        f"Share {file['name']}",
        f"Delete {file['name']}",
        f"View Properties",
        "Back"
    ]
    
    menu = SimpleMenu(menu_items, f"File: {file['name']}")
    
    while True:
        menu.display(stdscr)
        key = stdscr.getch()
        
        if key == ord('q'):
            return
        
        position = menu.handle_input(key)
        
        if key == 10:  # Enter key
            if position == 0:  # Download
                download_selected_file(stdscr, file)
            elif position == 1:  # Share
                share_selected_file(stdscr, file)
            elif position == 2:  # Delete
                if delete_selected_file(stdscr, file):
                    return  # File was deleted, go back to file list
            elif position == 3:  # Properties
                show_file_properties(stdscr, file)
            elif position == 4:  # Back
                return

def download_selected_file(stdscr, file):
    """Download a file"""
    message = SimpleMessage(f"Downloading {file['name']}...\n\nSize: {file['size']}\nType: {file['type']}", "Download")
    message.display(stdscr)
    
    # Simulate download
    for i in range(10):
        try:
            stdscr.addstr(10, 4, f"Progress: {i*10}%")
            stdscr.refresh()
            time.sleep(0.2)
        except curses.error:
            pass
    
    # Show completion message
    message = SimpleMessage(f"File {file['name']} downloaded successfully.", "Download Complete")
    message.display(stdscr)
    stdscr.getch()

def share_selected_file(stdscr, file):
    """Share a file"""
    recipient_input = SimpleInput("Enter recipient email:", "Share File")
    recipient = recipient_input.get_input(stdscr)
    
    if recipient is None:
        return
    
    # Generate a share link
    share_link = f"https://voidlink.example.com/share/{hash(file['name'] + recipient) % 1000000:06d}"
    
    # Show success message
    message = SimpleMessage(f"File {file['name']} shared with {recipient}.\n\nShare link:\n{share_link}", "File Shared")
    message.display(stdscr)
    stdscr.getch()

def delete_selected_file(stdscr, file):
    """Delete a file"""
    message = SimpleMessage(f"Are you sure you want to delete {file['name']}?\n\nPress 'y' to confirm, any other key to cancel.", "Confirm Delete")
    message.display(stdscr)
    
    key = stdscr.getch()
    if key == ord('y'):
        # Remove file from list
        global DEMO_FILES
        DEMO_FILES = [f for f in DEMO_FILES if f['name'] != file['name']]
        
        # Show success message
        message = SimpleMessage(f"File {file['name']} deleted successfully.", "File Deleted")
        message.display(stdscr)
        stdscr.getch()
        return True
    
    return False

def show_file_properties(stdscr, file):
    """Show file properties"""
    properties = f"Name: {file['name']}\n"
    properties += f"Size: {file['size']}\n"
    properties += f"Date: {file['date']}\n"
    properties += f"Type: {file['type']}\n"
    
    message = SimpleMessage(properties, "File Properties")
    message.display(stdscr)
    stdscr.getch()

def upload_file(stdscr):
    """Upload a file"""
    filename_input = SimpleInput("Enter file name:", "Upload File")
    filename = filename_input.get_input(stdscr)
    
    if filename is None:
        return
    
    size_input = SimpleInput("Enter file size (KB):", "Upload File")
    size_str = size_input.get_input(stdscr)
    
    if size_str is None:
        return
    
    try:
        size = int(size_str)
    except ValueError:
        message = SimpleMessage("Invalid size. Please enter a number.", "Error")
        message.display(stdscr)
        stdscr.getch()
        return
    
    # Determine file type based on extension
    ext = os.path.splitext(filename.lower())[1]
    file_type = "Other"
    
    if ext in ['.pdf']:
        file_type = "PDF"
    elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
        file_type = "Image"
    elif ext in ['.doc', '.docx', '.txt']:
        file_type = "Document"
    elif ext in ['.xls', '.xlsx']:
        file_type = "Spreadsheet"
    elif ext in ['.ppt', '.pptx']:
        file_type = "Presentation"
    elif ext in ['.zip', '.rar', '.tar', '.gz']:
        file_type = "Archive"
    
    # Format size
    if size < 1024:
        size_str = f"{size} KB"
    else:
        size_str = f"{size/1024:.1f} MB"
    
    # Show upload progress
    message = SimpleMessage(f"Uploading {filename}...\n\nSize: {size_str}\nType: {file_type}", "Upload")
    message.display(stdscr)
    
    # Simulate upload
    for i in range(10):
        try:
            stdscr.addstr(10, 4, f"Progress: {i*10}%")
            stdscr.refresh()
            time.sleep(0.2)
        except curses.error:
            pass
    
    # Add to file list
    global DEMO_FILES
    DEMO_FILES.append({
        "name": filename,
        "size": size_str,
        "date": time.strftime("%Y-%m-%d"),
        "type": file_type
    })
    
    # Show completion message
    message = SimpleMessage(f"File {filename} uploaded successfully.", "Upload Complete")
    message.display(stdscr)
    stdscr.getch()

def download_file(stdscr):
    """Download a file from the list"""
    file_list = SimpleFileList(DEMO_FILES, "Select File to Download")
    
    while True:
        file_list.display(stdscr)
        key = stdscr.getch()
        
        if key == ord('q'):
            return
        
        position = file_list.handle_input(key)
        
        if key == 10:  # Enter key
            selected_file = DEMO_FILES[position]
            download_selected_file(stdscr, selected_file)
            return

def share_file(stdscr):
    """Share a file from the list"""
    file_list = SimpleFileList(DEMO_FILES, "Select File to Share")
    
    while True:
        file_list.display(stdscr)
        key = stdscr.getch()
        
        if key == ord('q'):
            return
        
        position = file_list.handle_input(key)
        
        if key == 10:  # Enter key
            selected_file = DEMO_FILES[position]
            share_selected_file(stdscr, selected_file)
            return

def show_settings(stdscr):
    """Show settings menu"""
    menu_items = [
        "Change Password",
        "Security Settings",
        "Network Settings",
        "Back"
    ]
    
    menu = SimpleMenu(menu_items, "Settings")
    
    while True:
        menu.display(stdscr)
        key = stdscr.getch()
        
        if key == ord('q'):
            return
        
        position = menu.handle_input(key)
        
        if key == 10:  # Enter key
            if position == 0:  # Change Password
                change_password(stdscr)
            elif position == 1:  # Security Settings
                show_security_settings(stdscr)
            elif position == 2:  # Network Settings
                show_network_settings(stdscr)
            elif position == 3:  # Back
                return

def change_password(stdscr):
    """Change user password"""
    current_input = SimpleInput("Enter current password:", "Change Password")
    current = current_input.get_input(stdscr)
    
    if current is None:
        return
    
    new_input = SimpleInput("Enter new password:", "Change Password")
    new = new_input.get_input(stdscr)
    
    if new is None:
        return
    
    confirm_input = SimpleInput("Confirm new password:", "Change Password")
    confirm = confirm_input.get_input(stdscr)
    
    if confirm is None:
        return
    
    if new != confirm:
        message = SimpleMessage("New passwords do not match.", "Error")
        message.display(stdscr)
        stdscr.getch()
        return
    
    # Show success message (demo mode)
    message = SimpleMessage("Password changed successfully.", "Success")
    message.display(stdscr)
    stdscr.getch()

def show_security_settings(stdscr):
    """Show security settings"""
    settings = "Two-Factor Authentication: Disabled\n\n"
    settings += "File Encryption: Enabled\n\n"
    settings += "Auto-Logout: 30 minutes\n\n"
    settings += "Virus Scanning: Enabled"
    
    message = SimpleMessage(settings, "Security Settings")
    message.display(stdscr)
    stdscr.getch()

def show_network_settings(stdscr):
    """Show network settings"""
    settings = "Server Address: localhost\n\n"
    settings += "Port: 8000\n\n"
    settings += "Connection Type: Secure\n\n"
    settings += "Bandwidth Limit: None"
    
    message = SimpleMessage(settings, "Network Settings")
    message.display(stdscr)
    stdscr.getch()

def show_about(stdscr):
    """Show about information"""
    about = f"VoidLink v{VERSION}\n\n"
    about += "A secure file sharing application\n\n"
    about += "Features:\n"
    about += "- End-to-end encryption\n"
    about += "- Virus scanning\n"
    about += "- Resumable file transfers\n"
    about += "- Secure authentication\n\n"
    
    if VOIDLINK_MODULES_LOADED:
        about += "Running with VoidLink core modules"
    else:
        about += "Running in demo mode"
    
    message = SimpleMessage(about, "About VoidLink")
    message.display(stdscr)
    stdscr.getch()

def main(stdscr):
    """Main function"""
    # Initialize curses
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()
    
    # Set up colors if available
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    
    # Show splash screen
    h, w = stdscr.getmaxyx()
    try:
        stdscr.addstr(h//2-2, (w-10)//2, "VoidLink", curses.A_BOLD)
        stdscr.addstr(h//2, (w-22)//2, "Secure File Sharing")
        stdscr.addstr(h//2+2, (w-26)//2, "Press any key to continue")
        stdscr.refresh()
    except curses.error:
        pass
    
    stdscr.getch()
    
    # Show main menu
    result = show_main_menu(stdscr)
    
    # Exit message
    if result == "EXIT":
        try:
            stdscr.clear()
            stdscr.addstr(h//2, (w-18)//2, "Thanks for using")
            stdscr.addstr(h//2+1, (w-10)//2, "VoidLink!")
            stdscr.refresh()
            time.sleep(1)
        except curses.error:
            pass

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("VoidLink TUI terminated by user")
    except Exception as e:
        print(f"Error: {str(e)}")