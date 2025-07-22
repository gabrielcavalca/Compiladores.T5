#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define teste 8

int main() {
	switch (8) {
		case 0:
		case 1:
		case 2:
		case 3:
		case 4:
		case 5:
		case 6:
		case 7:
		printf("%s","ERRO");
			break;
		case 8:
		printf("%s","OK");
			break;
		default:
		printf("%s","ERRO");
			break;
	}
	return 0;
}
