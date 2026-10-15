# Native Windows implementation; compatible with Windows PowerShell 5.1 and PowerShell 7.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $utf8

try {
    $notesDir = Join-Path $PWD.Path '.notes/db'
    if ($args.Count -eq 0) {
        throw 'Usage: note add <text> | note list | note delete <hash>'
    }

    switch -CaseSensitive -Exact ($args[0]) {
        'add' {
            if ($args.Count -lt 2) {
                throw 'note text required'
            }
            $text = [string]::Join(' ', [string[]]$args[1..($args.Count - 1)])
            $sha256 = [System.Security.Cryptography.SHA256]::Create()
            try {
                $hash = [BitConverter]::ToString($sha256.ComputeHash($utf8.GetBytes($text))).Replace('-', '').ToLowerInvariant()
            }
            finally {
                $sha256.Dispose()
            }
            [void][System.IO.Directory]::CreateDirectory($notesDir)
            [System.IO.File]::WriteAllText((Join-Path $notesDir $hash), $text, $utf8)
            [Console]::WriteLine($hash)
        }
        'list' {
            if ([System.IO.Directory]::Exists($notesDir)) {
                foreach ($file in (Get-ChildItem -LiteralPath $notesDir -File | Sort-Object Name)) {
                    # Bash command substitution removes trailing line feeds, too.
                    $text = $utf8.GetString([System.IO.File]::ReadAllBytes($file.FullName)).TrimEnd([char]10)
                    [Console]::WriteLine("{0}`t{1}", $file.Name, $text)
                }
            }
        }
        'delete' {
            if ($args.Count -lt 2) {
                throw 'hash required'
            }
            $hash = [string]$args[1]
            # Only allow complete hashes, never paths or wildcard expressions.
            if ($hash -cnotmatch '\A[0-9a-f]{64}\z') {
                throw 'invalid hash: expected a complete lowercase SHA-256 hash'
            }
            $path = Join-Path $notesDir $hash
            if (-not [System.IO.File]::Exists($path)) {
                throw "no note with hash $hash"
            }
            [System.IO.File]::Delete($path)
        }
        default {
            throw 'Usage: note add <text> | note list | note delete <hash>'
        }
    }
    exit 0
}
catch {
    [Console]::Error.WriteLine('error: ' + $_.Exception.Message)
    exit 1
}
