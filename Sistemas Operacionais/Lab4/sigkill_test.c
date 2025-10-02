#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <stdlib.h>

void sigkill_handler(int sig) {
    printf("Tentativa de capturar SIGKILL - isso nunca será executado!\n");
}

int main() {
    printf("Tentando interceptar SIGKILL...\n");
    
    if (signal(SIGKILL, sigkill_handler) == SIG_ERR) {
        perror("Erro ao tentar interceptar SIGKILL");
        printf("SIGKILL não pode ser interceptado!\n");
    }
    
    printf("PID do processo: %d\n", getpid());
    printf("Execute 'kill -9 %d' em outro terminal para testar.\n", getpid());
    
    while(1) {
        sleep(1);
        printf("Processo ativo...\n");
    }
    
    return 0;
}