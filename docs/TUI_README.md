# VoidLink Terminal User Interface

This is a text-based user interface (TUI) for VoidLink that runs in the terminal.

## Features

- Full-featured terminal interface with menus and windows
- File management (upload, download, share, delete)
- User authentication
- Progress indicators for file transfers
- Settings management
- Responsive design that adapts to terminal size

## Getting Started

To use the VoidLink Terminal User Interface, follow these steps:

1. Activate the virtual environment:
   ```bash
   source voidlink-env/bin/activate
   ```

2. Make the run script executable:
   ```bash
   chmod +x run_tui.sh
   ```

3. Run the TUI:
   ```bash
   ./run_tui.sh
   ```

## Navigation

- Use the **arrow keys** to navigate through menus and lists
- Press **Enter** to select an item
- Press **Escape** to go back or cancel
- Press **q** to quit

## Demo Mode

If the VoidLink core modules are not available, the TUI will run in demo mode with mock data.

In demo mode, you can log in with any username and password.

## Requirements

- Python 3.6 or higher
- curses library (included with Python on most systems)
- Terminal with support for colors and special characters

## Customization

You can customize the TUI by modifying the `tui.py` file. The main areas you might want to customize are:

- `DEMO_FILES`: The list of files shown in demo mode
- `VERSION`: The version number displayed in the status bar
- Menu items and structure in the `init_menus` method

## Troubleshooting

If you encounter any issues:

1. Make sure your terminal supports curses and colors
2. Try resizing your terminal window to be at least 80x24 characters
3. Check that you're running the script from the correct directory
4. Verify that the virtual environment is activated

## Integration with VoidLink

The TUI is designed to work with the VoidLink core modules. When these modules are available, it will use them for:

- User authentication
- File transfers
- Encryption
- Security scanning

When running in demo mode, these features are simulated.