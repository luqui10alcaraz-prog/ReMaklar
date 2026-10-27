#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL delete line=%d errno=%d\n",__LINE__,errno);return 1;}}while(0)
int main(void)
{
 char path[256];int fd,r,e;struct stat st;
 sprintf(path,"/var/tmp/jaguar/.delete011-%d",getpid());
 fd=open(path,O_WRONLY|O_CREAT|O_EXCL,0600);CHECK(fd>=0);
 errno=0;r=syscall(226,path);e=errno;printf("open-file delete: result=%d errno=%d\n",r,e);
 CHECK(r==-1&&e==EBUSY);CHECK(stat(path,&st)==0);CHECK(close(fd)==0);
 CHECK(syscall(226,path)==0);errno=0;CHECK(stat(path,&st)==-1&&errno==ENOENT);
 errno=0;CHECK(syscall(226,path)==-1&&errno==ENOENT);
 errno=0;CHECK(syscall(226,(char *)1)==-1&&errno==EFAULT);
 CHECK(mkdir(path,0700)==0);errno=0;CHECK(syscall(226,path)==-1&&errno==EPERM);CHECK(rmdir(path)==0);
 puts("real Carbon delete: busy file, closed file, ENOENT, EFAULT and directory EPERM PASS");return 0;
}
