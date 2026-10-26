/* Real POSIX shared objects, FD sizing, offsets and lifetime across exec.
 * SPDX-License-Identifier: MIT */
#include <sys/types.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define C(x) do{if(!(x)){printf("FAIL shm line=%d errno=%d\n",__LINE__,errno);return __LINE__;}}while(0)
int main(int argc,char **argv) {
 char name[30];char *a,*b;int fd,other,status;pid_t child;struct stat st;
 if(argc==3 && !strcmp(argv[1],"--child")) {
  fd=shm_open(argv[2],O_RDWR,0);C(fd>=0);a=mmap(0,4096,PROT_READ|PROT_WRITE,MAP_SHARED,fd,4096);C(a!=MAP_FAILED && !memcmp(a,"before12",8));memcpy(a,"after123",8);C(!munmap(a,4096) && !close(fd));puts("POSIX shm child exec real mapping OK");return 0;
 }
 C(argc==2);sprintf(name,"RM010.%ld",(long)getpid());
 fd=shm_open(name,O_CREAT|O_EXCL|O_RDWR,0600);C(fd>=0);C(!ftruncate(fd,8192));C(!fstat(fd,&st) && st.st_size==8192);
 errno=0;other=shm_open(name,O_CREAT|O_EXCL|O_RDWR,0600);C(other==-1 && errno==EEXIST);
 a=mmap(0,8192,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);C(a!=MAP_FAILED && !a[4096]);memcpy(a+4096,"before12",8);
 other=shm_open(name,O_RDWR,0);C(other>=0);b=mmap(0,4096,PROT_READ|PROT_WRITE,MAP_SHARED,other,4096);C(b!=MAP_FAILED && !memcmp(b,"before12",8));
 child=fork();C(child>=0);if(!child){execl(argv[1],"shm010","--child",name,(char *)0);_exit(99);}
 C(waitpid(child,&status,0)==child && WIFEXITED(status) && !WEXITSTATUS(status));C(!memcmp(b,"after123",8) && !memcmp(a+4096,"after123",8));
 C(!shm_unlink(name));errno=0;C(shm_open(name,O_RDONLY,0)==-1 && errno==ENOENT);C(!memcmp(b,"after123",8));
 C(!munmap(a,8192) && !munmap(b,4096) && !close(fd) && !close(other));
 puts("POSIX shm real create EEXIST truncate aliases fork exec unlink lifetime cleanup OK");return 0;
}
