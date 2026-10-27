/* Exercise the production metadata mailbox across fork, exec and SIGKILL.
 * No application IPC or framebuffer responses are supplied by this probe. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <signal.h>
#include <mach/mach.h>
#define PAGE_VALID 8
#define TARGET_PAGE_ALIGN(x) (((x)+4095)&~4095)
static struct {uint32_t connection,type,address,bytes;} native_iomappings[64];
static unsigned live_kind[64],live_start[64],live_extent[64];
static void qerror(const char *format,...){va_list ap;va_start(ap,format);vfprintf(stderr,format,ap);va_end(ap);exit(99);}
/* Lifecycle never publishes a mapping event. An unexpected event is a failure. */
static void live_forget(uint32_t a,uint32_t b){exit(98);}
static void page_set_flags(uint32_t a,uint32_t b,int c){exit(98);}
static void live_bounds(void){exit(98);}
#include "remote-maps.inc"
#define CHECK(x) do {if(!(x)){fprintf(stderr,"FAIL line=%d errno=%d\n",__LINE__,errno);return 1;}}while(0)
int main(int argc,char **argv)
{
 int i,status;char path[128],fdtext[32];struct stat st;
 if(argc==3 && !strcmp(argv[1],"after-exec")){
  errno=0;CHECK(fcntl(atoi(argv[2]),F_GETFD)==-1 && errno==EBADF);
  rm_remote_sync();CHECK(fstat(rm_remote_fd,&st)==0 && st.st_nlink==1 && st.st_size==8192);
  return 0;
 }
 for(i=0;i<8;i++){
  pid_t pid=fork();CHECK(pid>=0);
  if(!pid){
   rm_remote_sync();CHECK(fstat(rm_remote_fd,&st)==0 && st.st_size==8192);
   CHECK((fcntl(rm_remote_fd,F_GETFD)&FD_CLOEXEC)!=0);
   sprintf(fdtext,"%d",rm_remote_fd);execl(argv[0],argv[0],"after-exec",fdtext,(char *)0);return 3;
  }
  CHECK(waitpid(pid,&status,0)==pid && status==0);
  sprintf(path,"/var/tmp/remaklar-remote-map-%d",pid);CHECK(unlink(path)==0);
 }
 for(i=0;i<8;i++){
  pid_t pid=fork();CHECK(pid>=0);
  if(!pid){rm_remote_sync();for(;;)pause();}
  sprintf(path,"/var/tmp/remaklar-remote-map-%d",pid);
  {int n;for(n=0;n<50 && stat(path,&st);n++)usleep(10000);CHECK(n<50);}
  CHECK(kill(pid,SIGKILL)==0);CHECK(waitpid(pid,&status,0)==pid && WIFSIGNALED(status) && WTERMSIG(status)==SIGKILL);
  CHECK(unlink(path)==0);
 }
 puts("mailbox lifecycle: 8 fork/exec + 8 SIGKILL, CLOEXEC, page-aligned backing PASS");return 0;
}
