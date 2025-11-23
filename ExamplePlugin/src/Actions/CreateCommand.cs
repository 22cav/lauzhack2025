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
                // TODO: CONTROLLARE SE QUESTE 10 RIGHE FUNZIONANO
                using (var watcher = new System.IO.FileSystemWatcher(scriptFolder, "status_icon.png"))
                {
                    watcher.NotifyFilter = System.IO.NotifyFilters.LastWrite | System.IO.NotifyFilters.CreationTime;
                    watcher.Changed += (s, e) => {
                        // Trigger UI update when icon changes
                        this.ActionImageChanged(actionParameter);
                    };
                    watcher.Created += (s, e) => {
                        this.ActionImageChanged(actionParameter);
                    };
                    watcher.EnableRaisingEvents = true;

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
                // TODO: CONTROLLARE SE SERVE E FUNZIONA Final update to ensure we reset if needed
                this.ActionImageChanged(actionParameter);
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
        {   // TODO: MODIFICARE QUI PER CARICARE L'ICONA DINAMICAMENTE E QUESTO PEZZO DA CONTROLLARE
            string scriptPath = @"c:\Users\luca_\OneDrive\Desktop\Unpoditutto\EPFL\hackathon\lauzhack2025\ExamplePlugin\src\Actions\scripts\create.py";
            string statusIconPath = System.IO.Path.Combine(System.IO.Path.GetDirectoryName(scriptPath), "status_icon.png");

            if (System.IO.File.Exists(statusIconPath))
            {
                try
                {
                    // Read file into memory to avoid locking it
                    using (var stream = new System.IO.FileStream(statusIconPath, System.IO.FileMode.Open, System.IO.FileAccess.Read, System.IO.FileShare.ReadWrite))
                    {
                        using (var memoryStream = new System.IO.MemoryStream())
                        {
                            stream.CopyTo(memoryStream);
                            memoryStream.Position = 0;
                            // Assuming BitmapImage can be created from stream or we use BitmapBuilder
                            // Loupedeck SDK usually has BitmapImage.FromArray or similar, but let's try standard way if available
                            // or fallback to BitmapBuilder if we can't easily load png.
                            // Actually, Loupedeck's BitmapImage can be constructed from byte array.
                            return BitmapImage.FromArray(memoryStream.ToArray());
                        }
                    }
                }
                catch
                {
                    // Fallback if reading fails
                }
            }
            // TODO: MODIFICARE QUA CHE SE RIUSCIAMO A PASSARE IL TESTO DEL COLORE INVECE DELL'ICONA è TOP
            var builder = new BitmapBuilder(imageSize);
            builder.DrawText("Create");
            return builder.ToImage();
        }
    }
}
