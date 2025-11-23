namespace Loupedeck.ExamplePlugin
{
    using System;
    using System.IO;
    using System.Threading; // Per Thread.Sleep
    using Loupedeck;
    using Newtonsoft.Json; // Necessario per leggere il JSON

    // Classe per mappare i dati del file .json
    public class ActionMeta7
    {
        public string Title { get; set; } = "";
        public string IconPath { get; set; } = ""; 
    }

    public class DynamicCommand7 : PluginDynamicCommand
    {
        // --- CONFIGURAZIONE PERCORSI ---
        // Percorso assoluto della cartella condivisa
        private const string BasePath = "/Users/matti/Documents/hackaton/ExamplePlugin/src/Actions/scripts";
        
        private string ScriptPath => Path.Combine(BasePath, "script_7.py");
        private string MetaPath => Path.Combine(BasePath, "script_7.json");
        private string DebugLogPath = "/tmp/MX_DEBUG.txt";

        // Variabili di stato
        private ActionMeta7 _currentMeta = new ActionMeta7();
        private FileSystemWatcher _watcher;

        public DynamicCommand7()
            : base(displayName: "Dynamic AI Action 7", description: "Action updated by Python", groupName: "AI Commands")
        {
            // 1. Caricamento iniziale
            UpdateMetaFromFile();

            // 2. Avvia il FileSystemWatcher per monitorare cambiamenti
            if (Directory.Exists(BasePath))
            {
                try 
                {
                    _watcher = new FileSystemWatcher(BasePath);
                    _watcher.Filter = "script_7.json"; // Ascolta solo il file di metadati
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

        // Evento: Scatta quando Python modifica script_7.json
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
                    var meta = JsonConvert.DeserializeObject<ActionMeta7>(jsonContent);
                    
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

        // Esegue lo script Python quando premi il tasto
        protected override void RunCommand(String actionParameter)
        {
            try
            {
                if (!File.Exists(ScriptPath)) return;

                var startInfo = new System.Diagnostics.ProcessStartInfo();
                startInfo.FileName = "/usr/bin/python3"; // Assicurati che sia il path giusto di python3
                startInfo.Arguments = $"\"{ScriptPath}\"";
                startInfo.UseShellExecute = false;
                startInfo.CreateNoWindow = true;
                
                System.Diagnostics.Process.Start(startInfo);
                Log($"Executed: {ScriptPath}");
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