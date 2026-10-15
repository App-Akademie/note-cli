# note-cli — macOS / Linux

Ein einfaches Kommandozeilen-Tool zum Speichern und Verwalten von Notizen. Jede Notiz wird als eigene Datei unter `.notes/db/<hash>` abgelegt. `<hash>` ist der vollständige **SHA-256-Hash** des UTF-8-Inhalts. Identische Notizen belegen dadurch nur eine Datei.

Dieser Branch `mac-linux` enthält die Bash-Version für macOS und Linux. Die native Windows-Version liegt im Branch [`windows`](https://github.com/App-Akademie/note-cli/tree/windows).

```bash
git clone --branch mac-linux --single-branch https://github.com/App-Akademie/note-cli.git
cd note-cli
```

## Installation unter macOS / Linux

Das Bash-Skript `note` benötigt `bash`, `shasum` und `awk`.

```bash
chmod +x note
./note add "Einkaufsliste: Milch, Eier, Brot"
```

Optional das Skript in den `PATH` legen:

```bash
sudo ln -s "$(pwd)/note" /usr/local/bin/note
```

## Verwendung

```text
note add <text>
note list
note delete <hash>
```

Alle Notizen werden **relativ zum aktuellen Arbeitsverzeichnis** unter `.notes/db/` gespeichert, nicht neben dem Skript. Das Verzeichnis wird beim ersten `add` automatisch angelegt. Das Dateiformat ist mit der Windows-Version kompatibel: UTF-8 ohne BOM und ohne zusätzlich angehängten Zeilenumbruch. Ein vorhandener `.notes`-Ordner kann zwischen den Betriebssystemen übernommen werden.

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

Ein erfolgreiches `delete` hat keine Ausgabe. Den vollständigen Hash aus `add` oder `list` verwenden. Fehler werden auf stderr ausgegeben und liefern Exitcode 1; erfolgreiche Befehle liefern Exitcode 0.

## Tests

Die Integrationstests benötigen Python 3 und arbeiten in temporären Ordnern:

```bash
python3 -m unittest discover -s tests -v
```

GitHub Actions prüft die Bash-Version auf macOS und Linux.
