"""Bounded framebuffer captures; reports changes and saves original VESA bytes."""
from pathlib import Path
import argparse,hashlib,json,socket,time
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--port',type=int,default=4445);p.add_argument('--seconds',type=int,default=240);p.add_argument('--interval',type=float,default=5);p.add_argument('--pause-on-window-candidate',action='store_true');args=p.parse_args()
assert 0<args.seconds<=600 and 1<=args.interval<=60
args.out.mkdir(parents=True,exist_ok=False);prior=None;deadline=time.monotonic()+args.seconds
def command(c):
 with socket.create_connection(('127.0.0.1',args.port),timeout=5) as s:
  s.settimeout(30);b=b''
  while not b.endswith(b'(qemu) '):b+=s.recv(65536)
  s.sendall((c+'\n').encode());b=b''
  while not b.endswith(b'(qemu) '):b+=s.recv(65536)
  return b
while time.monotonic()<deadline:
 stamp=time.time_ns();ppm=args.out/f'{stamp}.ppm'
 try:command('screendump '+ppm.as_posix())
 except OSError as error:
  print('Capture retry after monitor contention: '+str(error),flush=True);time.sleep(1);continue
 im=Image.open(ppm);digest=hashlib.sha256(im.tobytes()).hexdigest()
 if digest!=prior:
  png=ppm.with_suffix('.png');im.save(png);vram=ppm.with_suffix('.vram');command('pmemsave 0xfd000000 3145728 '+vram.as_posix())
  crop=im.crop((0,64,im.width,im.height));nonblue=crop.width*crop.height-sum(n for n,c in crop.getcolors(2000000) if c==(66,107,173))
  row={'time_ns':stamp,'png':str(png),'sha256_pixels':digest,'vram_sha256':hashlib.sha256(vram.read_bytes()).hexdigest(),'nonblue_below_y64':nonblue}
  with (args.out/'frames.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
  print(json.dumps(row),flush=True)
  dark=sum(n for n,c in crop.getcolors(2000000) if max(c)<50)
  if args.pause_on_window_candidate and nonblue>5000 and crop.width*crop.height-nonblue>50000 and dark<10000:
   command('stop');print('VM paused on a window candidate; visual and trace verification required.',flush=True);break
 prior=digest;time.sleep(min(args.interval,max(0,deadline-time.monotonic())))
