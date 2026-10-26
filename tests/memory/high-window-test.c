/* Isolated native proof before changing the translator address model.
 * SPDX-License-Identifier: MIT */
#include "high-window.h"
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <signal.h>
#include <errno.h>
#define CHECK(x) do {if(!(x)){fprintf(stderr,"FAIL high-window line=%d\n",__LINE__);return 1;}}while(0)
int main(void)
{
 char name[]="/tmp/high011-XXXXXX";int fd,status;pid_t pid;uintptr_t host;
 struct rlimit limit;limit.rlim_cur=limit.rlim_max=0;setrlimit(RLIMIT_CORE,&limit);
 CHECK((uint32_t)rm_high_map(0xff000000,12*1024*1024,PROT_READ|PROT_WRITE,MAP_FIXED|MAP_PRIVATE|MAP_ANONYMOUS,-1,0)==0xff000000);
 host=rm_high_host(0xff002000);CHECK(host<0xc0000000 && host!=0xff002000);
 CHECK(rm_high_guest(host)==0xff002000 && rm_high_backing(host,4));
 *(volatile unsigned *)host=0x12345678;CHECK(*(volatile unsigned *)rm_high_host(0xff002000)==0x12345678);
 fd=mkstemp(name);CHECK(fd>=0 && !unlink(name) && !ftruncate(fd,8192));
 CHECK((uint32_t)rm_high_map(0xff002000,4096,PROT_READ|PROT_WRITE,MAP_FIXED|MAP_SHARED,fd,4096)==0xff002000);
 CHECK((uint32_t)rm_high_map(0xfe000000,4096,PROT_READ|PROT_WRITE,MAP_FIXED|MAP_SHARED,fd,4096)==0xfe000000);
 *(volatile unsigned *)rm_high_host(0xfe000000)=0xaabbccdd;
 CHECK(*(volatile unsigned *)rm_high_host(0xff002000)==0xaabbccdd);
 pid=fork();CHECK(pid>=0);
 if(!pid){*(volatile unsigned *)rm_high_host(0xfe000000)=0x13579bdf;_exit(0);}
 CHECK(waitpid(pid,&status,0)==pid && status==0 && *(volatile unsigned *)rm_high_host(0xff002000)==0x13579bdf);
 CHECK(!rm_high_protect(0xff002000,4096,PROT_READ));
 pid=fork();CHECK(pid>=0);if(!pid){*(volatile unsigned *)rm_high_host(0xff002000)=0;_exit(1);}
 CHECK(waitpid(pid,&status,0)==pid && WIFSIGNALED(status) && (WTERMSIG(status)==SIGSEGV || WTERMSIG(status)==SIGBUS));
 CHECK(!rm_high_unmap(0xff002000,4096));
 CHECK(rm_high_backing(host,4)); /* retained private reservation, no host hole */
 CHECK(!rm_high_contains(0xff002000,4));
 CHECK(rm_high_protect(0xff002000,4096,PROT_READ|PROT_WRITE)==-1);
 CHECK(rm_high_protect(0xff001000,8192,PROT_READ|PROT_WRITE)==-1);
 CHECK(rm_high_contains(0xff001000,4096));
 CHECK((uint32_t)rm_high_map(0xff002000,4096,PROT_READ|PROT_WRITE,MAP_FIXED|MAP_SHARED,fd,4096)==0xff002000);
 CHECK(*(volatile unsigned *)rm_high_host(0xff002000)==0x13579bdf);
 CHECK(rm_high_map(0xff002000,4096,PROT_READ|PROT_EXEC,MAP_FIXED|MAP_PRIVATE|MAP_ANONYMOUS,-1,0)==-1 && errno==ENOTSUP);
 CHECK(!rm_high_unmap(0xfe000000,4096) && !rm_high_unmap(0xff000000,12*1024*1024));
 CHECK(!rm_high_backing(host,4) && !rm_high_contains(0xff002000,4));CHECK(!close(fd));
 puts("high-window isolated: ff000000/ff002000 real shared file offsets fork protection partial-unmap hole-protection reservation cleanup OK");return 0;
}
