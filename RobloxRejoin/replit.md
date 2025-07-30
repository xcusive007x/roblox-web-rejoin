# Roblox Rejoiner Bot

## Overview

This is a Flask-based web application that controls a Roblox bot designed to automatically rejoin Roblox games when disconnected. The bot integrates with MuMu Player (Android emulator) and uses ADB (Android Debug Bridge) to interact with the Roblox mobile app. The system provides a web interface for configuration, monitoring, and control of the bot operations.

## User Preferences

Preferred communication style: Simple, everyday language in Thai and English.

## Recent Changes (July 30, 2025)

✓ Successfully converted Python script from ZIP file to Flask web application
✓ Installed Android Debug Bridge (ADB) for device communication
✓ Created comprehensive web interface with 3 main panels:
  - Bot Control Panel (start/stop functionality)
  - Configuration Panel (settings management)
  - System Logs Panel (real-time monitoring)
✓ Added connection testing for MuMu Player and ADB
✓ Implemented Thai language support for user messages
✓ Added installation guide and setup instructions
✓ Enhanced error handling for cross-platform compatibility
✓ **NEW: Added Screen Detection & Auto-Click System**:
  - Real-time screenshot capture from Android device
  - Manual tap functionality with coordinate input
  - Template creation from screenshot regions
  - Auto-click based on image template matching
  - Game element detection using OpenCV
  - Full web interface for screen interaction controls
  - **Interactive UI workflow**: Take Screenshot → Detect & Enlarge → Click to Select → Save & Tap
  - Visual coordinate selection with click markers and animations
  - Automatic screenshot refresh after successful tap operations

## System Architecture

The application follows a simple Flask web application architecture with the following key characteristics:

### Frontend Architecture
- **Technology**: HTML templates with Bootstrap 5 (dark theme)
- **Styling**: Custom CSS with Font Awesome icons
- **JavaScript**: Vanilla JavaScript for dynamic interactions
- **UI Framework**: Bootstrap-based responsive design with dark theme
- **Real-time Updates**: AJAX-based status updates and log streaming

### Backend Architecture
- **Framework**: Flask web framework
- **Structure**: Monolithic application with separation of concerns
- **Bot Controller**: Separate `bot_controller.py` module handling bot logic
- **Session Management**: Flask sessions with configurable secret key
- **Logging**: Python's built-in logging with custom log message handling

## Key Components

### 1. Web Application (`app.py`)
- Flask server handling HTTP requests
- Configuration management (JSON-based)
- Bot lifecycle management (start/stop/status)
- Real-time log message collection and display
- Session management for web interface state

### 2. Bot Controller (`bot_controller.py`)
- Core bot logic for Roblox game rejoining
- MuMu Player process management
- ADB connection and Android device interaction
- Threaded operation for non-blocking execution
- Configurable check intervals and game settings
- Integrated screen detection capabilities

### 3. Screen Detection System (`screen_detector.py`)
- Real-time screenshot capture via ADB commands
- OpenCV-based template matching and image recognition
- Manual and automated screen tapping functionality
- Template creation and management from screenshot regions
- Game element detection using edge detection algorithms
- Cross-platform compatibility with PIL fallback

### 4. Configuration System
- JSON-based configuration (`config.json`)
- Persistent settings storage
- Default configuration creation
- Support for VIP server connections
- User-configurable emulator paths and game settings

### 5. Web Interface Templates
- Base template with common layout and navigation
- Index page with control panel and real-time monitoring
- Status indicators for bot, MuMu Player, Roblox, and ADB
- Configuration forms for bot settings
- **Screen Detection Panel**: Interactive screenshot viewer, manual tap controls, template creation tools, and auto-click interface

## Data Flow

1. **User Interaction**: Users interact with the web interface to configure and control the bot
2. **Configuration Management**: Settings are stored in `config.json` and loaded by both web app and bot
3. **Bot Control**: Web interface starts/stops bot instances running in separate threads
4. **Process Monitoring**: Bot continuously monitors MuMu Player and Roblox processes
5. **Game Rejoining**: When disconnection is detected, bot automatically restarts the game
6. **Status Updates**: Real-time status information is provided through AJAX requests
7. **Logging**: All operations are logged and displayed in the web interface

## External Dependencies

### Core Dependencies
- **Flask**: Web framework for the user interface
- **MuMu Player**: Android emulator for running Roblox mobile app
- **ADB (Android Debug Bridge)**: Communication with Android emulator
- **Bootstrap 5**: Frontend UI framework
- **Font Awesome**: Icon library for UI elements

### System Requirements
- **Windows Environment**: Primary target platform (process detection uses `tasklist`)
- **MuMu Player Installation**: Required Android emulator
- **ADB Tools**: Android SDK platform tools for device communication

### Integration Points
- **Roblox API**: Game joining through place IDs and VIP server codes
- **Process Management**: System process monitoring and control
- **File System**: Configuration and log file management

## Deployment Strategy

### Development Environment
- **Local Development**: Flask development server on port 5000
- **Debug Mode**: Enabled for development with hot reloading
- **Host Configuration**: Binds to all interfaces (0.0.0.0) for accessibility

### Production Considerations
- **Process Management**: Bot runs in separate threads to avoid blocking web interface
- **Error Handling**: Comprehensive exception handling for external process interactions
- **Logging**: Structured logging for debugging and monitoring
- **Session Security**: Configurable session secret key via environment variables

### File Structure
```
/
├── app.py                 # Main Flask application
├── bot_controller.py      # Bot logic and control
├── main.py               # Application entry point
├── config.json           # Configuration storage
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   └── index.html       # Main interface
├── static/              # Static assets
│   ├── css/custom.css   # Custom styles
│   └── js/app.js        # Frontend JavaScript
└── attached_assets/     # Additional configuration files
```

The architecture prioritizes simplicity and maintainability while providing a robust web interface for managing the Roblox rejoining bot. The separation between web interface and bot logic allows for independent development and testing of each component.