namespace Loupedeck.GestureControlPlugin
{
    using System;

    /// <summary>
    /// Main plugin class for the Gesture Control Plugin.
    /// Integrates webcam-based gesture recognition with Logitech G Hub.
    /// Manages the lifecycle of the gesture recognition WebSocket server and registers plugin events.
    /// </summary>
    public class GestureControlPlugin : Plugin
    {
        /// <summary>
        /// WebSocket server that receives gesture messages from the Python engine.
        /// </summary>
        private GestureServer _gestureServer;

        /// <summary>
        /// Gets a value indicating whether this is an API-only plugin.
        /// </summary>
        public override Boolean UsesApplicationApiOnly => true;

        /// <summary>
        /// Gets a value indicating whether this is a Universal plugin (works across all applications).
        /// </summary>
        public override Boolean HasNoApplication => true;

        /// <summary>
        /// Initializes a new instance of the <see cref="GestureControlPlugin"/> class.
        /// Sets up logging, resources, and the gesture server.
        /// </summary>
        public GestureControlPlugin()
        {
            // Initialize the plugin log.
            PluginLog.Init(this.Log);

            // Initialize the plugin resources.
            PluginResources.Init(this.Assembly);
            
            this._gestureServer = new GestureServer(this);
        }

        /// <summary>
        /// Called when the plugin is loaded by Logitech G Hub.
        /// Initializes plugin events and starts the gesture server to begin listening for gesture messages.
        /// </summary>
        public override void Load()
        {
            this.InitEvents();
            this._gestureServer.Start();
        }

        /// <summary>
        /// Called when the plugin is unloaded by Logitech G Hub.
        /// Stops the gesture server and cleans up resources.
        /// </summary>
        public override void Unload()
        {
            this._gestureServer.Stop();
        }
        
        /// <summary>
        /// Registers plugin events that can be bound to device actions in Logitech G Hub.
        /// Creates three events corresponding to the detected gestures: Open Palm, Closed Fist, and Pointing.
        /// </summary>
        private void InitEvents()
        {
            this.PluginEvents.AddEvent("gestureOpenPalm", "Open Palm", "Triggered when open palm is detected");
            this.PluginEvents.AddEvent("gestureClosedFist", "Closed Fist", "Triggered when closed fist is detected");
            this.PluginEvents.AddEvent("gesturePointing", "Pointing", "Triggered when pointing gesture is detected");
        }
    }
}
