namespace Loupedeck.ExamplePlugin
{
    using System;
    using System.IO;

    public class RevertCommand : PluginDynamicCommand
    {
        // Define paths for the Revert script
        private const string ScriptPath = "/Users/matti/Documents/hackaton/lauzhack2025/ExamplePlugin/src/Actions/scripts/revert.py";
        
        public RevertCommand()
            : base(displayName: "Revert Command", description: "Revert the last action", groupName: "Commands")
        {
        }

        protected override void RunCommand(String actionParameter)
        {
            string desktopLog = "/tmp/MX_DEBUG_REVERT.txt";

            try
            {
                File.AppendAllText(desktopLog, $"\n[{DateTime.Now}] REVERT BUTTON PRESSED via Terminal.\n");

                if (!File.Exists(ScriptPath))
                {
                    File.AppendAllText(desktopLog, "ERROR: Script non trovato!\n");
                    return;
                }

                // 1. Define the specific interpreter (venv)
                string venvPython = "/Users/matti/Documents/hackaton/lauzhack2025/ExamplePlugin/src/Actions/.venv/bin/python";
                
                // 2. Construct the command to run via Terminal
                string commandToRun = $"{venvPython} \"{ScriptPath}\"";

                var startInfo = new System.Diagnostics.ProcessStartInfo();
                
                // 3. Use osascript to run in Terminal
                startInfo.FileName = "/usr/bin/osascript";
                startInfo.Arguments = $"-e \"tell application \\\"Terminal\\\" to do script \\\"{commandToRun}\\\"\"";

                startInfo.UseShellExecute = false;
                startInfo.CreateNoWindow = true;

                using (var process = System.Diagnostics.Process.Start(startInfo))
                {
                    process.WaitForExit();
                    File.AppendAllText(desktopLog, "AppleScript sent successfully to Terminal.\n");
                }
            }
            catch (Exception ex)
            {
                File.AppendAllText(desktopLog, $"C# CRASH: {ex.Message}\n");
            }
        }

        protected override String GetCommandDisplayName(String actionParameter, PluginImageSize imageSize) => "Revert";
    }
}