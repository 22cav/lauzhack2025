namespace Loupedeck.ExamplePlugin
{
    using System;
    using System.IO;
    using System.Threading; // Per Thread.Sleep
    using Loupedeck;
    using Newtonsoft.Json; // Necessario per leggere il JSON

    public class DynamicCommand6 : PluginDynamicCommand
    {
        // --- CONFIGURAZIONE PERCORSI ---
        // Percorso assoluto della cartella condivisa
        private const string BasePath = "/Users/matti/Documents/hackaton/lauzhack2025/ExamplePlugin/src/Actions/scripts";
        
        private string ScriptPath => Path.Combine(BasePath, "script_6.py");
        private string MetaPath => Path.Combine(BasePath, "script_6.json");
        private string DebugLogPath = "/tmp/MX_DEBUG.txt";

        // Variabili di stato
        private ActionMeta _currentMeta = new ActionMeta();
        private FileSystemWatcher _watcher;

        public DynamicCommand6()
            : base(displayName: "Dynamic AI Action 6", description: "Action updated by Python", groupName: "AI Commands")
        {
            // 1. Caricamento iniziale
            UpdateMetaFromFile();

            // 2. Avvia il FileSystemWatcher per monitorare cambiamenti
            if (Directory.Exists(BasePath))
            {
                try 
                {
                    _watcher = new FileSystemWatcher(BasePath);
                    _watcher.Filter = "script_6.json"; // Ascolta solo il file di metadati
                    _watcher.NotifyFilter = NotifyFilters.LastWrite; 
                    _watcher.Changed += OnMetaFileChanged;
                    _watcher.EnableRaisingEvents = true;
                    
                    Log("WATCHER: Avviato con successo su " + BasePath);
                }
                catch (Exception ex)
                {
                    Log("WATCHER ERROR: " + ex.Message);
                }
            }
            else
            {
                Log("WATCHER ERROR: La cartella scripts non esiste!");
            }
        }

        // Evento: Scatta quando Python modifica script_6.json
        private void OnMetaFileChanged(object sender, FileSystemEventArgs e)
        {
            // Attendiamo un attimo che Python finisca di scrivere i file (evita lock)
            Thread.Sleep(100);
            
            UpdateMetaFromFile();
            
            // Ordina alla console di ridisegnare il tasto
            this.ActionImageChanged();
        }

        // Legge il JSON e aggiorna lo stato locale
        private void UpdateMetaFromFile()
        {
            try
            {
                if (File.Exists(MetaPath))
                {
                    string jsonContent = File.ReadAllText(MetaPath);
                    var meta = JsonConvert.DeserializeObject<ActionMeta>(jsonContent);
                    
                    if (meta != null)
                    {
                        _currentMeta = meta;
                    }
                }
            }
            catch (Exception ex)
            {
                Log($"JSON ERROR: {ex.Message}");
            }
        }

        // Disegna il tasto sulla console (Immagine o Testo)
        protected override BitmapImage GetCommandImage(String actionParameter, PluginImageSize imageSize)
        {
            var builder = new BitmapBuilder(imageSize);
            builder.Clear(BitmapColor.Black);

            // Controlliamo se c'è un percorso immagine valido nel JSON
            bool imageLoaded = false;
            if (!string.IsNullOrEmpty(_currentMeta.IconPath) && File.Exists(_currentMeta.IconPath))
            {
                try 
                {
                    // Carica l'immagine generata da Python
                    var img = BitmapImage.FromFile(_currentMeta.IconPath);
                    builder.DrawImage(img);
                    imageLoaded = true;
                }
                catch (Exception ex)
                {
                    Log($"IMG LOAD ERROR: {ex.Message}");
                }
            }

            // Se non c'è immagine (o fallisce), mostra il titolo
            if (!imageLoaded)
            {
                builder.DrawText(_currentMeta.Title, BitmapColor.White);
            }
            
            return builder.ToImage();
        }

        protected override String GetCommandDisplayName(String actionParameter, PluginImageSize imageSize) => _currentMeta.Title;

        // Esegue lo script Python tramite Terminale macOS (visibile) quando premi il tasto
        protected override void RunCommand(String actionParameter)
        {
            try
            {
                if (!File.Exists(ScriptPath)) return;

                // 1. Definiamo l'interprete specifico (il tuo venv)
                string venvPython = "/Users/matti/Documents/hackaton/lauzhack2025/ExamplePlugin/src/Actions/.venv/bin/python";

                // 2. Costruiamo il comando completo che il Terminale dovrà eseguire
                string commandToRun = $"{venvPython} \"{ScriptPath}\"";

                var startInfo = new System.Diagnostics.ProcessStartInfo();

                // 3. Usiamo osascript (AppleScript) per pilotare il Terminale
                startInfo.FileName = "/usr/bin/osascript";

                // 4. Diciamo al Terminale di eseguire il nostro comando
                //    Nota: Gli escape (\") sono fondamentali qui
                startInfo.Arguments = $"-e \"tell application \\\"Terminal\\\" to do script \\\"{commandToRun}\\\"\"";

                startInfo.UseShellExecute = false;
                startInfo.CreateNoWindow = true; // La finestra C# è nascosta, il Terminale apparirà

                using (var process = System.Diagnostics.Process.Start(startInfo))
                {
                    process.WaitForExit(); // Attendiamo che il comando venga inviato al Terminale
                    Log($"AppleScript executed: {ScriptPath}");
                }
                
                // Forziamo un aggiornamento immagine (Python ci metterà un po', ma intanto notifichiamo)
                this.ActionImageChanged(actionParameter);
            }
            catch (Exception ex)
            {
                Log($"EXEC ERROR: {ex.Message}");
            }
        }

        private void Log(string message)
        {
            try { File.AppendAllText(DebugLogPath, $"[{DateTime.Now}] {message}\n"); } catch {}
        }
    }
}