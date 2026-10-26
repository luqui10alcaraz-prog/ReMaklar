/* Original libc syscall() exercises Darwin's indirect PPC ABI. */
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <fcntl.h>
int main(void) {
 int r,e;
 if(syscall(20)!=getpid())return 1;
 if(syscall(4,1,"",0)!=0)return 2;
 errno=0;r=syscall(5,"/Remaklar011DefinitelyMissing",O_RDONLY,0);e=errno;
 if(r!=-1 || e!=ENOENT)return 3;
 errno=0;r=syscall(180,0x1fff0305,0,0,0,0);e=errno;
 printf("indirect getpid/write/open OK; real kdebug_trace result=%d errno=%d\n",r,e);
 return 0;
}
