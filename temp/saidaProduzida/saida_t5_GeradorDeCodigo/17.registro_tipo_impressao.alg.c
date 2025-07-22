#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
	char nome[80];
	int idade;
} treg;

int main() {
	treg reg;
	strcpy(reg.nome, "Maria");
	reg.idade = 30;
	printf("%s%s%d%s",reg.nome," tem ",reg.idade," anos");
	return 0;
}
