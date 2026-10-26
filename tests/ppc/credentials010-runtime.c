/* Real per-process credentials; no user databases are changed. SPDX-License-Identifier: MIT */
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
int main(void) {
 char name[80];int fd,status;pid_t pid;
 if(getuid() || geteuid())return 1;
 sprintf(name,"/tmp/uid010-%ld",(long)getpid());fd=open(name,O_CREAT|O_EXCL|O_RDWR,0600);if(fd<0)return 2;close(fd);
 pid=fork();if(pid<0)return 3;
 if(!pid){if(seteuid(1) || geteuid()!=1 || getuid()!=0)_exit(4);errno=0;fd=open(name,O_RDONLY);if(fd>=0 || errno!=EACCES)_exit(5);if(seteuid(0) || geteuid()!=0)_exit(6);_exit(0);}
 if(waitpid(pid,&status,0)!=pid || !WIFEXITED(status) || WEXITSTATUS(status) || unlink(name))return 7;
 puts("native seteuid effective access checks restore real credentials OK");return 0;
}
