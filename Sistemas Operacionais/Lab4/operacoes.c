#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
#include <fenv.h>

int erro_divisao = 0;

void sigfpe_handler(int sig) {
    printf("Erro: Divisão por zero detectada (SIGFPE)!\n");
    erro_divisao = 1;
}

void operacoes_reais() {
    float a, b;
    
    printf("\n=== OPERAÇÕES COM NÚMEROS REAIS ===\n");
    printf("Digite dois números reais: ");
    scanf("%f %f", &a, &b);
    
    printf("%.2f + %.2f = %.2f\n", a, b, a + b);
    printf("%.2f - %.2f = %.2f\n", a, b, a - b);
    printf("%.2f * %.2f = %.2f\n", a, b, a * b);
    
    erro_divisao = 0;
    if (b != 0) {
        printf("%.2f / %.2f = %.2f\n", a, b, a / b);
    } else {
        printf("%.2f / %.2f = ", a, b);
        float result = a / b;
        if (!erro_divisao) {
            printf("%.2f (infinito)\n", result);
        }
    }
}

void operacoes_inteiras() {
    int a, b;
    
    printf("\n=== OPERAÇÕES COM NÚMEROS INTEIROS ===\n");
    printf("Digite dois números inteiros: ");
    scanf("%d %d", &a, &b);
    
    printf("%d + %d = %d\n", a, b, a + b);
    printf("%d - %d = %d\n", a, b, a - b);
    printf("%d * %d = %d\n", a, b, a * b);
    
    erro_divisao = 0;
    if (b != 0) {
        printf("%d / %d = %d\n", a, b, a / b);
    } else {
        printf("Erro: Divisão de inteiro por zero não é permitida!\n");
    }
}

int main() {
    signal(SIGFPE, sigfpe_handler);
    
    operacoes_reais();
    operacoes_inteiras();
    
    return 0;
}