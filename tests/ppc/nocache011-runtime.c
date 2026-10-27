#include <sys/types.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL nocache line=%d errno=%d\n",__LINE__,errno);return 1;}}while(0)
int main(void)
{
 char path[256],data[6];int fd,channel[2];
 sprintf(path,"/var/tmp/jaguar/.nocache011-%d",getpid());
 fd=open(path,O_RDWR|O_CREAT|O_EXCL,0600);CHECK(fd>=0);
 CHECK(fcntl(fd,F_NOCACHE,1)==0);CHECK(write(fd,"ATS",3)==3);
 CHECK(fcntl(fd,F_NOCACHE,0)==0);CHECK(write(fd,"UFS",3)==3);
 CHECK(lseek(fd,0,SEEK_SET)==0);CHECK(read(fd,data,6)==6&&!memcmp(data,"ATSUFS",6));
 CHECK(fcntl(fd,F_NOCACHE,2)==0);CHECK(fcntl(fd,F_NOCACHE,0)==0);CHECK(close(fd)==0);
 errno=0;CHECK(fcntl(fd,F_NOCACHE,1)==-1&&errno==EBADF);CHECK(pipe(channel)==0);
 errno=0;CHECK(fcntl(channel[0],F_NOCACHE,1)==-1&&errno==EBADF);
 CHECK(close(channel[0])==0&&close(channel[1])==0);CHECK(unlink(path)==0);
 puts("real F_NOCACHE: enable disable nonzero-argument file I/O and closed/pipe EBADF PASS");return 0;
}
