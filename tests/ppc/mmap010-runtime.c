/* mmap ABI offsets, actual file sharing/COW, anonymous pages and errors.
 * SPDX-License-Identifier: MIT */
#include <sys/types.h>
#include <sys/mman.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#define C(x) do{if(!(x)){printf("FAIL mmap line=%d errno=%d\n",__LINE__,errno);return __LINE__;}}while(0)
int main(void) {
 char path[80],data[8192],readback[8];char *a,*b,*copy,*anon,*unaligned;int fd;
 sprintf(path,"/tmp/mmap010-%ld",(long)getpid());memset(data,'x',sizeof(data));memcpy(data+4096,"original",8);
 fd=open(path,O_CREAT|O_EXCL|O_RDWR,0600);C(fd>=0);C(write(fd,data,sizeof(data))==sizeof(data));
 a=mmap(0,4096,PROT_READ|PROT_WRITE,MAP_SHARED,fd,4096);C(a!=MAP_FAILED && !memcmp(a,"original",8));
 b=mmap(0,4096,PROT_READ|PROT_WRITE,MAP_SHARED,fd,4096);C(b!=MAP_FAILED);
 copy=mmap(0,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE,fd,4096);C(copy!=MAP_FAILED);
 memcpy(copy,"private!",8);C(!memcmp(a,"original",8));memcpy(a,"shared!!",8);C(!memcmp(b,"shared!!",8) && !memcmp(copy,"private!",8));
 C(lseek(fd,4096,SEEK_SET)==4096 && read(fd,readback,8)==8 && !memcmp(readback,"shared!!",8));
 anon=mmap(0,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANON,-1,0);C(anon!=MAP_FAILED && !anon[0]);anon[0]=42;C(anon[0]==42);
 errno=0;C(mmap(0,4096,PROT_READ,MAP_PRIVATE,-1,0)==MAP_FAILED && errno==EBADF);
 unaligned=mmap(0,4096,PROT_READ,MAP_PRIVATE,fd,1);C(unaligned!=MAP_FAILED && unaligned[0]=='x');C(!munmap(unaligned,4096));
 errno=0;C(mmap(0,4096,PROT_READ,MAP_PRIVATE|MAP_ANON,fd,0)==MAP_FAILED && errno==EINVAL);
 C(!munmap(a,4096) && !munmap(b,4096) && !munmap(copy,4096) && !munmap(anon,4096));C(!close(fd) && !unlink(path));
 puts("mmap real file offset unaligned shared COW anonymous EBADF EINVAL munmap cleanup OK");return 0;
}
