#include <sys/types.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL utimes line=%d errno=%d\n",__LINE__,errno);return 1;}}while(0)
int main(void)
{
 char path[256],missing[280];int fd;struct stat st;struct timeval tv[2],before,after;
 sprintf(path,"/var/tmp/jaguar/.utimes011-%d",getpid());sprintf(missing,"%s-missing",path);
 fd=open(path,O_WRONLY|O_CREAT|O_EXCL,0600);CHECK(fd>=0);CHECK(close(fd)==0);
 tv[0].tv_sec=1234567001;tv[0].tv_usec=432101;
 tv[1].tv_sec=1234567890;tv[1].tv_usec=123456;
 CHECK(utimes(path,tv)==0);CHECK(stat(path,&st)==0);
 CHECK(st.st_atime==tv[0].tv_sec&&st.st_mtime==tv[1].tv_sec);
 printf("stored nanoseconds: atime=%ld mtime=%ld\n",st.st_atimespec.tv_nsec,st.st_mtimespec.tv_nsec);
 errno=0;CHECK(utimes(missing,tv)==-1&&errno==ENOENT);
 errno=0;CHECK(utimes(path,(const struct timeval *)1)==-1&&errno==EFAULT);
 CHECK(gettimeofday(&before,0)==0);CHECK(utimes(path,0)==0);CHECK(gettimeofday(&after,0)==0);
 CHECK(stat(path,&st)==0);CHECK(st.st_atime>=before.tv_sec&&st.st_atime<=after.tv_sec);
 CHECK(st.st_mtime>=before.tv_sec&&st.st_mtime<=after.tv_sec);CHECK(unlink(path)==0);
 puts("real utimes: two timeval records, native precision, NULL current time, ENOENT and EFAULT PASS");return 0;
}
