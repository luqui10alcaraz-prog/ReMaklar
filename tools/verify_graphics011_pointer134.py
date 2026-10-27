"""Verify original Aqua pointer displacement in actual physical VESA bytes."""
from pathlib import Path
import hashlib,json
from PIL import Image
base=Path('reports/graphics-011/joint134/captures')
names=['1793076709806847518','1793076731754132378'];frames=[];record={'hardware_command':'mouse_move 40 30','mouse':'QEMU HID Mouse over original AppleUSBOHCI/IOUSBHIDDriver','framebuffer':'physical 0xfd000000, 1024x768x32 BGRX','frames':[]}
for name in names:
 ppm=base/(name+'.ppm');vram=base/(name+'.vram');im=Image.open(ppm).convert('RGB');raw=vram.read_bytes()
 assert im.size==(1024,768) and len(raw)==3145728
 physical=Image.frombytes('RGB',im.size,raw,'raw','BGRX');assert physical.tobytes()==im.tobytes()
 shape={(i%1024,i//1024):c for i,c in enumerate(im.getdata()) if c!=(66,107,173)}
 assert 50<len(shape)<500,len(shape);frames.append(shape)
 record['frames'].append({'ppm':str(ppm),'vram':str(vram),'png':str(ppm.with_suffix('.png')),'rgb_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'vram_sha256':hashlib.sha256(raw).hexdigest(),'pointer_bounds':[min(x for x,y in shape),min(y for x,y in shape),max(x for x,y in shape),max(y for x,y in shape)],'pointer_pixels':len(shape),'different_pixels_from_physical_VRAM':0})
assert {(x+40,y+30):c for (x,y),c in frames[0].items()}==frames[1]
record['result']='PASS identical original pointer pixels translated exactly (40,30), all framebuffer pixels verified against physical VESA'
out=Path('reports/graphics-011/resume-validation/pointer134-framebuffer-verification.json');assert not out.exists();out.write_text(json.dumps(record,indent=2)+'\n');print(out)
