#!/usr/bin/perl
# Cross-build with the original GCC2 and original Jaguar dylibs, no runtime stubs.
# SPDX-License-Identifier: MIT
use strict;
my ($root,$out)=@ARGV;
die 'usage: jaguar-root output-directory' unless $out;
open MAP,'<',"$root/remaklar-link-map.tsv" or die $!;
my @overrides;
while (<MAP>) { chomp;my ($install,$relative)=split /\t/;push @overrides,"-Wl,-dylib_file,$install:$root$relative"; }
my @base=('gcc2','-no-cpp-precomp','-arch','ppc',"-F$root/System/Library/Frameworks",
 "-F$root/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks");
for my $item (['quartz','tests/ppc/quartz-bitmap.c','CoreGraphics'],['foundation','tests/ppc/foundation-smoke.m','Foundation']) {
    my ($name,$source,$framework)=@$item;
    my $pid=fork();die $! unless defined $pid;
    if (!$pid) {
        open STDOUT,'>',"$out/$name-build.txt" or die $!;open STDERR,'>&STDOUT' or die $!;
        exec @base,@overrides,$source,'-o',"build/$name-ppc",'-framework',$framework;
        die $!;
    }
    waitpid($pid,0);my $status=$?>>8;
    open LOG,'>>',"$out/$name-build.txt" or die $!;print LOG "compiler_status=$status\n";close LOG;
}
