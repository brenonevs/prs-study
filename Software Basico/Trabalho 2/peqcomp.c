/* Diogo Adario Marassi 2220354 3WB */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "peqcomp.h"

#define OFFSET_VAR(i) (-4 * (i))  // v1 → -4, v2 → -8, etc.
#define MAX_LINHAS 30
#define MAX_TAMANHO_LINHA 128

typedef struct {
    int linha_sbas;
    int posicao_codigo;
} LinhaMapa;

typedef struct {
    int pos_jle_offset;
    int linha_destino;
} SaltoPendente;

static int32_t var_offset(int idx) {
    if (idx < 1 || idx > 5) {
        fprintf(stderr, "Índice inválido v%d\n", idx);
        exit(1);
    }
    return OFFSET_VAR(idx);
}

funcp peqcomp(FILE *f, unsigned char codigo[]) {
    char linhas[MAX_LINHAS][MAX_TAMANHO_LINHA];
    LinhaMapa mapa_linhas[MAX_LINHAS];
    SaltoPendente saltos[MAX_LINHAS];
    int total_linhas = 0, total_saltos = 0;
    int pos = 0;

    // Leitura das linhas do arquivo
    while (fgets(linhas[total_linhas], MAX_TAMANHO_LINHA, f) != NULL) {
        if (strlen(linhas[total_linhas]) > 1)
            total_linhas++;
        if (total_linhas >= MAX_LINHAS)
            break;
    }

    // Prólogo
    codigo[pos++] = 0x55;
    codigo[pos++] = 0x48; codigo[pos++] = 0x89; codigo[pos++] = 0xe5;
    codigo[pos++] = 0x48; codigo[pos++] = 0x83; codigo[pos++] = 0xec;
    codigo[pos++] = 32;

    // Segunda passagem: geração de código
    for (int i = 0; i < total_linhas; i++) {
        mapa_linhas[i].linha_sbas = i + 1;
        mapa_linhas[i].posicao_codigo = pos;

        char *linha = linhas[i];
        int v1, v2, v3, c;
        char op;

        // ret $const
        if (sscanf(linha, "ret $%d", &c) == 1) {
            codigo[pos++] = 0xb8;
            *(int32_t *)(codigo + pos) = c;
            pos += 4;
            codigo[pos++] = 0xc9;
            codigo[pos++] = 0xc3;
            continue;
        }

        // ret vX
        if (sscanf(linha, "ret v%d", &v1) == 1) {
            codigo[pos++] = 0x8b; codigo[pos++] = 0x45;
            codigo[pos++] = (unsigned char)var_offset(v1);
            codigo[pos++] = 0xc9;
            codigo[pos++] = 0xc3;
            continue;
        }

        // vX : $const
        if (sscanf(linha, "v%d : $%d", &v1, &c) == 2) {
            codigo[pos++] = 0xc7;
            codigo[pos++] = 0x45;
            codigo[pos++] = (unsigned char)var_offset(v1);
            *(int32_t *)(codigo + pos) = c;
            pos += 4;
            continue;
        }

        // vX : pY
        if (sscanf(linha, "v%d : p%d", &v1, &v2) == 2) {
            switch (v2) {
                case 1: codigo[pos++] = 0x89; codigo[pos++] = 0xf8; break; // eax ← edi
                case 2: codigo[pos++] = 0x89; codigo[pos++] = 0xf0; break; // eax ← esi
                case 3: codigo[pos++] = 0x89; codigo[pos++] = 0xd0; break; // eax ← edx
                default: exit(1);
            }
            codigo[pos++] = 0x89; codigo[pos++] = 0x45;
            codigo[pos++] = (unsigned char)var_offset(v1);
            continue;
        }

        // vX : vY
        if (sscanf(linha, "v%d : v%d", &v1, &v2) == 2) {
            codigo[pos++] = 0x8b; codigo[pos++] = 0x45;
            codigo[pos++] = (unsigned char)var_offset(v2);
            codigo[pos++] = 0x89; codigo[pos++] = 0x45;
            codigo[pos++] = (unsigned char)var_offset(v1);
            continue;
        }

        // vX = vY op vZ
        if (sscanf(linha, "v%d = v%d %c v%d", &v1, &v2, &op, &v3) == 4) {
            codigo[pos++] = 0x8b; codigo[pos++] = 0x45;
            codigo[pos++] = (unsigned char)var_offset(v2);
            if (op == '+') codigo[pos++] = 0x03;
            else if (op == '-') codigo[pos++] = 0x2b;
            else if (op == '*') { codigo[pos++] = 0x0f; codigo[pos++] = 0xaf; }
            else exit(1);
            codigo[pos++] = 0x45;
            codigo[pos++] = (unsigned char)var_offset(v3);
            codigo[pos++] = 0x89; codigo[pos++] = 0x45;
            codigo[pos++] = (unsigned char)var_offset(v1);
            continue;
        }

        // vX = vY op $const
        if (sscanf(linha, "v%d = v%d %c $%d", &v1, &v2, &op, &c) == 4) {
            codigo[pos++] = 0x8b; codigo[pos++] = 0x45;
            codigo[pos++] = (unsigned char)var_offset(v2);

            if (op == '+') {
                codigo[pos++] = 0x05;
                *(int32_t *)(codigo + pos) = c;
                pos += 4;
            } else if (op == '-') {
                codigo[pos++] = 0x2d;
                *(int32_t *)(codigo + pos) = c;
                pos += 4;
            } else if (op == '*') {
                codigo[pos++] = 0x69; codigo[pos++] = 0xc0;
                *(int32_t *)(codigo + pos) = c;
                pos += 4;
            } else exit(1);

            codigo[pos++] = 0x89; codigo[pos++] = 0x45;
            codigo[pos++] = (unsigned char)var_offset(v1);
            continue;
        }

        // vX = $const op vY
        if (sscanf(linha, "v%d = $%d %c v%d", &v1, &c, &op, &v2) == 4) {
            codigo[pos++] = 0xb8;
            *(int32_t *)(codigo + pos) = c;
            pos += 4;

            if (op == '+') {
                codigo[pos++] = 0x03;
                codigo[pos++] = 0x45;
                codigo[pos++] = (unsigned char)var_offset(v2);
            } else if (op == '-') {
                codigo[pos++] = 0x2b;
                codigo[pos++] = 0x45;
                codigo[pos++] = (unsigned char)var_offset(v2);
            } else if (op == '*') {
                codigo[pos++] = 0x0f; codigo[pos++] = 0xaf;
                codigo[pos++] = 0x45;
                codigo[pos++] = (unsigned char)var_offset(v2);
            } else exit(1);

            codigo[pos++] = 0x89; codigo[pos++] = 0x45;
            codigo[pos++] = (unsigned char)var_offset(v1);
            continue;
        }

        // iflez vX N
        if (sscanf(linha, "iflez v%d %d", &v1, &c) == 2) {
            codigo[pos++] = 0x8b; codigo[pos++] = 0x45;
            codigo[pos++] = (unsigned char)var_offset(v1);
            codigo[pos++] = 0x83; codigo[pos++] = 0xf8; codigo[pos++] = 0x00;
            codigo[pos++] = 0x0f; codigo[pos++] = 0x8e;
            int pos_offset = pos;
            *(int32_t *)(codigo + pos) = 0; // será ajustado depois
            pos += 4;

            saltos[total_saltos++] = (SaltoPendente){ pos_offset, c };
            continue;
        }

        fprintf(stderr, "Erro na linha %d: %s\n", i + 1, linha);
        exit(1);
    }

    // Corrige todos os offsets de salto dos iflez
    for (int i = 0; i < total_saltos; i++) {
        int destino = saltos[i].linha_destino;
        int pos_destino = -1;
        for (int j = 0; j < total_linhas; j++) {
            if (mapa_linhas[j].linha_sbas == destino) {
                pos_destino = mapa_linhas[j].posicao_codigo;
                break;
            }
        }
        if (pos_destino == -1) {
            fprintf(stderr, "Destino de salto inválido: linha %d\n", destino);
            exit(1);
        }

        int desloc = pos_destino - (saltos[i].pos_jle_offset + 4);
        *(int32_t *)(codigo + saltos[i].pos_jle_offset) = desloc;
    }

    return (funcp)codigo;
}

