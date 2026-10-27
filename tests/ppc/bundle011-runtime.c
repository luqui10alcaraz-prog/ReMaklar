/* Darwin 6's shipped CF header set is incomplete. These declarations follow
 * the original 32-bit CoreFoundation ABI; the original framework is linked. */
typedef const void *CFStringRef;
typedef const void *CFURLRef;
typedef const void *CFBundleRef;
typedef const void *CFDictionaryRef;
extern CFStringRef __CFStringMakeConstantString(const char *);
#define CFSTR(s) __CFStringMakeConstantString(s)
#define kCFStringEncodingUTF8 0x08000100
#define kCFURLPOSIXPathStyle 0
extern CFStringRef CFStringCreateWithCString(const void *,const char *,unsigned);
extern unsigned char CFStringGetCString(CFStringRef,char *,long,unsigned);
extern CFURLRef CFURLCreateWithFileSystemPath(const void *,CFStringRef,int,unsigned char);
extern CFStringRef CFURLCopyFileSystemPath(CFURLRef,int);
extern CFBundleRef CFBundleCreate(const void *,CFURLRef);
extern CFDictionaryRef CFBundleGetInfoDictionary(CFBundleRef);
extern const void *CFDictionaryGetValue(CFDictionaryRef,const void *);
extern CFURLRef CFBundleCopyResourceURL(CFBundleRef,CFStringRef,CFStringRef,CFStringRef);
extern CFURLRef CFBundleCopyResourceURLForLocalization(CFBundleRef,CFStringRef,CFStringRef,CFStringRef,CFStringRef);
extern void CFRelease(const void *);
#include <stdio.h>
#include <string.h>
static void show(const char *label,CFStringRef value)
{
 char text[4096];if(!value){printf("%s=NULL\n",label);return;}
 if(!CFStringGetCString(value,text,sizeof(text),kCFStringEncodingUTF8)){printf("%s=conversion-failed\n",label);return;}
 printf("%s=%s\n",label,text);
}
static int resource(CFBundleRef bundle,const char *label,CFStringRef name,CFStringRef ext,CFStringRef language)
{
 CFURLRef url=language?CFBundleCopyResourceURLForLocalization(bundle,name,ext,0,language):CFBundleCopyResourceURL(bundle,name,ext,0);CFStringRef path;
 if(!url){printf("%s=NULL\n",label);return 1;}
 path=CFURLCopyFileSystemPath(url,kCFURLPOSIXPathStyle);show(label,path);CFRelease(path);CFRelease(url);return 0;
}
int main(int argc,char **argv)
{
 CFStringRef path;CFURLRef url;CFBundleRef bundle;CFDictionaryRef info;int failed=0;
 if(argc!=2)return 2;
 path=CFStringCreateWithCString(0,argv[1],kCFStringEncodingUTF8);url=CFURLCreateWithFileSystemPath(0,path,kCFURLPOSIXPathStyle,1);bundle=CFBundleCreate(0,url);
 if(!bundle){puts("bundle=NULL");return 3;}
 info=CFBundleGetInfoDictionary(bundle);show("NSPrincipalClass",CFDictionaryGetValue(info,CFSTR("NSPrincipalClass")));show("NSMainNibFile",CFDictionaryGetValue(info,CFSTR("NSMainNibFile")));
 failed+=resource(bundle,"split-name",CFSTR("PagedInstaller"),CFSTR("nib"),0);
 failed+=resource(bundle,"full-name",CFSTR("PagedInstaller.nib"),0,0);
 failed+=resource(bundle,"English",CFSTR("PagedInstaller"),CFSTR("nib"),CFSTR("English"));
 CFRelease(bundle);CFRelease(url);CFRelease(path);return failed?1:0;
}
