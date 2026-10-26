/* Guest-high mappings backed by real host files; compare native low reference. */
#include <sys/types.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <mach/mach.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#ifndef MAP_ANONYMOUS
#define MAP_ANONYMOUS MAP_ANON
#endif
extern kern_return_t mach_make_memory_entry_64(mach_port_t,unsigned long long *,unsigned long long,vm_prot_t,mach_port_t *,mach_port_t);
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL high guest line=%d errno=%d\n",__LINE__,errno);return 1;}}while(0)
int main(void)
{
#ifdef __ppc__
 unsigned base=0xff000000U;
#else
 unsigned base=0x50000000U;
#endif
 char name[]="/tmp/remaklar-high011-XXXXXX";int fd,status;pid_t pid;void *reserve,*a,*alias;unsigned value=0;
 fd=mkstemp(name);CHECK(fd>=0);CHECK(!unlink(name));CHECK(!ftruncate(fd,8192));
 reserve=mmap((void *)base,12*1024*1024,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);CHECK(reserve==(void *)base);
 a=mmap((void *)(base+8192),4096,PROT_READ|PROT_WRITE,MAP_SHARED|MAP_FIXED,fd,4096);CHECK(a==(void *)(base+8192));
 alias=mmap(0,4096,PROT_READ|PROT_WRITE,MAP_SHARED,fd,4096);CHECK(alias!=MAP_FAILED && alias!=a);
 *(volatile unsigned *)a=0x12345678;CHECK(*(volatile unsigned *)alias==0x12345678);
 *(volatile unsigned *)alias=0xaabbccdd;CHECK(*(volatile unsigned *)a==0xaabbccdd);
 CHECK(lseek(fd,0,SEEK_SET)==0 && write(fd,a,4)==4 && lseek(fd,0,SEEK_SET)==0 && read(fd,&value,4)==4 && value==0xaabbccdd);
 {
  unsigned long long length=4096;mach_port_t entry=0;vm_address_t view=0;
  CHECK(!mach_make_memory_entry_64(mach_task_self(),&length,(unsigned)a,3,&entry,0));
  CHECK(!vm_map(mach_task_self(),&view,4096,0,1,entry,0,0,3,3,VM_INHERIT_NONE));
  CHECK(*(volatile unsigned *)view==0xaabbccdd);
  *(volatile unsigned *)view=0x13579bdf;CHECK(*(volatile unsigned *)a==0x13579bdf);
  *(volatile unsigned *)a=0xaabbccdd;CHECK(*(volatile unsigned *)view==0xaabbccdd);
  CHECK(!vm_deallocate(mach_task_self(),view,4096) && !mach_port_deallocate(mach_task_self(),entry));
 }
 pid=fork();CHECK(pid>=0);if(!pid){*(volatile unsigned *)a=0x2468ace0;_exit(0);}
 CHECK(waitpid(pid,&status,0)==pid && status==0 && *(volatile unsigned *)alias==0x2468ace0);
 CHECK(!mprotect(a,4096,PROT_READ));CHECK(*(volatile unsigned *)a==0x2468ace0);
 CHECK(!mprotect(a,4096,PROT_READ|PROT_WRITE));
 CHECK(!munmap(a,4096));CHECK(mprotect(a,4096,PROT_READ)==-1);
 a=mmap((void *)(base+8192),4096,PROT_READ|PROT_WRITE,MAP_SHARED|MAP_FIXED,fd,4096);CHECK(a==(void *)(base+8192) && *(volatile unsigned *)a==0x2468ace0);
 CHECK(!vm_protect(mach_task_self(),(vm_address_t)a,4096,0,VM_PROT_READ));CHECK(*(volatile unsigned *)a==0x2468ace0);
 CHECK(!munmap(alias,4096));CHECK(!munmap(reserve,12*1024*1024));CHECK(!close(fd));
 puts("guest high MAP_FIXED exact file-offset aliases TCG syscall Mach-entry fork protect hole remap vm_protect cleanup OK");return 0;
}
