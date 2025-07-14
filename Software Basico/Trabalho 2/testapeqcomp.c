/* Diogo Adario Marassi 2220354 3WB */
#include <stdio.h>
#include <stdlib.h>
#include "peqcomp.h"

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Uso: %s <arquivo.sbas> [param1 param2 param3]\n", argv[0]);
        return 1;
    }

    FILE *fp = fopen(argv[1], "r");
    if (!fp) {
        perror("Erro ao abrir arquivo .sbas");
        return 1;
    }

    unsigned char codigo[1024]; // buffer para código gerado
    funcp funcao = peqcomp(fp, codigo);
    fclose(fp);

    // Lê até 3 argumentos inteiros opcionais
    int p1 = argc > 2 ? atoi(argv[2]) : 0;
    int p2 = argc > 3 ? atoi(argv[3]) : 0;
    int p3 = argc > 4 ? atoi(argv[4]) : 0;

    // Executa função com os parâmetros
    int resultado = funcao(p1, p2, p3);
    printf("Resultado da função gerada: %d\n", resultado);

    return 0;
}
