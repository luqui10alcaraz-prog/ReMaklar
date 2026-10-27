#include <sys/types.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL filelock line=%d errno=%d\n",__LINE__,errno);return 1;}}while(0)
int main(void)
{
 char path[256],token='x';int fd,channel[2],status,r,e;pid_t parent=getpid(),child;struct flock lock,query;struct timeval before,after;long elapsed;
 CHECK(sizeof(lock)==24);sprintf(path,"/var/tmp/jaguar/.filelock011-%d",parent);
 fd=open(path,O_RDWR|O_CREAT|O_EXCL,0600);CHECK(fd>=0);CHECK(write(fd,"x",1)==1);
 memset(&lock,0,sizeof(lock));lock.l_start=0x100000123LL;lock.l_len=0x202;lock.l_type=F_WRLCK;lock.l_whence=SEEK_SET;
 CHECK(fcntl(fd,F_SETLK,&lock)==0);errno=0;CHECK(fcntl(fd,F_GETLK,(void *)1)==-1&&errno==EFAULT);
 CHECK(pipe(channel)==0);errno=0;CHECK(fcntl(channel[0],F_SETLK,&lock)==-1&&errno==EBADF);
 child=fork();CHECK(child>=0);
 if(!child){
  query=lock;CHECK(fcntl(fd,F_GETLK,&query)==0);CHECK(query.l_type==F_WRLCK&&query.l_pid==parent&&query.l_start==lock.l_start&&query.l_len==lock.l_len&&query.l_whence==SEEK_SET);
  query=lock;query.l_start+=0x400;CHECK(fcntl(fd,F_GETLK,&query)==0&&query.l_type==F_UNLCK);
  errno=0;r=fcntl(fd,F_SETLK,&lock);e=errno;CHECK(r==-1&&(e==EAGAIN||e==EACCES));
  CHECK(gettimeofday(&before,0)==0);CHECK(write(channel[1],&token,1)==1);CHECK(fcntl(fd,F_SETLKW,&lock)==0);
  CHECK(gettimeofday(&after,0)==0);elapsed=(after.tv_sec-before.tv_sec)*1000000+after.tv_usec-before.tv_usec;CHECK(elapsed>=100000);
  CHECK(close(fd)==0);return 0;
 }
 CHECK(read(channel[0],&token,1)==1);usleep(300000);lock.l_type=F_UNLCK;CHECK(fcntl(fd,F_SETLK,&lock)==0);
 CHECK(waitpid(child,&status,0)==child&&WIFEXITED(status)&&WEXITSTATUS(status)==0);
 lock.l_type=F_WRLCK;CHECK(fcntl(fd,F_GETLK,&lock)==0&&lock.l_type==F_UNLCK);
 CHECK(close(fd)==0);errno=0;CHECK(fcntl(fd,F_SETLK,&lock)==-1&&errno==EBADF);
 CHECK(close(channel[0])==0&&close(channel[1])==0);CHECK(unlink(path)==0);
 puts("real POSIX file locks: 64-bit range and owner query, contention, blocking handoff, close release, EFAULT and EBADF PASS");return 0;
}
