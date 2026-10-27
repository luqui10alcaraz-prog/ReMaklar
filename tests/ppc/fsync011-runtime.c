#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL fsync line=%d errno=%d\n",__LINE__,errno);return 1;}}while(0)
int main(void)
{
 char path[256],data[12];int fd,channel[2];
 sprintf(path,"/var/tmp/jaguar/.fsync011-%d",getpid());
 fd=open(path,O_RDWR|O_CREAT|O_EXCL,0600);CHECK(fd>=0);CHECK(write(fd,"original UFS",12)==12);
 CHECK(fsync(fd)==0);CHECK(lseek(fd,0,SEEK_CUR)==12);CHECK(lseek(fd,0,SEEK_SET)==0);
 CHECK(read(fd,data,12)==12&&!memcmp(data,"original UFS",12));CHECK(close(fd)==0);
 fd=open(path,O_RDONLY);CHECK(fd>=0);CHECK(fsync(fd)==0);CHECK(close(fd)==0);
 errno=0;CHECK(fsync(fd)==-1&&errno==EBADF);CHECK(pipe(channel)==0);
 errno=0;CHECK(fsync(channel[0])==-1&&errno==EINVAL);
 CHECK(close(channel[0])==0&&close(channel[1])==0);CHECK(unlink(path)==0);
 puts("real fsync: data and read-only descriptors, offset and bytes preserved, EBADF and pipe EINVAL PASS");return 0;
}
