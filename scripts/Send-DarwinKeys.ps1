param([Parameter(Mandatory=$true)][string]$Text, [int]$Port=4444)
$ErrorActionPreference = 'Stop'
$client = [Net.Sockets.TcpClient]::new('127.0.0.1',$Port)
try {
    $stream = $client.GetStream()
    $map = @{ ' '='spc'; "`n"='ret'; '-'='minus'; '='='equal'; '/'='slash'; '.'='dot'; ':'='shift-semicolon'; ';'='semicolon'; '_'='shift-minus'; '|'='shift-backslash'; '>'='shift-dot' }
    foreach ($character in $Text.ToCharArray()) {
        $key = [string]$character
        if ($map.ContainsKey($key)) { $key=$map[$key] }
        elseif ($key -cmatch '^[A-Z]$') { $key='shift-'+$key.ToLowerInvariant() }
        elseif ($key -notmatch '^[a-z0-9]$') { throw "Unsupported character: $character" }
        $bytes = [Text.Encoding]::ASCII.GetBytes("sendkey $key 30`n")
        $stream.Write($bytes,0,$bytes.Length)
        Start-Sleep -Milliseconds 100
        while ($stream.DataAvailable) { $buffer=New-Object byte[] 4096; $null=$stream.Read($buffer,0,$buffer.Length) }
    }
} finally { $client.Dispose() }
