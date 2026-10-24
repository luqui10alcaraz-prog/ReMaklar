$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$iso = Join-Path $projectRoot 'media/darwinx86-602.iso'
$dest = Join-Path $projectRoot 'research/samples-local'
if ((Get-FileHash $iso -Algorithm SHA256).Hash -ne 'D2C4668DCD4CA4A7498ACFFAF703A19862F53AB9B58B06C51745BD33E58A584F') {
    throw 'Unexpected Darwin ISO hash'
}
New-Item -ItemType Directory -Force $dest | Out-Null
tar.exe -xf $iso -C $dest usr/bin/true usr/bin/false bin/echo bin/cat bin/ls bin/pwd usr/lib/dyld usr/lib/libSystem.B.dylib usr/lib/system/libmathCommon.A.dylib usr/lib/libobjc.A.dylib System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation
if ($LASTEXITCODE -ne 0) { throw 'Could not extract original samples' }
Get-FileHash (Join-Path $dest 'usr/bin/true'),(Join-Path $dest 'usr/bin/false') -Algorithm SHA256
