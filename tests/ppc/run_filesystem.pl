#!/usr/bin/perl
# Controlled host setup, original ls/pwd, own PPC filesystem syscall probe.
# SPDX-License-Identifier: MIT
use strict;
my ($exe, $root, $probe, $out) = @ARGV;
die "usage: executor guest-root filesystem-probe output\n" unless defined $out;
mkdir $out unless -d $out;
mkdir "$root/fixtures/fs-work",0700 unless -d "$root/fixtures/fs-work";
my $list="$root/fixtures/fs-list";
mkdir $list,0750 unless -d $list;
mkdir "$list/directory",0750 unless -d "$list/directory";
for my $name ('alpha','beta','.hidden') {
    open F,'>',"$list/$name" or die $!; print F "abc\n"; close F;
    chmod 0640,"$list/$name" or die $!; utime 978307200,978307200,"$list/$name";
}
symlink 'alpha',"$list/link" or die $! unless -l "$list/link";
my $many="$root/fixtures/fs-many";
mkdir $many,0700 unless -d $many;
for my $i (0..299) { open F,'>',sprintf("$many/item%03d",$i) or die $!; close F; }
my ($count,$failed)=(0,0);
open RESULTS,'>',"$out/results.txt" or die $!;
sub slurp { open F,'<',$_[0] or die $!; binmode F; local $/; my $s=<F>;close F;return defined $s?$s:''; }
sub run {
    my ($id,$program,$cwd,$expected_status,$expected,@args)=@_;
    my @cmd=$program eq 'probe' ? ($exe,'--root',$root,$probe) : ($exe,'--root',$root,'--cwd',$cwd,"$root/bin/$program",@args);
    my $pid=fork();die $! unless defined $pid;
    if (!$pid) {
        open STDIN,'<','/dev/null' or die $!;
        open STDOUT,'>',"$out/$id.stdout" or die $!;
        open STDERR,'>',"$out/$id.stderr" or die $!;
        $ENV{LANG}=$ENV{LC_ALL}='C';$ENV{TZ}='UTC';delete $ENV{REMAKLAR_TRACE};
        exec @cmd;die $!;
    }
    my $timeout=0;local $SIG{ALRM}=sub {$timeout=1;kill 9,$pid;};alarm 120;
    while(waitpid($pid,0)!=$pid){} my $raw=$?;alarm 0;
    my $status=($raw&127)?128+($raw&127):$raw>>8;
    my $stdout=slurp("$out/$id.stdout");my $stderr=slurp("$out/$id.stderr");
    my $output_ok=ref($expected) eq 'Regexp' ? $stdout =~ $expected : $stdout eq $expected;
    my $ok=!$timeout && $status==$expected_status && $output_ok;
    $ok &&= index($stderr,'unsupported')<0 && index($stderr,'unhandled host')<0 && index($stderr,'probe-main:')<0;
    $ok &&= index($stderr,'No such file or directory')>=0 if $id eq 'ls-missing';
    if ($program ne 'probe') {
        my $entry=$program eq 'ls'?'00001950':'00002478';
        my $observations=()=$stderr=~/startup: entered original executable at $entry/g;
        $ok &&= $observations==1 && $stderr =~ / r0=1 /;
        $ok &&= index($stderr,"guest open $root/usr/lib/libSystem.B.dylib")>=0;
    }
    my $line=($ok?'PASS':'FAIL')." $id exit=$status expected=$expected_status bytes=".length($stdout)."\n";
    print $line;print RESULTS $line;$failed++ unless $ok;$count++;
}
run('pwd-root','pwd','/',0,"/\n");
run('pwd-nested','pwd','/fixtures/fs-list/directory',0,"/fixtures/fs-list/directory\n");
run('pwd-parent','pwd','/fixtures/fs-list/directory/..',0,"/fixtures/fs-list\n");
run('ls-names','ls','/',0,".hidden\nalpha\nbeta\ndirectory\nlink\n",'-1A','/fixtures/fs-list');
run('ls-hidden','ls','/',0,".\n..\n.hidden\nalpha\nbeta\ndirectory\nlink\n",'-1a','/fixtures/fs-list');
run('ls-types','ls','/fixtures/fs-list',0,".hidden\nalpha\nbeta\ndirectory/\nlink@\n",'-1AF','.');
run('ls-many','ls','/',0,join('',map {sprintf("item%03d\n",$_)} 0..299),'-1','/fixtures/fs-many');
my @st=stat "$list/alpha";
my $metadata=qr/\A-rw-r-----\s+$st[3]\s+$st[4]\s+$st[5]\s+4\s+Jan\s+1\s+00:00:00\s+2001\s+\/fixtures\/fs-list\/alpha\n\z/;
run('ls-metadata','ls','/',0,$metadata,'-lnT','/fixtures/fs-list/alpha');
my @link=lstat "$list/link";
my $mode='l';my $mask=0400;
for my $character (split //,'rwxrwxrwx') { $mode.=($link[2]&$mask)?$character:'-';$mask>>=1; }
my $link_metadata=qr/\A\Q$mode\E\s+$link[3]\s+$link[4]\s+$link[5]\s+$link[7]\s+.*\/fixtures\/fs-list\/link -> alpha\n\z/;
run('ls-link','ls','/',0,$link_metadata,'-ldn','/fixtures/fs-list/link');
run('ls-missing','ls','/',0,'','-1','/fixtures/fs-list/absent');
run('filesystem-probe','probe','/',0,"filesystem PPC OK\n");
my $left=-e "$root/fixtures/fs-work/created";
print RESULTS "cases=$count failed=$failed leftover=".($left?1:0)."\n";
print "cases=$count failed=$failed leftover=".($left?1:0)."\n";
exit($failed || $left ? 1:0);
