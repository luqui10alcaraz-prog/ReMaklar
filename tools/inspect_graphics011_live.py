"""Read kernel process and UBC log state through HMP, without kernel writes.
Offsets are for the preserved Darwin 6 RELEASE_I386 kernel, not arbitrary XNU.
The VM is paused only for a consistent sample and returned to its prior state.
"""
from pathlib import Path
import socket,struct,argparse,json,time
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--port',type=int,default=4445);p.add_argument('--logs',action='store_true');p.add_argument('--tail-bytes',type=int,default=0);p.add_argument('--pids',default='');p.add_argument('--directory');args=p.parse_args()
selected={int(x) for x in args.pids.split(',') if x};log_cache={};log_sizes={}
args.out.mkdir(parents=True,exist_ok=False)
s=socket.create_connection(('127.0.0.1',args.port),timeout=5);s.settimeout(30)
def recv():
 b=b''
 while not b.endswith(b'(qemu) '):
  c=s.recv(65536)
  if not c:raise RuntimeError('HMP closed')
  b+=c
 return b.decode(errors='replace')
def cmd(c):s.sendall((c+'\n').encode());return recv()
recv();running='running' in cmd('info status');cache={};serial=0
def read(a,n,physical=False):
 global serial
 # Read small kernel fields from cached pages. Physical reads are file bytes.
 if not physical:
  r=b''
  while n:
   page=a&~4095;count=min(n,4096-(a&4095))
   if page not in cache:
    f=args.out/'scratch.bin';cmd('memsave 0x%x 4096 %s'%((page+0xc0000000)&0xffffffff,f.as_posix()));cache[page]=f.read_bytes()
   r+=cache[page][a&4095:(a&4095)+count];a+=count;n-=count
  return r
 f=args.out/'scratch.bin';cmd('pmemsave 0x%x %d %s'%(a,n,f.as_posix()));return f.read_bytes()
def u(a):return struct.unpack('<I',read(a,4))[0]
def read_log(v):
 ubc=u(v+64)
 if not ubc or ubc==0xdeadd1ed:return None
 size=struct.unpack('<Q',read(ubc+24,8))[0];log_sizes[v]=size
 if size>4*1024*1024 and not args.tail_bytes:return None
 start=max(0,(size-args.tail_bytes)&~4095) if args.tail_bytes else 0
 obj=u(u(ubc+4));data=bytearray(size-start);link=u(obj+4) if args.tail_bytes else u(obj);seen=set();covered=set()
 while link and link!=obj:
  if link in seen:raise RuntimeError('cyclic UBC list')
  seen.add(link);pb=read(link,44);nxt=struct.unpack_from('<I',pb,12 if args.tail_bytes else 8)[0];offset=struct.unpack_from('<Q',pb,24)[0];phys=struct.unpack_from('<I',pb,40)[0]
  if struct.unpack_from('<I',pb,20)[0]!=obj:raise RuntimeError('UBC object mismatch')
  if start<=offset<size:data[offset-start:min(offset+4096,size)-start]=read(phys,min(4096,size-offset),True);covered.add(offset)
  if args.tail_bytes and len(covered)==(size-start+4095)//4096:break
  link=nxt
 return data,[i for i in range(start,size,4096) if i not in covered]
def log(v):
 if v not in log_cache:log_cache[v]=read_log(v)
 return log_cache[v]
try:
 cmd('stop')
 (args.out/'registers.txt').write_text(cmd('info registers'))
 cmd('screendump '+(args.out/'frame.ppm').as_posix())
 ptr=u(0x3d8b70);rows=[]
 while ptr and len(rows)<128:
  b=read(ptr,352);pid=struct.unpack_from('<I',b,36)[0];fd=struct.unpack_from('<I',b,12)[0];task=struct.unpack_from('<I',b,228)[0]
  row={'proc':hex(ptr),'pid':pid,'comm':b[195:212].split(b'\0')[0].decode(errors='replace'),'xstat':struct.unpack_from('<H',b,216)[0],'fds':[],'task':hex(task)}
  if fd and args.logs and (not selected or pid in selected):
   n=u(fd+16);tab=u(fd)
   if n<2048:
    for i in [1,2,255]:
     if i>=n:continue
     fp=u(tab+4*i)
     if not fp or (u(fp+8)>>16)!=1:continue
     v=u(fp+32);r=log(v)
     if r is not None:
      data,holes=r;name='%d-fd%d.txt'%(pid,i);(args.out/name).write_bytes(data);row['fds'].append({'fd':i,'vnode':hex(v),'file':name,'size':len(data),'source_size':log_sizes[v],'holes':holes})
  rows.append(row);ptr=struct.unpack_from('<I',b,0)[0]
 (args.out/'processes.json').write_text(json.dumps(rows,indent=2));print(json.dumps([{k:v for k,v in r.items() if k!='fds'} for r in rows],indent=2))
 symbols=Path('build/011-kernel-live-symbols.txt')
 if symbols.exists():
  lookup={name:int(a,16) for a,name in (line.split() for line in symbols.read_text().splitlines())}
  counts={name:u(lookup[name]) for name in ['_vm_page_free_count','_vm_page_active_count','_vm_page_inactive_count','_vm_page_wire_count'] if name in lookup}
  (args.out/'vm-counts.json').write_text(json.dumps(counts,indent=2)+'\n');print('VM page counts',counts)
 if args.directory:
  entry=u(0x3e3b80);entries=[];seen=set()
  while entry:
   if entry in seen:raise RuntimeError('cyclic namecache')
   seen.add(entry);b=read(entry,64);entries.append((b[33:33+b[32]].decode(errors='replace'),struct.unpack_from('<I',b,16)[0],struct.unpack_from('<I',b,24)[0]));entry=struct.unpack_from('<I',b,8)[0]
  dirs={v for name,parent,v in entries if name==args.directory and v}
  for name,parent,v in entries:
   if parent not in dirs or not v or name in ['.','..'] or '/' in name or '\\' in name:continue
   result=log(v)
   if result is not None:
    data,holes=result;(args.out/('dir-'+name)).write_bytes(data)
    print('directory file',name,'captured_bytes',len(data),'source_bytes',log_sizes[v],'holes',holes)
finally:
 if running:cmd('cont')
 s.close()
