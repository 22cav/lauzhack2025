namespace Loupedeck.ExamplePlugin
{
    using System;

    // This class implements an example command that counts button presses.

    public class CreateCommand : PluginDynamicCommand
    {

        // Initializes the command class.
        public CreateCommand()
            : base(displayName: "Create Command", description: "Create a new command", groupName: "Commands")
        {
        }

        // This method is called when the user executes the command.
        protected override void RunCommand(String actionParameter)
        {
            // DEBUG: Continuiamo a usare /tmp per sicurezza
            string desktopLog = "/tmp/MX_DEBUG.txt";

            try
            {
                // --- HARDCODED PATH (La via veloce) ---
                string scriptPath = "/Users/matti/Documents/hackaton/ExamplePlugin/src/Actions/scripts/create.py";

                // Log iniziale
                System.IO.File.AppendAllText(desktopLog, $"\n[{DateTime.Now}] BUTTON PRESSED.\n");
                System.IO.File.AppendAllText(desktopLog, $"Target Script: {scriptPath}\n");

                // Controllo esistenza file (Cruciale)
                if (!System.IO.File.Exists(scriptPath))
                {
                    System.IO.File.AppendAllText(desktopLog, "ERROR: File Python non trovato in quel percorso!\n");
                    return;
                }

                var startInfo = new System.Diagnostics.ProcessStartInfo();
                startInfo.FileName = "/usr/bin/python3";
                startInfo.Arguments = $"\"{scriptPath}\"";
                startInfo.UseShellExecute = false;
                startInfo.CreateNoWindow = true;
                startInfo.RedirectStandardOutput = true;
                startInfo.RedirectStandardError = true;

                using (var process = System.Diagnostics.Process.Start(startInfo))
                {
                    // Catturiamo l'output per capire se Python parte
                    string stderr = process.StandardError.ReadToEnd();
                    string stdout = process.StandardOutput.ReadToEnd();
                    process.WaitForExit();

                    if (!string.IsNullOrEmpty(stderr))
                        System.IO.File.AppendAllText(desktopLog, $"PYTHON ERROR: {stderr}\n");
                    else
                        System.IO.File.AppendAllText(desktopLog, $"PYTHON SUCCESS: {stdout}\n");
                }
            }
            catch (Exception ex)
            {
                System.IO.File.AppendAllText(desktopLog, $"C# CRASH: {ex.Message}\n");
            }
        }

        // This method is called when Loupedeck needs to show the command on the console or the UI.
        protected override String GetCommandDisplayName(String actionParameter, PluginImageSize imageSize) =>
            "Create";

        protected override BitmapImage GetCommandImage(String actionParameter, PluginImageSize imageSize)
        {
            var builder = new BitmapBuilder(imageSize);
            builder.DrawText("Create");
            return builder.ToImage();
        }
    }
}
