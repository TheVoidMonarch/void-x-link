#!/usr/bin/env python3
"""
VoidLink Terminal User Interface

A text-based user interface for VoidLink that runs in the terminal.
"""

import os
import sys
import time
import curses
import threading
from curses import panel

# Add the current directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Try to import VoidLink modules
try:
    import authentication
    import encryption
    import file_security
    import file_transfer
    import file_transfer_resumable
    VOIDLINK_MODULES_LOADED = True
except ImportError:
    print("Warning: Some VoidLink modules could not be imported. Running in demo mode.")
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
    {"name": "Music_Track.mp3", "size": "8.7 MB", "date": "2023-02-28", "type": "Audio"},
    {"name": "Video_Clip.mp4", "size": "25.4 MB", "date": "2023-02-25", "type": "Video"},
]

class MenuItem:
    """Menu item class for the menu system"""
    def __init__(self, name, function=None, args=None):
        self.name = name
        self.function = function
        self.args = args if args is not None else []

class Menu:
    """Menu class for the menu system"""
    def __init__(self, items, title="Menu", parent=None):
        self.items = items
        self.title = title
        self.parent = parent
        self.position = 0
        self.window = None
        self.panel = None
    
    def navigate(self, n):
        """Navigate through menu items"""
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.items):
            self.position = len(self.items) - 1
    
    def display(self):
        """Display the menu"""
        self.window.clear()
        h, w = self.window.getmaxyx()

        # Draw title
        title = f" {self.title} "
        title_len = len(title)
        if title_len < w:
            self.window.addstr(0, max(0, (w - title_len) // 2), title[:w-1])
        self.window.hline(1, 1, curses.ACS_HLINE, w - 2)

        # Draw menu items
        for idx, item in enumerate(self.items):
            if idx == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL

            # Calculate position to display item
            item_y = 2 + idx
            if item_y < h - 2:  # Leave space for footer
                item_name = item.name[:w-4]  # Truncate if too long
                self.window.addstr(item_y, 2, item_name, mode)

        # Draw footer
        self.window.hline(h - 3, 1, curses.ACS_HLINE, w - 2)
        footer = " ↑/↓: Navigate | Enter: Select | Esc: Back "
        footer_len = len(footer)
        if footer_len < w and h > 3:
            try:
                self.window.addstr(h - 2, max(0, (w - footer_len) // 2), footer[:w-1])
            except curses.error:
                # Ignore errors when writing to the bottom of the window
                pass

        try:
            self.window.border()
        except curses.error:
            # Ignore errors when drawing the border
            pass

        self.window.refresh()
    
    def select(self):
        """Select the current menu item"""
        if self.position >= 0 and self.position < len(self.items):
            item = self.items[self.position]
            if item.function:
                return item.function(*item.args)
        return None

class FileListWindow:
    """Window to display a list of files"""
    def __init__(self, files, title="Files"):
        self.files = files
        self.title = title
        self.position = 0
        self.offset = 0
        self.window = None
        self.panel = None
        self.selected_file = None
    
    def navigate(self, n):
        """Navigate through the file list"""
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.files):
            self.position = len(self.files) - 1
        
        # Adjust offset to keep the selected item visible
        h, w = self.window.getmaxyx()
        visible_lines = h - 6  # Account for borders, title, headers, and footer
        
        if self.position < self.offset:
            self.offset = self.position
        elif self.position >= self.offset + visible_lines:
            self.offset = self.position - visible_lines + 1
    
    def display(self):
        """Display the file list"""
        self.window.clear()
        h, w = self.window.getmaxyx()

        # Draw title
        title = f" {self.title} "
        title_len = len(title)
        if title_len < w:
            try:
                self.window.addstr(0, max(0, (w - title_len) // 2), title[:w-1])
            except curses.error:
                pass

        try:
            self.window.hline(1, 1, curses.ACS_HLINE, w - 2)
        except curses.error:
            pass

        # Draw column headers
        headers = ["Name", "Size", "Date", "Type"]
        col_widths = [max(10, w - 36), 10, 12, 12]  # Adjust column widths based on window size

        header_x = 2
        for idx, header in enumerate(headers):
            if header_x + len(header) < w:
                try:
                    self.window.addstr(2, header_x, header[:w-header_x-1], curses.A_BOLD)
                except curses.error:
                    pass
            header_x += col_widths[idx]

        try:
            self.window.hline(3, 1, curses.ACS_HLINE, w - 2)
        except curses.error:
            pass

        # Draw files
        visible_lines = max(1, h - 7)  # Ensure at least one line is visible
        end_idx = min(self.offset + visible_lines, len(self.files))

        for idx in range(self.offset, end_idx):
            file = self.files[idx]

            if idx == self.position:
                mode = curses.A_REVERSE
                self.selected_file = file
            else:
                mode = curses.A_NORMAL

            # Calculate position to display item
            item_y = 4 + (idx - self.offset)
            if item_y >= h - 3:
                break  # Don't draw beyond the window

            # Display file information in columns
            col_x = 2
            for col_idx, key in enumerate(["name", "size", "date", "type"]):
                value = file[key]
                # Truncate value if it's too long for the column
                max_len = min(col_widths[col_idx] - 1, w - col_x - 1)
                if max_len <= 0:
                    break  # Skip if no space left

                if len(value) > max_len:
                    value = value[:max_len - 3] + "..."

                try:
                    self.window.addstr(item_y, col_x, value, mode)
                except curses.error:
                    pass

                col_x += col_widths[col_idx]

        # Draw footer
        footer_y = h - 2
        if footer_y > 4:  # Ensure there's space for the footer
            try:
                self.window.hline(footer_y - 1, 1, curses.ACS_HLINE, w - 2)
            except curses.error:
                pass

            footer = " ↑/↓: Navigate | Enter: Select | Esc: Back "
            footer_len = len(footer)
            if footer_len < w:
                try:
                    self.window.addstr(footer_y, max(0, (w - footer_len) // 2), footer[:w-1])
                except curses.error:
                    pass

        # Draw scrollbar if needed
        if len(self.files) > visible_lines:
            scrollbar_height = max(1, int(visible_lines * visible_lines / len(self.files)))
            scrollbar_pos = min(visible_lines - scrollbar_height, int(visible_lines * self.offset / len(self.files)))

            for i in range(min(visible_lines, h - 6)):
                if i >= scrollbar_pos and i < scrollbar_pos + scrollbar_height and w > 2:
                    try:
                        self.window.addch(4 + i, w - 3, curses.ACS_BLOCK)
                    except curses.error:
                        pass

        try:
            self.window.border()
        except curses.error:
            pass

        self.window.refresh()
    
    def select(self):
        """Select the current file"""
        if self.position >= 0 and self.position < len(self.files):
            return self.files[self.position]
        return None

class ProgressWindow:
    """Window to display a progress bar"""
    def __init__(self, title="Progress", max_value=100):
        self.title = title
        self.max_value = max_value
        self.current_value = 0
        self.window = None
        self.panel = None
        self.thread = None
        self.running = False
    
    def display(self):
        """Display the progress window"""
        self.window.clear()
        h, w = self.window.getmaxyx()

        # Draw title
        title = f" {self.title} "
        title_len = len(title)
        if title_len < w:
            try:
                self.window.addstr(0, max(0, (w - title_len) // 2), title[:w-1])
            except curses.error:
                pass

        try:
            self.window.hline(1, 1, curses.ACS_HLINE, w - 2)
        except curses.error:
            pass

        # Draw progress bar
        bar_width = max(1, w - 6)
        progress = int(bar_width * self.current_value / self.max_value)
        progress = min(progress, bar_width)  # Ensure progress doesn't exceed bar width

        try:
            self.window.addstr(3, 2, "[" + "=" * progress + " " * (bar_width - progress) + "]"[:w-3])
        except curses.error:
            pass

        # Draw percentage
        percentage = f"{int(self.current_value / self.max_value * 100)}%"
        percentage_len = len(percentage)
        if percentage_len < w and h > 4:
            try:
                self.window.addstr(4, max(0, (w - percentage_len) // 2), percentage)
            except curses.error:
                pass

        # Draw footer
        if h > 6:
            try:
                self.window.hline(h - 3, 1, curses.ACS_HLINE, w - 2)
            except curses.error:
                pass

            footer = " Press any key to cancel "
            footer_len = len(footer)
            if footer_len < w:
                try:
                    self.window.addstr(h - 2, max(0, (w - footer_len) // 2), footer[:w-1])
                except curses.error:
                    pass

        try:
            self.window.border()
        except curses.error:
            pass

        self.window.refresh()
    
    def update(self, value):
        """Update the progress value"""
        self.current_value = value
        if self.current_value > self.max_value:
            self.current_value = self.max_value
        self.display()
    
    def start_progress(self, increment=1, delay=0.1):
        """Start the progress bar animation"""
        self.running = True
        self.thread = threading.Thread(target=self._progress_thread, args=(increment, delay))
        self.thread.daemon = True
        self.thread.start()
    
    def stop_progress(self):
        """Stop the progress bar animation"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _progress_thread(self, increment, delay):
        """Thread function for progress bar animation"""
        while self.running and self.current_value < self.max_value:
            self.current_value += increment
            if self.current_value > self.max_value:
                self.current_value = self.max_value
            self.display()
            time.sleep(delay)

class InputWindow:
    """Window to get text input from the user"""
    def __init__(self, title="Input", prompt="Enter value:"):
        self.title = title
        self.prompt = prompt
        self.value = ""
        self.window = None
        self.panel = None
    
    def display(self):
        """Display the input window"""
        self.window.clear()
        h, w = self.window.getmaxyx()

        # Draw title
        title = f" {self.title} "
        title_len = len(title)
        if title_len < w:
            try:
                self.window.addstr(0, max(0, (w - title_len) // 2), title[:w-1])
            except curses.error:
                pass

        try:
            self.window.hline(1, 1, curses.ACS_HLINE, w - 2)
        except curses.error:
            pass

        # Draw prompt
        if h > 3:
            try:
                self.window.addstr(3, 2, self.prompt[:w-3])
            except curses.error:
                pass

        # Draw input field
        if h > 5:
            field_width = max(1, w - 6)
            try:
                self.window.addstr(5, 2, "[" + " " * field_width + "]"[:w-3])
            except curses.error:
                pass

            # Draw value
            display_value = self.value
            if len(display_value) > field_width - 2:
                display_value = display_value[-(field_width - 2):]

            try:
                self.window.addstr(5, 3, display_value[:field_width-2])
            except curses.error:
                pass

            # Draw cursor
            try:
                cursor_x = min(3 + len(display_value), w - 2)
                self.window.addstr(5, cursor_x, " ", curses.A_REVERSE)
            except curses.error:
                pass

        # Draw footer
        if h > 7:
            try:
                self.window.hline(h - 3, 1, curses.ACS_HLINE, w - 2)
            except curses.error:
                pass

            footer = " Enter: Confirm | Esc: Cancel "
            footer_len = len(footer)
            if footer_len < w:
                try:
                    self.window.addstr(h - 2, max(0, (w - footer_len) // 2), footer[:w-1])
                except curses.error:
                    pass

        try:
            self.window.border()
        except curses.error:
            pass

        self.window.refresh()
    
    def get_input(self, stdscr):
        """Get input from the user"""
        self.display()
        
        while True:
            key = stdscr.getch()
            
            if key == 27:  # Escape
                return None
            elif key == 10:  # Enter
                return self.value
            elif key == 127 or key == 8:  # Backspace
                self.value = self.value[:-1]
            elif key == curses.KEY_DC:  # Delete
                self.value = self.value[:-1]
            elif 32 <= key <= 126:  # Printable characters
                self.value += chr(key)
            
            self.display()

class MessageWindow:
    """Window to display a message"""
    def __init__(self, title="Message", message=""):
        self.title = title
        self.message = message
        self.window = None
        self.panel = None
    
    def display(self):
        """Display the message window"""
        self.window.clear()
        h, w = self.window.getmaxyx()

        # Draw title
        title = f" {self.title} "
        title_len = len(title)
        if title_len < w:
            try:
                self.window.addstr(0, max(0, (w - title_len) // 2), title[:w-1])
            except curses.error:
                pass

        try:
            self.window.hline(1, 1, curses.ACS_HLINE, w - 2)
        except curses.error:
            pass

        # Draw message
        lines = self.message.split('\n')
        for idx, line in enumerate(lines):
            if 2 + idx < h - 3 and len(line) > 0:
                try:
                    self.window.addstr(2 + idx, 2, line[:w - 4])
                except curses.error:
                    pass

        # Draw footer
        if h > 5:
            try:
                self.window.hline(h - 3, 1, curses.ACS_HLINE, w - 2)
            except curses.error:
                pass

            footer = " Press any key to continue "
            footer_len = len(footer)
            if footer_len < w:
                try:
                    self.window.addstr(h - 2, max(0, (w - footer_len) // 2), footer[:w-1])
                except curses.error:
                    pass

        try:
            self.window.border()
        except curses.error:
            pass

        self.window.refresh()

class VoidLinkTUI:
    """Main class for the VoidLink Terminal User Interface"""
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_user = None
        self.files = DEMO_FILES
        
        # Initialize curses
        curses.curs_set(0)  # Hide cursor
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        
        # Get screen dimensions
        self.height, self.width = stdscr.getmaxyx()
        
        # Create main window
        self.main_win = curses.newwin(self.height, self.width, 0, 0)
        self.main_win.keypad(1)
        self.main_panel = panel.new_panel(self.main_win)
        
        # Create status bar
        self.status_win = curses.newwin(1, self.width, self.height - 1, 0)
        self.status_panel = panel.new_panel(self.status_win)
        
        # Initialize menus
        self.init_menus()
    
    def init_menus(self):
        """Initialize the menu system"""
        # Main menu
        self.main_menu = Menu([
            MenuItem("Login", self.login),
            MenuItem("Files", self.show_files),
            MenuItem("Upload", self.upload_file),
            MenuItem("Download", self.download_file),
            MenuItem("Share", self.share_file),
            MenuItem("Settings", self.show_settings),
            MenuItem("About", self.show_about),
            MenuItem("Exit", self.exit_program)
        ], title="VoidLink Main Menu")
        
        # Settings menu
        self.settings_menu = Menu([
            MenuItem("Change Password", self.change_password),
            MenuItem("Security Settings", self.security_settings),
            MenuItem("Back", lambda: None)
        ], title="Settings", parent=self.main_menu)
        
        # File actions menu
        self.file_actions_menu = Menu([
            MenuItem("Download", self.download_selected_file),
            MenuItem("Share", self.share_selected_file),
            MenuItem("Delete", self.delete_selected_file),
            MenuItem("Properties", self.show_file_properties),
            MenuItem("Back", lambda: None)
        ], title="File Actions", parent=self.main_menu)
        
        # Set initial menu
        self.current_menu = self.main_menu
    
    def create_window(self, height, width, y, x, window_class, *args, **kwargs):
        """Create a new window of the specified class"""
        win = curses.newwin(height, width, y, x)
        win.keypad(1)
        p = panel.new_panel(win)
        
        window_obj = window_class(*args, **kwargs)
        window_obj.window = win
        window_obj.panel = p
        
        return window_obj
    
    def center_window(self, height, width, window_class, *args, **kwargs):
        """Create a centered window of the specified class"""
        y = (self.height - height) // 2
        x = (self.width - width) // 2
        return self.create_window(height, width, y, x, window_class, *args, **kwargs)
    
    def update_status_bar(self, message):
        """Update the status bar with a message"""
        try:
            self.status_win.clear()
            if self.width > 0:
                self.status_win.addstr(0, 0, message[:self.width - 1])
            self.status_win.refresh()
        except curses.error:
            # Ignore errors when updating the status bar
            pass
    
    def run(self):
        """Run the main loop"""
        self.update_status_bar(f"VoidLink v{VERSION} | Press 'q' to quit")

        # Create main menu window
        self.resize_menu_window()

        # Main loop
        while True:
            try:
                # Check if terminal was resized
                new_height, new_width = self.stdscr.getmaxyx()
                if new_height != self.height or new_width != self.width:
                    self.height, self.width = new_height, new_width
                    self.resize_menu_window()
                    self.update_status_bar(f"VoidLink v{VERSION} | Press 'q' to quit")

                # Display current menu
                self.current_menu.display()
                panel.update_panels()
                curses.doupdate()

                # Get user input
                key = self.current_menu.window.getch()

                if key == ord('q'):
                    break
                elif key == curses.KEY_UP:
                    self.current_menu.navigate(-1)
                elif key == curses.KEY_DOWN:
                    self.current_menu.navigate(1)
                elif key == 10:  # Enter key
                    result = self.current_menu.select()
                    if result == "EXIT":
                        break
                elif key == 27:  # Escape key
                    if self.current_menu.parent:
                        self.current_menu = self.current_menu.parent
            except curses.error:
                # Handle curses errors (like terminal resize)
                self.stdscr.refresh()
                self.height, self.width = self.stdscr.getmaxyx()
                self.resize_menu_window()

    def resize_menu_window(self):
        """Resize the menu window to fit the terminal"""
        menu_height = min(12, max(6, self.height - 4))
        menu_width = min(30, max(20, self.width - 4))
        y = max(0, (self.height - menu_height) // 2)
        x = max(0, (self.width - menu_width) // 2)

        try:
            self.current_menu.window = curses.newwin(menu_height, menu_width, y, x)
            self.current_menu.window.keypad(1)
            self.current_menu.panel = panel.new_panel(self.current_menu.window)
        except curses.error:
            # If terminal is too small, create a minimal window
            try:
                self.current_menu.window = curses.newwin(6, 20, 0, 0)
                self.current_menu.window.keypad(1)
                self.current_menu.panel = panel.new_panel(self.current_menu.window)
            except curses.error:
                pass
    
    def login(self):
        """Show login screen"""
        # Create username input window
        username_input = self.center_window(8, 50, InputWindow, "Login", "Username:")
        username = username_input.get_input(self.stdscr)
        
        if username is None:
            return
        
        # Create password input window
        password_input = self.center_window(8, 50, InputWindow, "Login", "Password:")
        password = password_input.get_input(self.stdscr)
        
        if password is None:
            return
        
        # Authenticate user
        if VOIDLINK_MODULES_LOADED:
            try:
                success = authentication.authenticate_user(username, password)
                if success:
                    self.current_user = username
                    self.update_status_bar(f"Logged in as {username}")
                    
                    # Show welcome message
                    welcome = self.center_window(10, 50, MessageWindow, "Welcome", f"Welcome back, {username}!\n\nYou are now logged in to VoidLink.")
                    welcome.display()
                    welcome.window.getch()
                else:
                    # Show error message
                    error = self.center_window(8, 50, MessageWindow, "Error", "Invalid username or password.")
                    error.display()
                    error.window.getch()
            except Exception as e:
                # Show error message
                error = self.center_window(8, 50, MessageWindow, "Error", f"Authentication error: {str(e)}")
                error.display()
                error.window.getch()
        else:
            # Demo mode - accept any login
            if username and password:
                self.current_user = username
                self.update_status_bar(f"Logged in as {username}")
                
                # Show welcome message
                welcome = self.center_window(10, 50, MessageWindow, "Welcome", f"Welcome back, {username}!\n\nYou are now logged in to VoidLink.")
                welcome.display()
                welcome.window.getch()
            else:
                # Show error message
                error = self.center_window(8, 50, MessageWindow, "Error", "Username and password are required.")
                error.display()
                error.window.getch()
    
    def show_files(self):
        """Show file list"""
        if not self.current_user:
            # Show error message
            error = self.center_window(8, 50, MessageWindow, "Error", "You must be logged in to view files.")
            error.display()
            error.window.getch()
            return
        
        # Create file list window
        file_list = self.center_window(20, 70, FileListWindow, self.files, f"Files - {self.current_user}")
        
        # Display file list
        file_list.display()
        
        # Handle user input
        while True:
            key = file_list.window.getch()
            
            if key == ord('q') or key == 27:  # q or Escape
                break
            elif key == curses.KEY_UP:
                file_list.navigate(-1)
                file_list.display()
            elif key == curses.KEY_DOWN:
                file_list.navigate(1)
                file_list.display()
            elif key == 10:  # Enter key
                selected_file = file_list.select()
                if selected_file:
                    # Show file actions menu
                    self.file_actions_menu.window = curses.newwin(10, 30, file_list.window.getbegyx()[0] + 5, file_list.window.getbegyx()[1] + 20)
                    self.file_actions_menu.window.keypad(1)
                    self.file_actions_menu.panel = panel.new_panel(self.file_actions_menu.window)
                    
                    # Store selected file
                    self.selected_file = selected_file
                    
                    # Show file actions menu
                    old_menu = self.current_menu
                    self.current_menu = self.file_actions_menu
                    self.current_menu.display()
                    
                    # Handle file actions menu
                    while True:
                        key = self.current_menu.window.getch()
                        
                        if key == ord('q') or key == 27:  # q or Escape
                            self.current_menu = old_menu
                            break
                        elif key == curses.KEY_UP:
                            self.current_menu.navigate(-1)
                            self.current_menu.display()
                        elif key == curses.KEY_DOWN:
                            self.current_menu.navigate(1)
                            self.current_menu.display()
                        elif key == 10:  # Enter key
                            result = self.current_menu.select()
                            if result is None:  # Back option
                                self.current_menu = old_menu
                                break
                    
                    # Redisplay file list
                    file_list.display()
    
    def upload_file(self):
        """Upload a file"""
        if not self.current_user:
            # Show error message
            error = self.center_window(8, 50, MessageWindow, "Error", "You must be logged in to upload files.")
            error.display()
            error.window.getch()
            return
        
        # Get file name
        filename_input = self.center_window(8, 50, InputWindow, "Upload File", "Enter file name:")
        filename = filename_input.get_input(self.stdscr)
        
        if filename is None:
            return
        
        # Get file size (for demo)
        size_input = self.center_window(8, 50, InputWindow, "Upload File", "Enter file size (KB):")
        size_str = size_input.get_input(self.stdscr)
        
        if size_str is None:
            return
        
        try:
            size = int(size_str)
            if size <= 0:
                raise ValueError("Size must be positive")
        except ValueError:
            # Show error message
            error = self.center_window(8, 50, MessageWindow, "Error", "Invalid file size. Please enter a positive number.")
            error.display()
            error.window.getch()
            return
        
        # Show progress window
        progress = self.center_window(8, 50, ProgressWindow, f"Uploading {filename}", 100)
        progress.display()
        
        # Start progress animation
        progress.start_progress(2, 0.1)
        
        # Wait for user input or completion
        while progress.current_value < progress.max_value:
            key = progress.window.getch()
            if key != -1:
                progress.stop_progress()
                break
        
        # Stop progress animation
        progress.stop_progress()
        
        # Add file to list (for demo)
        if progress.current_value >= progress.max_value:
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
            elif ext in ['.mp3', '.wav', '.ogg']:
                file_type = "Audio"
            elif ext in ['.mp4', '.avi', '.mov']:
                file_type = "Video"
            
            # Format size
            if size < 1024:
                size_str = f"{size} KB"
            else:
                size_str = f"{size/1024:.1f} MB"
            
            # Add to file list
            self.files.append({
                "name": filename,
                "size": size_str,
                "date": time.strftime("%Y-%m-%d"),
                "type": file_type
            })
            
            # Show success message
            success = self.center_window(8, 50, MessageWindow, "Success", f"File '{filename}' uploaded successfully.")
            success.display()
            success.window.getch()
        else:
            # Show cancelled message
            cancelled = self.center_window(8, 50, MessageWindow, "Cancelled", f"Upload of '{filename}' was cancelled.")
            cancelled.display()
            cancelled.window.getch()
    
    def download_file(self):
        """Download a file"""
        if not self.current_user:
            # Show error message
            error = self.center_window(8, 50, MessageWindow, "Error", "You must be logged in to download files.")
            error.display()
            error.window.getch()
            return
        
        # Show file list
        file_list = self.center_window(20, 70, FileListWindow, self.files, "Select File to Download")
        
        # Display file list
        file_list.display()
        
        # Handle user input
        while True:
            key = file_list.window.getch()
            
            if key == ord('q') or key == 27:  # q or Escape
                return
            elif key == curses.KEY_UP:
                file_list.navigate(-1)
                file_list.display()
            elif key == curses.KEY_DOWN:
                file_list.navigate(1)
                file_list.display()
            elif key == 10:  # Enter key
                selected_file = file_list.select()
                if selected_file:
                    # Download the selected file
                    self.download_selected_file(selected_file)
                    return
    
    def download_selected_file(self, file=None):
        """Download the selected file"""
        if file is None:
            file = self.selected_file
        
        if not file:
            return
        
        # Show progress window
        progress = self.center_window(8, 50, ProgressWindow, f"Downloading {file['name']}", 100)
        progress.display()
        
        # Start progress animation
        progress.start_progress(2, 0.1)
        
        # Wait for user input or completion
        while progress.current_value < progress.max_value:
            key = progress.window.getch()
            if key != -1:
                progress.stop_progress()
                break
        
        # Stop progress animation
        progress.stop_progress()
        
        # Show result message
        if progress.current_value >= progress.max_value:
            success = self.center_window(8, 50, MessageWindow, "Success", f"File '{file['name']}' downloaded successfully.")
            success.display()
            success.window.getch()
        else:
            cancelled = self.center_window(8, 50, MessageWindow, "Cancelled", f"Download of '{file['name']}' was cancelled.")
            cancelled.display()
            cancelled.window.getch()
    
    def share_file(self):
        """Share a file"""
        if not self.current_user:
            # Show error message
            error = self.center_window(8, 50, MessageWindow, "Error", "You must be logged in to share files.")
            error.display()
            error.window.getch()
            return
        
        # Show file list
        file_list = self.center_window(20, 70, FileListWindow, self.files, "Select File to Share")
        
        # Display file list
        file_list.display()
        
        # Handle user input
        while True:
            key = file_list.window.getch()
            
            if key == ord('q') or key == 27:  # q or Escape
                return
            elif key == curses.KEY_UP:
                file_list.navigate(-1)
                file_list.display()
            elif key == curses.KEY_DOWN:
                file_list.navigate(1)
                file_list.display()
            elif key == 10:  # Enter key
                selected_file = file_list.select()
                if selected_file:
                    # Share the selected file
                    self.share_selected_file(selected_file)
                    return
    
    def share_selected_file(self, file=None):
        """Share the selected file"""
        if file is None:
            file = self.selected_file
        
        if not file:
            return
        
        # Get recipient
        recipient_input = self.center_window(8, 50, InputWindow, "Share File", "Enter recipient email:")
        recipient = recipient_input.get_input(self.stdscr)
        
        if recipient is None:
            return
        
        # Generate share link
        share_link = f"https://voidlink.example.com/share/{hash(file['name'] + recipient) % 1000000:06d}"
        
        # Show success message
        success = self.center_window(10, 60, MessageWindow, "File Shared", f"File '{file['name']}' shared with {recipient}.\n\nShare link: {share_link}")
        success.display()
        success.window.getch()
    
    def delete_selected_file(self):
        """Delete the selected file"""
        if not self.selected_file:
            return
        
        # Show confirmation dialog
        confirm = self.center_window(8, 50, MessageWindow, "Confirm Delete", f"Are you sure you want to delete '{self.selected_file['name']}'?\n\nPress 'y' to confirm, any other key to cancel.")
        confirm.display()
        
        key = confirm.window.getch()
        if key == ord('y'):
            # Remove file from list
            self.files = [f for f in self.files if f['name'] != self.selected_file['name']]
            
            # Show success message
            success = self.center_window(8, 50, MessageWindow, "Success", f"File '{self.selected_file['name']}' deleted successfully.")
            success.display()
            success.window.getch()
        
        # Clear selected file
        self.selected_file = None
    
    def show_file_properties(self):
        """Show properties of the selected file"""
        if not self.selected_file:
            return
        
        # Format properties
        properties = f"Name: {self.selected_file['name']}\n"
        properties += f"Size: {self.selected_file['size']}\n"
        properties += f"Date: {self.selected_file['date']}\n"
        properties += f"Type: {self.selected_file['type']}\n"
        
        # Show properties
        props = self.center_window(10, 50, MessageWindow, "File Properties", properties)
        props.display()
        props.window.getch()
    
    def show_settings(self):
        """Show settings menu"""
        if not self.current_user:
            # Show error message
            error = self.center_window(8, 50, MessageWindow, "Error", "You must be logged in to access settings.")
            error.display()
            error.window.getch()
            return
        
        # Create settings menu window
        self.settings_menu.window = curses.newwin(10, 30, (self.height - 10) // 2, (self.width - 30) // 2)
        self.settings_menu.window.keypad(1)
        self.settings_menu.panel = panel.new_panel(self.settings_menu.window)
        
        # Show settings menu
        old_menu = self.current_menu
        self.current_menu = self.settings_menu
    
    def change_password(self):
        """Change user password"""
        if not self.current_user:
            return
        
        # Get current password
        current_input = self.center_window(8, 50, InputWindow, "Change Password", "Current password:")
        current = current_input.get_input(self.stdscr)
        
        if current is None:
            return
        
        # Get new password
        new_input = self.center_window(8, 50, InputWindow, "Change Password", "New password:")
        new = new_input.get_input(self.stdscr)
        
        if new is None:
            return
        
        # Get confirmation
        confirm_input = self.center_window(8, 50, InputWindow, "Change Password", "Confirm new password:")
        confirm = confirm_input.get_input(self.stdscr)
        
        if confirm is None:
            return
        
        # Check if new passwords match
        if new != confirm:
            # Show error message
            error = self.center_window(8, 50, MessageWindow, "Error", "New passwords do not match.")
            error.display()
            error.window.getch()
            return
        
        # Change password (demo mode)
        success = self.center_window(8, 50, MessageWindow, "Success", "Password changed successfully.")
        success.display()
        success.window.getch()
    
    def security_settings(self):
        """Show security settings"""
        # Show security settings
        settings = self.center_window(12, 60, MessageWindow, "Security Settings", "Two-Factor Authentication: Disabled\n\nFile Encryption: Enabled\n\nAuto-Logout: 30 minutes\n\nVirus Scanning: Enabled")
        settings.display()
        settings.window.getch()
    
    def show_about(self):
        """Show about information"""
        about_text = f"VoidLink v{VERSION}\n\n"
        about_text += "A secure file sharing application\n\n"
        about_text += "Features:\n"
        about_text += "- End-to-end encryption\n"
        about_text += "- Virus scanning\n"
        about_text += "- Resumable file transfers\n"
        about_text += "- Secure authentication\n\n"
        about_text += "Created by: Your Name"
        
        about = self.center_window(15, 60, MessageWindow, "About VoidLink", about_text)
        about.display()
        about.window.getch()
    
    def exit_program(self):
        """Exit the program"""
        # Show confirmation dialog
        confirm = self.center_window(8, 50, MessageWindow, "Confirm Exit", "Are you sure you want to exit?\n\nPress 'y' to confirm, any other key to cancel.")
        confirm.display()
        
        key = confirm.window.getch()
        if key == ord('y'):
            return "EXIT"
        
        return None

def main(stdscr):
    """Main function"""
    # Initialize the TUI
    tui = VoidLinkTUI(stdscr)
    
    # Run the TUI
    tui.run()

if __name__ == "__main__":
    # Run the curses application
    curses.wrapper(main)