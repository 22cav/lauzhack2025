namespace Loupedeck.GestureControlPlugin
{
    using System;
    using System.Net;
    using System.Net.Sockets;
    using System.Text;
    using System.Threading;

    /// <summary>
    /// TCP server that receives gesture messages from the Python gesture recognition engine.
    /// Listens on localhost:5000 for incoming connections and translates gesture messages
    /// into plugin events that can be bound to device actions.
    /// </summary>
    public class GestureServer
    {
        /// <summary>
        /// TCP listener that accepts gesture engine connections.
        /// </summary>
        private TcpListener _listener;

        /// <summary>
        /// Background thread that runs the server listen loop.
        /// </summary>
        private Thread _serverThread;

        /// <summary>
        /// Flag indicating whether the server is currently running.
        /// Volatile to ensure thread-safe reads/writes.
        /// </summary>
        private volatile bool _isRunning;

        /// <summary>
        /// Reference to the main plugin instance for raising events.
        /// </summary>
        private readonly GestureControlPlugin _plugin;

        /// <summary>
        /// Initializes a new instance of the <see cref="GestureServer"/> class.
        /// </summary>
        /// <param name="plugin">The main plugin instance.</param>
        public GestureServer(GestureControlPlugin plugin)
        {
            this._plugin = plugin;
        }

        /// <summary>
        /// Starts the WebSocket server and begins listening for gesture engine connections.
        /// Creates a background thread to handle incoming connections without blocking the main plugin thread.
        /// </summary>
        public void Start()
        {
            if (this._isRunning) return;

            this._isRunning = true;
            this._listener = new TcpListener(IPAddress.Loopback, 5000);
            this._listener.Start();
            
            this._serverThread = new Thread(this.ListenLoop);
            this._serverThread.IsBackground = true;
            this._serverThread.Start();
            
            PluginLog.Info("GestureServer started on port 5000");
        }

        /// <summary>
        /// Stops the WebSocket server and closes all active connections.
        /// Waits up to 1 second for the server thread to complete before forcing termination.
        /// </summary>
        public void Stop()
        {
            this._isRunning = false;
            this._listener?.Stop();
            this._serverThread?.Join(1000);
            PluginLog.Info("GestureServer stopped");
        }

        /// <summary>
        /// Main server loop that accepts incoming client connections.
        /// Spawns a thread pool worker for each connected client.
        /// Runs until the server is stopped via <see cref="Stop"/>.
        /// </summary>
        private void ListenLoop()
        {
            while (this._isRunning)
            {
                try
                {
                    var client = this._listener.AcceptTcpClient();
                    ThreadPool.QueueUserWorkItem(this.HandleClient, client);
                }
                catch (SocketException)
                {
                    // Listener stopped
                }
                catch (Exception ex)
                {
                    PluginLog.Error(ex, "Error accepting client");
                }
            }
        }

        /// <summary>
        /// Handles communication with a connected gesture engine client.
        /// Reads gesture messages from the TCP stream and processes them until the connection closes.
        /// </summary>
        /// <param name="state">TcpClient object representing the connected client.</param>
        private void HandleClient(object state)
        {
            var client = (TcpClient)state;
            using (client)
            using (var stream = client.GetStream())
            {
                var buffer = new byte[1024];
                while (this._isRunning && client.Connected)
                {
                    try
                    {
                        int bytesRead = stream.Read(buffer, 0, buffer.Length);
                        if (bytesRead == 0) break;

                        var message = Encoding.UTF8.GetString(buffer, 0, bytesRead).Trim();
                        this.ProcessMessage(message);
                    }
                    catch
                    {
                        break;
                    }
                }
            }
        }

        /// <summary>
        /// Processes a gesture message received from the Python engine.
        /// Maps gesture names to plugin event names and raises the corresponding event.
        /// </summary>
        /// <param name="message">Gesture name string (e.g., "OPEN_PALM", "CLOSED_FIST", "POINTING").</param>
        /// <remarks>
        /// Supported gestures:
        /// - OPEN_PALM → gestureOpenPalm
        /// - CLOSED_FIST → gestureClosedFist
        /// - POINTING → gesturePointing
        /// </remarks>
        private void ProcessMessage(string message)
        {
            // Message format: "GESTURE_NAME"
            // e.g. "OPEN_PALM", "CLOSED_FIST", "POINTING"
            
            string eventName = "";
            switch (message)
            {
                case "OPEN_PALM":
                    eventName = "gestureOpenPalm";
                    break;
                case "CLOSED_FIST":
                    eventName = "gestureClosedFist";
                    break;
                case "POINTING":
                    eventName = "gesturePointing";
                    break;
                default:
                    return;
            }

            if (!string.IsNullOrEmpty(eventName))
            {
                // Raise event on main thread if necessary, but PluginEvents.RaiseEvent is usually thread-safe or handles it.
                // However, best practice is to ensure we don't block the socket thread.
                try 
                {
                    this._plugin.PluginEvents.RaiseEvent(eventName);
                    PluginLog.Info($"Raised event: {eventName}");
                }
                catch (Exception ex)
                {
                    PluginLog.Error(ex, $"Failed to raise event {eventName}");
                }
            }
        }
    }
}
