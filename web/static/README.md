# VoidLink Web Interface

This directory contains the web interface for VoidLink, a secure file sharing application.

## Features

- Modern, responsive design that works on desktop and mobile devices
- Drag-and-drop file uploads
- File management with preview capabilities
- Secure file sharing with customizable permissions
- Real-time progress indicators for file transfers
- Comprehensive dashboard with storage usage statistics
- Activity tracking for all file operations

## Getting Started

To use the VoidLink web interface, you need to run the web server:

```bash
python web_server.py
```

Then open your browser and navigate to:

```
http://localhost:8000
```

## Demo Mode

If the VoidLink core modules are not available, the web server will run in demo mode with mock data.

In demo mode, you can log in with:
- Username: demo
- Password: password

## Directory Structure

- `index.html` - The main HTML file
- `css/` - Contains all CSS stylesheets
- `js/` - Contains all JavaScript files
- `img/` - Contains images and icons

## Customization

You can customize the appearance by modifying the CSS variables in `css/styles.css`. The main color scheme is defined at the top of the file.

## Browser Compatibility

The web interface is compatible with:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Security Considerations

In a production environment, make sure to:
1. Serve the web interface over HTTPS
2. Implement proper authentication and session management
3. Set appropriate Content Security Policy headers
4. Regularly update all dependencies