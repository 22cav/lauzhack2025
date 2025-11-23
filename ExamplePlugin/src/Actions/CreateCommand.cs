namespace Loupedeck.ExamplePlugin
{
    using System;
    using System.IO; // Aggiunto per brevità

    public class CreateCommand : PluginDynamicCommand
    {
        // 1. Dichiariamo il watcher a livello di classe (così vive per sempre)
        private FileSystemWatcher _watcher;
        
        // Percorsi (meglio tenerli qui per usarli ovunque)
        private const string ScriptPath = "/Users/matti/Documents/hackaton/lauzhack2025/ExamplePlugin/src/Actions/scripts/create.py";
        private const string IconFolder = "/Users/matti/Documents/hackaton/lauzhack2025/ExamplePlugin/src/Actions/scripts";
        private const string IconFile = "status_icon.png";

        public CreateCommand()
            : base(displayName: "Create Command", description: "Create a new command", groupName: "Commands")
        {
            // 2. Inizializziamo il Watcher SUBITO, appena il plugin parte
            InitializeWatcher();
        }

        private void InitializeWatcher()
        {
            try 
            {
                if (!Directory.Exists(IconFolder)) return;

                _watcher = new FileSystemWatcher(IconFolder, IconFile);
                
                // Monitoriamo tutto: scrittura, creazione, dimensione
                _watcher.NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.CreationTime | NotifyFilters.Size;

                // Quando il file cambia, ricarica l'immagine
                _watcher.Changed += (s, e) => { this.ActionImageChanged(null); }; // null aggiorna tutte le istanze
                _watcher.Created += (s, e) => { this.ActionImageChanged(null); };
                // Importante: a volte i file vengono sovrascritti non modificati
                _watcher.Renamed += (s, e) => { this.ActionImageChanged(null); };

                _watcher.EnableRaisingEvents = true;
            }
            catch (Exception ex)
            {
                Console.WriteLine("Watcher Error: " + ex.Message);
            }
        }

        protected override void RunCommand(String actionParameter)
        {
            string desktopLog = "/tmp/MX_DEBUG.txt";

            try
            {
                File.AppendAllText(desktopLog, $"\n[{DateTime.Now}] BUTTON PRESSED.\n");

                if (!File.Exists(ScriptPath))
                {
                    File.AppendAllText(desktopLog, "ERROR: Script non trovato!\n");
                    return;
                }

                var startInfo = new System.Diagnostics.ProcessStartInfo();
                // Usa il python del venv come facevi
                startInfo.FileName = "/Users/matti/Documents/hackaton/lauzhack2025/ExamplePlugin/src/Actions/.venv/bin/python"; 
                startInfo.Arguments = $"\"{ScriptPath}\"";
                startInfo.UseShellExecute = false;
                startInfo.CreateNoWindow = true;
                startInfo.RedirectStandardOutput = true;
                startInfo.RedirectStandardError = true;

                using (var process = System.Diagnostics.Process.Start(startInfo))
                {
                    // Leggiamo l'output per debug
                    string stderr = process.StandardError.ReadToEnd();
                    string stdout = process.StandardOutput.ReadToEnd();
                    process.WaitForExit();

                    if (!string.IsNullOrEmpty(stderr))
                        File.AppendAllText(desktopLog, $"PYTHON ERROR: {stderr}\n");
                    else
                        File.AppendAllText(desktopLog, $"PYTHON SUCCESS: {stdout}\n");
                }
                
                // Forziamo un aggiornamento manuale alla fine per sicurezza
                this.ActionImageChanged(actionParameter);
            }
            catch (Exception ex)
            {
                File.AppendAllText(desktopLog, $"C# CRASH: {ex.Message}\n");
            }
        }

        protected override String GetCommandDisplayName(String actionParameter, PluginImageSize imageSize) => "Create";

        protected override BitmapImage GetCommandImage(String actionParameter, PluginImageSize imageSize)
        {
            string fullIconPath = Path.Combine(IconFolder, IconFile);

            // Retry logic: se Python sta scrivendo, C# potrebbe fallire la lettura. Riprova brevemente.
            for (int i = 0; i < 3; i++) 
            {
                try
                {
                    if (File.Exists(fullIconPath))
                    {
                        using (var stream = new FileStream(fullIconPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
                        {
                            using (var memoryStream = new MemoryStream())
                            {
                                stream.CopyTo(memoryStream);
                                return BitmapImage.FromArray(memoryStream.ToArray());
                            }
                        }
                    }
                }
                catch (IOException) 
                {
                    System.Threading.Thread.Sleep(50); // Aspetta 50ms e riprova se il file è bloccato
                }
            }

            // Fallback
            var builder = new BitmapBuilder(imageSize);
            builder.DrawText("...");
            return builder.ToImage();
        }
    }
}