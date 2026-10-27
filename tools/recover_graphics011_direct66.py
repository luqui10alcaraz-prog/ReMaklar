"""Recover unsynced direct66 logs from a read-only 512 MiB physical RAM dump.
Known layouts/addresses are specific to the preserved Darwin 6 i386 machine.
No VM execution, kernel writes, or filesystem repair is performed here.
"""
import argparse,bisect,hashlib,json,mmap,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('ram',type=Path);p.add_argument('out',type=Path);p.add_argument('--symbols',type=Path,default=Path('build/011-kernel-live-symbols.txt'));args=p.parse_args()
assert args.ram.stat().st_size==512*1024*1024
args.out.mkdir(parents=True,exist_ok=False)
file=args.ram.open('rb');ram=mmap.mmap(file.fileno(),0,access=mmap.ACCESS_READ)
def physical_u(a):return struct.unpack_from('<I',ram,a)[0]
def physical(a):
 d=physical_u(0x03160000+(a>>22)*4);assert d&1
 if d&128:return (d&0xffc00000)+(a&0x3fffff)
 t=physical_u((d&0xfffff000)+((a>>12)&1023)*4);assert t&1
 return (t&0xfffff000)+(a&4095)
def read(a,n):
 result=b'';a=(a+0xc0000000)&0xffffffff
 while n:
  size=min(n,4096-(a&4095));at=physical(a);result+=ram[at:at+size];a+=size;n-=size
 return result
def u(a):return struct.unpack('<I',read(a,4))[0]
symbols=sorted((int(a,16),name) for a,name in (line.split() for line in args.symbols.read_text().splitlines()));lookup=dict((name,a) for a,name in symbols);values=[a for a,name in symbols]
def cached(vp):
 ubc=u(vp+64)
 if not ubc or ubc==0xdeadd1ed:return None
 size=struct.unpack('<Q',read(ubc+24,8))[0];assert size<4*1024*1024
 obj=u(u(ubc+4));data=bytearray(size);link=u(obj);pages=[];seen=set()
 while link and link!=obj:
  assert link not in seen;seen.add(link);b=read(link,44);nxt=struct.unpack_from('<I',b,8)[0];offset=struct.unpack_from('<Q',b,24)[0];at=struct.unpack_from('<I',b,40)[0]
  assert struct.unpack_from('<I',b,20)[0]==obj
  if offset<size:data[offset:min(size,offset+4096)]=ram[at:at+min(4096,size-offset)]
  pages.append({'page':hex(link),'offset':offset,'physical':hex(at)});link=nxt
 return bytes(data),{'vnode':hex(vp),'object':hex(obj),'bytes':size,'resident_pages':pages,'holes':[i for i in range(0,size,4096) if i not in {r['offset'] for r in pages}]}
entry=u(lookup['_nclruhead']);entries=[];seen=set()
while entry:
 assert entry not in seen;seen.add(entry);b=read(entry,64)
 entries.append((b[33:33+b[32]].decode(errors='replace'),struct.unpack_from('<I',b,16)[0],struct.unpack_from('<I',b,24)[0]));entry=struct.unpack_from('<I',b,8)[0]
dirs={vp for name,parent,vp in entries if name=='graphics011-joint66'};manifest={}
for name,parent,vp in entries:
 if parent not in dirs or not vp:continue
 result=cached(vp)
 if result is None:continue
 data,row=result;assert not row['holes'];assert '/' not in name and '\\' not in name
 (args.out/name).write_bytes(data);row['sha256']=hashlib.sha256(data).hexdigest();manifest[name]=row
mailbox,row=cached(0x20d9c5c8);(args.out/'exiting-mailbox.bin').write_bytes(mailbox)
proc=read(0x20c1b214,352);identity={'pid':struct.unpack_from('<I',proc,36)[0],'p_xstat':struct.unpack_from('<H',proc,216)[0],'mailbox_magic':hex(struct.unpack_from('<I',mailbox)[0]),'mailbox_pid':struct.unpack_from('<I',mailbox,4)[0],'mailbox':row}
(args.out/'exiting-process.json').write_text(json.dumps(identity,indent=2)+'\n')
(args.out/'manifest.json').write_text(json.dumps({'ram_sha256':hashlib.sha256(ram).hexdigest(),'files':manifest},indent=2)+'\n')
print('Recovered',len(manifest),'complete resident logs. Exiting identity:',{k:v for k,v in identity.items() if k!='mailbox'})
