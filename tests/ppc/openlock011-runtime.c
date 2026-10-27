#include <sys/types.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <pthread.h>
#include <stdio.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL openlock line=%d errno=%d\n",__LINE__,errno);return 1;}}while(0)
static int held,channel[2],helper_error;
static void *release_lock(void *unused)
{
 char c;if(read(channel[0],&c,1)!=1){helper_error=1;return 0;}
 usleep(300000);if(close(held))helper_error=2;return 0;
}
int main(void)
{
 char path[256],c='x';int fd,a,b;pthread_t thread;struct timeval before,after;long elapsed;
 sprintf(path,"/var/tmp/jaguar/.openlock011-%d",getpid());
 fd=open(path,O_RDWR|O_CREAT|O_EXCL,0600);CHECK(fd>=0);CHECK(close(fd)==0);
 fd=open(path,O_RDWR|O_EXLOCK|O_NONBLOCK);CHECK(fd>=0);
 errno=0;CHECK(open(path,O_RDWR|O_SHLOCK|O_NONBLOCK)==-1&&errno==EWOULDBLOCK);
 errno=0;CHECK(open(path,O_RDWR|O_EXLOCK|O_NONBLOCK)==-1&&errno==EWOULDBLOCK);CHECK(close(fd)==0);
 a=open(path,O_RDONLY|O_SHLOCK|O_NONBLOCK);CHECK(a>=0);
 b=open(path,O_RDONLY|O_SHLOCK|O_NONBLOCK);CHECK(b>=0);
 errno=0;CHECK(open(path,O_RDWR|O_EXLOCK|O_NONBLOCK)==-1&&errno==EWOULDBLOCK);
 CHECK(close(a)==0&&close(b)==0);
 held=open(path,O_RDWR|O_EXLOCK|O_NONBLOCK);CHECK(held>=0);CHECK(pipe(channel)==0);
 CHECK(pthread_create(&thread,0,release_lock,0)==0);CHECK(gettimeofday(&before,0)==0);
 CHECK(write(channel[1],&c,1)==1);fd=open(path,O_RDWR|O_EXLOCK);CHECK(fd>=0);
 CHECK(gettimeofday(&after,0)==0);elapsed=(after.tv_sec-before.tv_sec)*1000000+after.tv_usec-before.tv_usec;
 CHECK(elapsed>=100000);CHECK(pthread_join(thread,0)==0);CHECK(!helper_error);CHECK(close(fd)==0);
 CHECK(close(channel[0])==0&&close(channel[1])==0);CHECK(unlink(path)==0);
 puts("real locked open: exclusive contention, shared coexistence, close release, blocking open released by another thread PASS");return 0;
}
