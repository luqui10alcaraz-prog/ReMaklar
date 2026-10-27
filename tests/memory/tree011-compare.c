/* Verify a native filesystem copy without following absolute Jaguar symlinks. */
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned files,links,dirs,repairs;static double bytes;static int repair;
static void fail(const char *s){perror(s);exit(1);}
static void compare(const char *a,const char *b)
{
 struct stat x,y;char p[8192],q[8192];DIR *d;struct dirent *e;
 if(lstat(a,&x)||lstat(b,&y))fail(a);
 if((x.st_mode&0170000)!=(y.st_mode&0170000)){fprintf(stderr,"type mismatch %s\n",a);exit(1);}
 if((x.st_mode&07777)!=(y.st_mode&07777)){
  if(!repair||S_ISLNK(x.st_mode)||chmod(b,x.st_mode&07777)){fprintf(stderr,"mode mismatch %s %o %o\n",a,x.st_mode,y.st_mode);exit(1);}
  printf("restored mode %s %o -> %o\n",b,y.st_mode,x.st_mode);repairs++;
 }
 if(S_ISDIR(x.st_mode)){
  dirs++;d=opendir(a);if(!d)fail(a);
  while((e=readdir(d))){if(!strcmp(e->d_name,".")||!strcmp(e->d_name,".."))continue;
   if(snprintf(p,sizeof(p),"%s/%s",a,e->d_name)>=sizeof(p)||snprintf(q,sizeof(q),"%s/%s",b,e->d_name)>=sizeof(q))exit(2);
   compare(p,q);
  }closedir(d);
 }else if(S_ISLNK(x.st_mode)){
  int n=readlink(a,p,sizeof(p)),m=readlink(b,q,sizeof(q));if(n<0||m<0||n!=m||memcmp(p,q,n)){fprintf(stderr,"symlink mismatch %s\n",a);exit(1);}links++;
 }else if(S_ISREG(x.st_mode)){
  FILE *f,*g;size_t n,m;if(x.st_size!=y.st_size){fprintf(stderr,"size mismatch %s\n",a);exit(1);}
  f=fopen(a,"rb");g=fopen(b,"rb");if(!f||!g)fail(a);
  do{n=fread(p,1,sizeof(p),f);m=fread(q,1,sizeof(q),g);if(n!=m||memcmp(p,q,n)){fprintf(stderr,"byte mismatch %s\n",a);exit(1);}bytes+=n;}while(n);
  if(ferror(f)||ferror(g))fail(a);fclose(f);fclose(g);files++;
  if(!(files%1000)){printf("verified files=%u bytes=%.0f\n",files,bytes);fflush(stdout);}
 }else if(x.st_rdev!=y.st_rdev){fprintf(stderr,"device mismatch %s\n",a);exit(1);}
}
int main(int argc,char **argv){if(argc!=3&&argc!=4)return 2;if(argc==4){if(strcmp(argv[3],"--repair-modes"))return 2;repair=1;}compare(argv[1],argv[2]);printf("COPY_VERIFIED files=%u links=%u dirs=%u bytes=%.0f restored_modes=%u\n",files,links,dirs,bytes,repairs);return 0;}
