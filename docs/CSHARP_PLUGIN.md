# C# Logitech Plugin

## Overview

The C# plugin integrates with Logitech G Hub to translate gesture events from the Python engine into device actions. It implements a WebSocket server to receive gesture messages and raises plugin events that users can bind to device buttons.

## Project Structure

```
src/
├── GestureControlPlugin.cs      # Main plugin class
├── GestureServer.cs              # WebSocket server
├── GestureControlApplication.cs  # Application logic
├── Helpers/
│   ├── PluginLog.cs              # Logging utility
│   └── PluginResources.cs        # Resource management
└── package/
    ├── events/                   # Event definitions
    └── metadata/                 # Plugin metadata
```

## Main Components

### GestureControlPlugin.cs

**Purpose**: Main entry point for the plugin, manages lifecycle and initialization.

**Key Properties:**
- `UsesApplicationApiOnly`: `true` - Plugin doesn't need UI application
- `HasNoApplication`: `true` - Universal plugin (works across all apps)

**Lifecycle Methods:**
- `Load()`: Initializes events and starts gesture server
- `Unload()`: Stops gesture server

**Registered Events:**
- `gestureOpenPalm`: Triggered when open palm detected
- `gestureClosedFist`: Triggered when closed fist detected
- `gesturePointing`: Triggered when pointing detected

### GestureServer.cs

**Purpose**: TCP server that receives gesture messages from Python engine.

**Configuration:**
- **Host**: `IPAddress.Loopback` (127.0.0.1)
- **Port**: `5000`

**Threading Model:**
- Main thread: Accepts new connections
- Thread pool: Handles each client connection
- Background thread: Server runs in background, doesn't block plugin

**Message Processing:**
```csharp
OPEN_PALM    → gestureOpenPalm
CLOSED_FIST  → gestureClosedFist
POINTING     → gesturePointing
```

**Error Handling:**
- `SocketException`: Logged, server continues
- Client disconnect: Closes connection, ready for new client
- Event raise failure: Logged, doesn't crash server

### GestureControlApplication.cs

**Purpose**: Application-level plugin logic (minimal for this plugin).

**Note**: This plugin is application-agnostic (works with any app).

### Helpers

#### PluginLog.cs
- **Purpose**: Wrapper around Logitech plugin logging
- **Methods**: `Init()`, `Info()`, `Error()`
- **Location**: Logs written to Logitech G Hub log directory

#### PluginResources.cs
- **Purpose**: Manages embedded resources (icons, assets)
- **Methods**: `Init()`, resource loading utilities

## Building the Plugin

```bash
cd GestureControlPlugin
dotnet build
```

**Output**: Build artifacts in `bin/Debug/`

**Hot Reload**: Logitech G Hub automatically detects changes during development.

## Plugin Configuration

### LoupedeckPackage.yaml

Defines plugin metadata:
- Display name
- Description
- Version
- Capabilities

**Required capability for this plugin:**
```yaml
pluginCapabilities: []
```

Note: `HasHapticMapping` removed since we're not using haptics for gesture control.

### Event Configuration

#### DefaultEventSource.yaml
Defines available events and their metadata.

#### eventMapping.yaml
Maps events to device capabilities (haptics, etc.).

## Testing the Plugin

1. **Build** the plugin: `dotnet build`
2. **Start Logitech G Hub**
3. **Verify** plugin appears in available plugins
4. **Start Python engine** to send gestures
5. **Bind events** to device buttons in G Hub
6. **Trigger gestures** and verify plugin events fire

## Debugging

### Enable Logging

Logs are written via `PluginLog`:
```csharp
PluginLog.Info("Message");
PluginLog.Error(exception, "Error message");
```

### Check Logs

Logitech G Hub log directory (varies by OS):
- Windows: `%LocalAppData%\Logitech\Logi Options Plus\logs`
- macOS: `~/Library/Logs/Logitech/`

### Common Issues

**Plugin not appearing:**
- Check build completed successfully
- Verify `.csproj` references correct SDK version
- Restart Logitech G Hub

**Events not triggering:**
- Check Python engine is connected (see Python logs)
- Verify event names match exactly in code and YAML
- Check PluginLog for error messages

**Connection refused:**
- Ensure C# plugin (server) starts before Python engine (client)
- Check firewall isn't blocking localhost:5000

## Deployment

### Development
Build creates symbolic link that G Hub follows for hot reload.

### Production
Use `LogiPluginTool` to package for distribution:
```bash
LogiPluginTool package GestureControlPlugin
```

Generates `.plugin` file for Logitech Marketplace upload.

## Code Style

- Uses C# XML documentation comments
- Follows Logitech plugin SDK conventions
- Private fields prefixed with `_`
- Thread-safe implementation for server

## Future Enhancements

- **Gesture customization**: Allow users to define custom gestures
- **Sensitivity settings**: Adjustable detection thresholds
- **Multiple engines**: Support multiple Python engine connections
- **Gesture history**: Track and display recent gestures
- **Advanced actions**: Chain multiple gestures, gesture sequences
