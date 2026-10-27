from pathlib import Path
import subprocess,hashlib,json
p=Path('build/BootPanel-original.pdf');assert not p.exists()
with p.open('wb') as f:subprocess.run(['7z','x','-so','media/Mac OS X Jaguar Install CD.iso','Mac OS X Install Disc 1/System/Library/CoreServices/SystemStarter/QuartzDisplay.bundle/Resources/BootPanel.pdf'],stdout=f,check=True)
assert p.read_bytes().startswith(b'%PDF')
Path('reports/graphics-011/resume-validation/bootpanel-original.json').write_text(json.dumps({'source_iso':'Mac OS X Jaguar Install CD.iso','source_path':'System/Library/CoreServices/SystemStarter/QuartzDisplay.bundle/Resources/BootPanel.pdf','bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2))
