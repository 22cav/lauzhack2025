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
                
                // Monitor everything that might change the file
                _watcher.NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.CreationTime | NotifyFilters.Size | NotifyFilters.FileName;

                // Use a debounce mechanism to avoid spamming updates
                // (FileSystemWatcher can fire multiple events for a single file write)
                _watcher.Changed += OnFileChanged;
                _watcher.Created += OnFileChanged;
                _watcher.Renamed += OnFileChanged;
                _watcher.Deleted += OnFileChanged; // Handle deletion too just in case

                _watcher.EnableRaisingEvents = true;
            }
            catch (Exception ex)
            {
                Console.WriteLine("Watcher Error: " + ex.Message);
            }
        }

        private DateTime _lastUpdate = DateTime.MinValue;
        private readonly object _lock = new object();

        private void OnFileChanged(object sender, FileSystemEventArgs e)
        {
            lock (_lock)
            {
                // Simple debounce: ignore updates if they happen within 100ms of the last one
                if ((DateTime.Now - _lastUpdate).TotalMilliseconds < 100)
                    return;

                _lastUpdate = DateTime.Now;
            }

            // Force update on a thread pool thread to avoid blocking the watcher
            System.Threading.Tasks.Task.Run(async () => 
            {
                // Give the file a moment to be fully written/released
                await System.Threading.Tasks.Task.Delay(100); 
                this.ActionImageChanged(null);
            });
        }

        protected override void RunCommand(String actionParameter)
        {
            // Percorso del log generale per il plugin C# (non catturerà l'output di python, che vedrai a video)
            string desktopLog = "/tmp/MX_DEBUG.txt";

            try
            {
                File.AppendAllText(desktopLog, $"\n[{DateTime.Now}] BUTTON PRESSED via Terminal.\n");

                if (!File.Exists(ScriptPath))
                {
                    File.AppendAllText(desktopLog, "ERROR: Script non trovato!\n");
                    return;
                }

                // --- MODIFICA PER PERMESSI MICROFONO ---
                
                // 1. Definiamo l'interprete specifico (il tuo venv)
                string venvPython = "/Users/matti/Documents/hackaton/lauzhack2025/ExamplePlugin/src/Actions/.venv/bin/python";
                
                // 2. Costruiamo il comando completo che il Terminale dovrà digitare ed eseguire
                //    Sintassi: /path/to/venv/python "/path/to/script.py"
                string commandToRun = $"{venvPython} \"{ScriptPath}\"";

                var startInfo = new System.Diagnostics.ProcessStartInfo();
                
                // 3. Invece di lanciare Python direttamente, lanciamo 'osascript' (AppleScript)
                startInfo.FileName = "/usr/bin/osascript";
                
                // 4. Diciamo al Terminale di eseguire il nostro comando.
                //    Questo aprirà una nuova finestra di terminale con i permessi giusti.
                //    Attenzione agli escape delle virgolette (\")
                startInfo.Arguments = $"-e \"tell application \\\"Terminal\\\" to do script \\\"{commandToRun}\\\"\"";

                startInfo.UseShellExecute = false;
                startInfo.CreateNoWindow = true; // La finestra di C# è nascosta, ma quella del Terminale apparirà

                using (var process = System.Diagnostics.Process.Start(startInfo))
                {
                    process.WaitForExit();
                    File.AppendAllText(desktopLog, "AppleScript inviato correttamente al Terminale.\n");
                }
                
                // Forziamo un aggiornamento immagine (Python ci metterà un po', ma intanto aggiorniamo)
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