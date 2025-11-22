# WebSocket API Documentation

## Overview

The Python gesture engine and C# plugin communicate via a simple TCP socket connection using plain text messages.

## Connection Details

- **Protocol**: TCP
- **Host**: `127.0.0.1` (localhost)
- **Port**: `5000`
- **Direction**: Python (client) → C# (server)

## Message Format

Messages are plain text strings terminated with a newline character (`\n`).

```
<GESTURE_NAME>\n
```

## Supported Messages

### `OPEN_PALM`

**Description:** Sent when an open palm gesture is detected (all 4 fingers extended).

**Example:**
```
OPEN_PALM\n
```

**C# Event:** `gestureOpenPalm`

---

### `CLOSED_FIST`

**Description:** Sent when a closed fist gesture is detected (no fingers extended).

**Example:**
```
CLOSED_FIST\n
```

**C# Event:** `gestureClosedFist`

---

### `POINTING`

**Description:** Sent when a pointing gesture is detected (only index finger extended).

**Example:**
```
POINTING\n
```

**C# Event:** `gesturePointing`

---

## Connection Lifecycle

### Server (C# Plugin)

1. **Startup**: Creates `TcpListener` on port 5000
2. **Listening**: Accepts incoming connections
3. **Connection**: Spawns thread to handle each client
4. **Receiving**: Reads messages from stream until connection closes
5. **Shutdown**: Stops listener and closes all connections

### Client (Python Engine)

1. **Startup**: Attempts to connect to server
2. **Connection**: Establishes socket connection
3. **Sending**: Sends gesture messages as they are detected
4. **Error Handling**: If connection fails, runs in "offline mode"
5. **Shutdown**: Closes socket on exit

## Error Handling

### Connection Refused (Python)

If the C# plugin is not running, the Python engine will:
- Log: `"Could not connect to 127.0.0.1:5000. Running in offline mode."`
- Continue running and displaying gestures locally
- Not attempt to reconnect (manual restart required)

### Socket Exception (C#)

If a socket error occurs, the C# plugin will:
- Log the error
- Close the problematic connection
- Continue listening for new connections

## Implementation Examples

### Python (Sending)

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 5000))

# Send gesture
message = "OPEN_PALM\n"
sock.sendall(message.encode('utf-8'))
```

### C# (Receiving)

```csharp
var listener = new TcpListener(IPAddress.Loopback, 5000);
listener.Start();
var client = listener.AcceptTcpClient();

using var stream = client.GetStream();
var buffer = new byte[1024];
int bytesRead = stream.Read(buffer, 0, buffer.Length);
string message = Encoding.UTF8.GetString(buffer, 0, bytesRead).Trim();
// message = "OPEN_PALM"
```

## Future Enhancements

Potential improvements to the API:

- **Bidirectional communication**: Allow C# to send commands to Python (e.g., calibration, sensitivity adjustment)
- **JSON format**: Structured messages with metadata (confidence, timestamp, hand side)
- **Authentication**: Token-based auth to prevent unauthorized connections
- **Compression**: For high-frequency gesture data
- **WebSocket upgrade**: Use WebSocket protocol for better tooling and debugging
