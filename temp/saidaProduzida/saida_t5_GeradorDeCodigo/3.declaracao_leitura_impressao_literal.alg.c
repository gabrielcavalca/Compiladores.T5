#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
	char x[80];
	fgets(x, 80, stdin);
	x[strcspn(x, "\n")] = '\0';
	printf("%s",x);
	return 0;
}
