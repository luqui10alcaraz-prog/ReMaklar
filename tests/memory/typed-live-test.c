/* Real MAP_SHARED aliases and competing native process, no device emulation.
 * SPDX-License-Identifier: MIT */
#include "typed-live.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <errno.h>
#include <string.h>
#define CHECK(x) do { if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);return 1;} } while(0)
static const struct rm_field fields[]={
 {0,4,0},{4,2,0},{6,1,0},{7,1,0},{8,8,0},{16,4,RM_HID_BITS},
 {20,4,0},{24,4,0},{28,4,0},{32,4,RM_PAIR16},{36,4,RM_BYTES},{44,8,RM_NUMBER}
};
static unsigned native_lock(volatile unsigned *p)
{
 unsigned value=1;
 __asm__ __volatile__("xchgl %0,%1" : "=r"(value), "=m"(*p) : "0"(value), "m"(*p) : "memory");
 return value;
}
int main(void)
{
 char name[]="/tmp/remaklar011-XXXXXX";int fd=mkstemp(name),ok,status;unsigned i;
 unsigned char *p,*alias;rm_u64 x;struct rm_view v;pid_t child;
 CHECK(fd>=0);CHECK(!unlink(name));CHECK(!ftruncate(fd,4096));
 p=mmap(0,4096,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);
 alias=mmap(0,4096,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);
 CHECK(p!=MAP_FAILED && alias!=MAP_FAILED && alias!=p);
 v.base=p;v.bytes=4096;v.fields=fields;v.count=sizeof(fields)/sizeof(fields[0]);v.writable=1;
 *(unsigned *)alias=0x12345678;
 CHECK(!rm_read(&v,0,4,&x) && x==0x12345678);
 CHECK(!rm_read(&v,0,1,&x) && x==0x12);
 CHECK(!rm_read(&v,1,2,&x) && x==0x3456);
 CHECK(!rm_write(&v,1,1,0xab) && *(unsigned *)alias==0x12ab5678);
 CHECK(!rm_write(&v,4,2,0x789a) && *(unsigned short *)(alias+4)==0x789a);
 CHECK(!rm_write(&v,5,1,0xbc) && *(unsigned short *)(alias+4)==0x78bc);
 CHECK(!rm_write(&v,6,1,0xde) && alias[6]==0xde && alias[7]==0);
 CHECK(!rm_write(&v,8,8,0x0123456789abcdefULL));
 CHECK(*(rm_u64 *)(alias+8)==0x0123456789abcdefULL);
 CHECK(!rm_read(&v,8,8,&x) && x==0x0123456789abcdefULL);
 CHECK(!rm_write(&v,11,2,0xaabb));
 CHECK(*(rm_u64 *)(alias+8)==0x012345aabbabcdefULL);
 *(unsigned *)(alias+16)=0x80000001;
 CHECK(!rm_read(&v,16,4,&x) && x==0x21);
 CHECK(!rm_write(&v,19,1,0x21) && *(unsigned *)(alias+16)==0x80000001);
 CHECK(!rm_cas32(&v,20,0,1,&ok) && ok && *(unsigned *)(alias+20)==1);
 CHECK(!rm_cas32(&v,20,0,2,&ok) && !ok && *(unsigned *)(alias+20)==1);
 CHECK(!rm_write(&v,20,4,0));
 CHECK(rm_write(&v,3,2,0)==EINVAL && rm_read(&v,4095,4,&x)==EINVAL);
 CHECK(rm_read(&v,40,4,&x)==EINVAL);
 CHECK(!rm_write(&v,44,8,0x0123456789abcdefULL));
 CHECK(!rm_read(&v,44,8,&x) && x==0x0123456789abcdefULL);
 CHECK(!rm_write(&v,46,2,0xaabb));CHECK(!rm_read(&v,44,8,&x) && x==0x0123aabb89abcdefULL);
 CHECK(alias[43]==0 && alias[52]==0);
 *(unsigned short *)(alias+32)=0x1234;*(unsigned short *)(alias+34)=0x5678;
 CHECK(!rm_read(&v,32,4,&x) && x==0x12345678);
 CHECK(!rm_write(&v,32,4,0xaabbccdd) && *(unsigned short *)(alias+32)==0xaabb && *(unsigned short *)(alias+34)==0xccdd);
 CHECK(!rm_write(&v,33,1,0x99) && *(unsigned short *)(alias+32)==0xaa99 && *(unsigned short *)(alias+34)==0xccdd);
 CHECK(!rm_cas32(&v,32,0xaa99ccdd,0x11223344,&ok) && ok && *(unsigned short *)(alias+32)==0x1122 && *(unsigned short *)(alias+34)==0x3344);
 alias[36]=0x12;alias[37]=0x34;alias[38]=0x56;alias[39]=0x78;
 CHECK(!rm_read(&v,36,4,&x) && x==0x12345678);
 CHECK(!rm_write(&v,38,2,0xaabb) && alias[36]==0x12 && alias[37]==0x34 && alias[38]==0xaa && alias[39]==0xbb);
 v.writable=0;CHECK(rm_write(&v,0,4,0)==EACCES);CHECK(rm_cas32(&v,20,0,1,&ok)==EACCES);v.writable=1;
 child=fork();CHECK(child>=0);
 if(!child) {
  for(i=0;i<100000;i++) {
   while(native_lock((volatile unsigned *)(alias+20))) {}
   ++*(volatile unsigned *)(alias+24);
   rm_barrier();*(volatile unsigned *)(alias+20)=0;
  }
  _exit(0);
 }
 for(i=0;i<100000;i++) {
  do {CHECK(!rm_cas32(&v,20,0,1,&ok));}while(!ok);
  CHECK(!rm_read(&v,24,4,&x));CHECK(!rm_write(&v,24,4,x+1));
  rm_barrier();CHECK(!rm_write(&v,20,4,0));
 }
 CHECK(waitpid(child,&status,0)==child && status==0);
 CHECK(*(unsigned *)(alias+24)==200000);
 child=fork();CHECK(child>=0);
 if(!child) {
  volatile unsigned *counter=(volatile unsigned *)(alias+28);
  for(i=0;i<100000;i++) {
   unsigned old,actual,value;
   do {
    old=*counter;value=(old&0xff000000)|((old+1)&0xffffff);
    __asm__ __volatile__("lock; cmpxchgl %2,%1"
       : "=a"(actual), "=m"(*counter) : "r"(value), "0"(old), "m"(*counter) : "memory","cc");
   }while(actual!=old);
  }
  _exit(0);
 }
 for(i=0;i<100000;i++)CHECK(!rm_write(&v,28,1,0xa5));
 CHECK(waitpid(child,&status,0)==child && status==0);
 CHECK(*(unsigned *)(alias+28)==0xa50186a0);
 CHECK(!mprotect(p,4096,PROT_READ));v.writable=0;
 CHECK(!rm_read(&v,0,4,&x) && x==0x12ab5678);
 CHECK(rm_write(&v,0,1,0)==EACCES && rm_read(&v,8,8,&x)==EACCES);
 CHECK(*(unsigned *)alias==0x12ab5678 && alias[6]==0xde && alias[7]==0);
 CHECK(!munmap(p,4096));CHECK(*(unsigned *)(alias+24)==200000);
 CHECK(!munmap(alias,4096) && !close(fd));
 puts("typed-live: 8/16/32/64 partial pair16 bytes bits aliases native-lock contention 200000 concurrent-partial100000 readonly cleanup OK");
 return 0;
}
