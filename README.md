# note-cli — Windows

Ein natives Kommandozeilen-Tool zum Speichern und Verwalten von Notizen unter Windows. Jede Notiz wird als eigene Datei unter `.notes/db/<hash>` abgelegt. `<hash>` ist der vollständige **SHA-256-Hash** des UTF-8-Inhalts. Identische Notizen belegen dadurch nur eine Datei.

Dieser Branch `windows` enthält `note.cmd` und `note.ps1`. Die Bash-Version für macOS und Linux liegt im Branch [`mac-linux`](https://github.com/App-Akademie/note-cli/tree/mac-linux).

```powershell
git clone --branch windows --single-branch https://github.com/App-Akademie/note-cli.git
cd note-cli
```

## Installation unter Windows

Benötigt Windows PowerShell 5.1 (auf Windows 10/11 bereits enthalten). Weder WSL noch Git Bash oder zusätzliche Pakete sind nötig.

1. Dieses Repository herunterladen und entpacken oder mit Git klonen.
2. `note.cmd` und `note.ps1` im selben Ordner behalten.
3. Ein Terminal in diesem Ordner öffnen.

In PowerShell:

```powershell
.\note.cmd add "Einkaufsliste: Milch, Eier, Brot"
.\note.cmd list
.\note.cmd delete <hash>
```

In der Eingabeaufforderung (`cmd.exe`):

```bat
note.cmd add "Einkaufsliste: Milch, Eier, Brot"
note.cmd list
note.cmd delete <hash>
```

`<hash>` durch den vollständigen Hash aus `add` oder `list` ersetzen (ohne spitze Klammern). Text mit Leerzeichen oder Shell-Sonderzeichen in Anführungszeichen setzen.

Optional den Ordner mit beiden Dateien zum Benutzer-`PATH` hinzufügen. Danach ist `note` in einem neu geöffneten Terminal von überall aufrufbar.

`note.cmd` startet Windows PowerShell mit `-NoProfile` und einer nur für diesen Prozess geltenden Ausführungsrichtlinie. Es verändert keine systemweite Einstellung. Organisationsrichtlinien können weiterhin die Skriptausführung einschränken. Bei einer heruntergeladenen ZIP gegebenenfalls vor dem Entpacken in den Dateieigenschaften „Zulassen“ aktivieren.

Alternativ lässt sich das Skript direkt mit Windows PowerShell oder PowerShell 7 ausführen:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\note.ps1 add "Meine Notiz"
pwsh -NoProfile -File .\note.ps1 list
```

## Verwendung

```text
note add <text>
note list
note delete <hash>
```

Alle Notizen werden **relativ zum aktuellen Arbeitsverzeichnis** unter `.notes/db/` gespeichert, nicht neben dem Skript. Das Verzeichnis wird beim ersten `add` automatisch angelegt. Das Dateiformat ist mit der Bash-Version kompatibel: UTF-8 ohne BOM und ohne zusätzlich angehängten Zeilenumbruch. Ein vorhandener `.notes`-Ordner kann zwischen den Betriebssystemen übernommen werden.

### Notiz hinzufügen

`add` verbindet seine Textargumente mit Leerzeichen und gibt ausschließlich den 64-stelligen Hash aus:

```text
note add hello
2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
```

Derselbe Text ergibt denselben Hash und überschreibt dieselbe Datei. Es wird keine zusätzliche Notiz erzeugt.

### Notizen auflisten

`list` gibt pro Datei den Hash, einen Tabulator und den Inhalt aus. Ohne Notizen bleibt die Ausgabe leer.

### Notiz löschen

```text
note delete 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
```

Ein erfolgreiches `delete` hat keine Ausgabe. Unter Windows werden nur vollständige, kleingeschriebene SHA-256-Hashes akzeptiert. Fehler werden auf stderr ausgegeben und liefern Exitcode 1; erfolgreiche Befehle liefern Exitcode 0.

## Tests

Die Integrationstests benötigen nur Python 3. Sie arbeiten in temporären Ordnern und prüfen Speichern, Auflisten, Deduplizierung, Löschen, Unicode, Sonderzeichen und Fehlerfälle.

```powershell
$env:NOTE_CLI_VARIANT = 'powershell' # alternativ: pwsh oder cmd
python -m unittest discover -s tests -v
```

GitHub Actions prüft Windows PowerShell 5.1, PowerShell 7 und den CMD-Launcher auf Windows. Ein erfolgreicher Windows-PowerShell-Lauf stellt außerdem das ZIP-Artefakt `note-cli-windows` bereit.
