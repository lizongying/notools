#include <dirent.h>
#include <stdio.h>
#include <string.h>

int main() {
    DIR *d = opendir("/Users/lizongying/IdeaProjects/notools/git/tests/tmp-refs-br/.git/refs/heads");
    if (!d) { printf("opendir failed\n"); return 1; }
    struct dirent *e;
    while ((e = readdir(d)) != NULL) {
        printf("entry: '%s' (d_name offset: %ld)\n", e->d_name, (long)((char*)e->d_name - (char*)e));
    }
    closedir(d);
    return 0;
}
