namespace Loupedeck.ExamplePlugin
{
    using System;
    using System.IO;

    public class UndoCommand : PluginDynamicCommand
    {
        // Percorsi
        private const string ScriptPath = "/Users/matti/Documents/hackaton/lauzhack2025/ExamplePlugin/src/Actions/scripts/undo.py";

        public UndoCommand()
            : base(displayName: "Undo Command", description: "Undo the last action", groupName: "Commands")
        {
        }

        protected override void RunCommand(String actionParameter)
        {
            string desktopLog = "/tmp/MX_DEBUG_UNDO.txt";

            try
            {
                File.AppendAllText(desktopLog, $"\n[{DateTime.Now}] UNDO BUTTON PRESSED via Terminal.\n");

                if (!File.Exists(ScriptPath))
                {
                    File.AppendAllText(desktopLog, "ERROR: Script undo.py non trovato!\n");
                    return;
                }

                string venvPython = "/Users/matti/Documents/hackaton/lauzhack2025/ExamplePlugin/src/Actions/.venv/bin/python";
                string commandToRun = $"{venvPython} \"{ScriptPath}\"";

                var startInfo = new System.Diagnostics.ProcessStartInfo();
                startInfo.FileName = "/usr/bin/osascript";
                startInfo.Arguments = $"-e \"tell application \\\"Terminal\\\" to do script \\\"{commandToRun}\\\"\"";

                startInfo.UseShellExecute = false;
                startInfo.CreateNoWindow = true;

                using (var process = System.Diagnostics.Process.Start(startInfo))
                {
                    process.WaitForExit();
                    File.AppendAllText(desktopLog, "AppleScript undo inviato correttamente al Terminale.\n");
                }
            }
            catch (Exception ex)
            {
                File.AppendAllText(desktopLog, $"C# CRASH: {ex.Message}\n");
            }
        }

        protected override String GetCommandDisplayName(String actionParameter, PluginImageSize imageSize) => "Undo";

        protected override BitmapImage GetCommandImage(String actionParameter, PluginImageSize imageSize)
        {
            var builder = new BitmapBuilder(imageSize);
            builder.DrawText("Undo");
            return builder.ToImage();
        }
    }
}