/* SPDX-License-Identifier: MIT */
#include <stdio.h>
static int ready;
static void initialize(void) __attribute__((constructor));
static void initialize(void) { ready = 40; puts("DYLIB initializer"); }
int remaklar_value(void) { return ready + 2; }
