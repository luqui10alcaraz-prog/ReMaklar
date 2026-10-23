param([switch]$Headless)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$qemu = 'C:\Program Files\qemu\qemu-system-i386.exe'
$qemuImg = 'C:\Program Files\qemu\qemu-img.exe'
$iso = Join-Path $projectRoot 'media/darwinx86-602.iso'
$disk = Join-Path $projectRoot 'vm/darwin602.qcow2'
if (!(Test-Path $iso)) { throw "Missing ISO: $iso" }
if ((Get-FileHash $iso -Algorithm SHA256).Hash -ne 'D2C4668DCD4CA4A7498ACFFAF703A19862F53AB9B58B06C51745BD33E58A584F') { throw 'Unexpected ISO SHA-256' }
New-Item -ItemType Directory -Force (Join-Path $projectRoot 'vm'),(Join-Path $projectRoot 'logs') | Out-Null
if (!(Test-Path $disk)) {
    & $qemuImg create -f qcow2 $disk 2G
    if ($LASTEXITCODE -ne 0) { throw 'Could not create virtual disk' }
}
$display = if ($Headless) { 'none' } else { 'sdl' }
$qemuArgs = @('-machine','pc-i440fx-5.0','-accel','tcg','-cpu','pentium3','-m','128','-smp','1',
    '-drive',"file=$($disk.Replace('\','/')),format=qcow2,if=ide,index=0",
    '-drive',"file=$($iso.Replace('\','/')),media=cdrom,readonly=on,if=ide,index=2",
    '-boot','d','-nic','none','-vga','std','-display',$display,
    '-monitor','tcp:127.0.0.1:4444,server=on,wait=off',
    '-serial',"file:$projectRoot/logs/serial.log",'-no-reboot')
& $qemu @qemuArgs
exit $LASTEXITCODE
