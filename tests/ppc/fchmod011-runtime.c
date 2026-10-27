#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL fchmod line=%d errno=%d\n",__LINE__,errno);return 1;}}while(0)
int main(void)
{
 char path[256],data[4];int fd;struct stat st;
 sprintf(path,"/var/tmp/jaguar/.fchmod011-%d",getpid());
 fd=open(path,O_RDWR|O_CREAT|O_EXCL,0600);CHECK(fd>=0);CHECK(write(fd,"mode",4)==4);
 CHECK(fchmod(fd,0660)==0);CHECK(fstat(fd,&st)==0&&(st.st_mode&07777)==0660);
 CHECK(fchmod(fd,0400)==0);CHECK(stat(path,&st)==0&&(st.st_mode&07777)==0400&&st.st_size==4);
 CHECK(lseek(fd,0,SEEK_SET)==0);CHECK(read(fd,data,4)==4&&!memcmp(data,"mode",4));CHECK(close(fd)==0);
 errno=0;CHECK(fchmod(fd,0600)==-1&&errno==EBADF);CHECK(unlink(path)==0);
 puts("real fchmod: inode modes 0660/0400, file bytes unchanged and closed descriptor EBADF PASS");return 0;
}
