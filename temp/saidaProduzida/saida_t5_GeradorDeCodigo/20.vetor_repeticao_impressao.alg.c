#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
	int vetor[5];
	int i;
	for (i = 0; i <= 4; i++) {
	vetor[i] = i+1;
	}
	printf("%d",vetor[0]);
	return 0;
}
