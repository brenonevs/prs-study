#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <stdlib.h>

void signal_handler(int sig) {
    if (sig == SIGINT) {
        printf("\nRecebido SIGINT (Ctrl-C). Continuando execução...\n");
    } else if (sig == SIGQUIT) {
        printf("\nRecebido SIGQUIT (Ctrl-\\). Terminando programa.\n");
        exit(0);
    }
}

int main() {
    signal(SIGINT, signal_handler);
    signal(SIGQUIT, signal_handler);
    
    printf("Programa rodando. Pressione Ctrl-C ou Ctrl-\\ para testar.\n");
    printf("Pressione Ctrl-\\ para sair.\n");
    
    while(1) {
        sleep(1);
        printf("Programa ativo...\n");
    }
    
    return 0;
}