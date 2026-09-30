# note-cli

Ein einfaches Kommandozeilen-Tool zum Speichern und Verwalten von Notizen. Jede Notiz wird als eigene Datei unter `.notes/db/<hash>` abgelegt, wobei `<hash>` der SHA1-Hash des Inhalts ist (analog zu Git-Blobs). Dadurch werden identische Notizen automatisch dedupliziert.

## Installation

`note-cli` ist ein einzelnes Bash-Skript ohne Abhängigkeiten (außer `bash`, `sha1sum`/`shasum` und `awk`, die auf den meisten Systemen bereits vorhanden sind).

```bash
chmod +x note
```

Optional das Skript in den `PATH` legen, damit es überall aufrufbar ist:

```bash
sudo ln -s "$(pwd)/note" /usr/local/bin/note
```

## Verwendung

```
note add <text>
note list
note delete <hash>
```

Alle Notizen werden relativ zum aktuellen Arbeitsverzeichnis unter `.notes/db/` gespeichert – das Verzeichnis wird bei Bedarf automatisch angelegt.

### Notiz hinzufügen

```bash
./note add Einkaufsliste: Milch, Eier, Brot
```

Ausgabe:

```
Notiz gespeichert: a1b2c3d4e5f6...
```

Wird derselbe Text erneut hinzugefügt, erkennt `note-cli` den bereits vorhandenen Hash und legt keine Duplikat-Datei an:

```
Notiz existiert bereits: a1b2c3d4e5f6...
```

### Notizen auflisten

```bash
./note list
```

Zeigt alle gespeicherten Notizen mit ihrem Hash und Inhalt:

```
a1b2c3d4e5f6...  Einkaufsliste: Milch, Eier, Brot
```

Sind keine Notizen vorhanden, wird `Keine Notizen vorhanden.` ausgegeben.

### Notiz löschen

```bash
./note delete a1b2c3d4e5f6...
```

Der Hash muss dabei nicht vollständig sein wie bei Git-Kurzhashes – hier ist der komplette Hash aus `note list` bzw. `note add` erforderlich.

Ausgabe:

```
Notiz gelöscht: a1b2c3d4e5f6...
```