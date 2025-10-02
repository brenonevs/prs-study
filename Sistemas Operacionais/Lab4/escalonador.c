#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>
#include <time.h>

pid_t filho1, filho2;
int processo_ativo = 1;

void criar_filhos() {
    if ((filho1 = fork()) == 0) {
        execvp("./infinite_loop", (char*[]){"infinite_loop", "Filho1", NULL});
        perror("execvp filho1 failed");
        exit(1);
    }
    
    if ((filho2 = fork()) == 0) {
        execvp("./infinite_loop", (char*[]){"infinite_loop", "Filho2", NULL});
        perror("execvp filho2 failed");
        exit(1);
    }
    
    printf("Pai: Filhos criados - PID1: %d, PID2: %d\n", filho1, filho2);
}

void escalonador_preemptivo() {
    time_t inicio = time(NULL);
    
    kill(filho2, SIGSTOP);
    printf("Pai: Executando Filho1\n");
    
    while (time(NULL) - inicio < 15) {
        sleep(1);
        
        if (processo_ativo == 1) {
            kill(filho1, SIGSTOP);
            kill(filho2, SIGCONT);
            processo_ativo = 2;
            printf("Pai: Preempção - Pausando Filho1, Executando Filho2\n");
        } else {
            kill(filho2, SIGSTOP);
            kill(filho1, SIGCONT);
            processo_ativo = 1;
            printf("Pai: Preempção - Pausando Filho2, Executando Filho1\n");
        }
    }
}

void terminar_filhos() {
    printf("Pai: Terminando execução após 15 segundos\n");
    printf("Pai: Matando processos filhos\n");
    
    kill(filho1, SIGKILL);
    kill(filho2, SIGKILL);
    
    wait(NULL);
    wait(NULL);
    
    printf("Pai: Todos os processos terminados. Fim.\n");
}

int main() {
    printf("=== ESCALONADOR PREEMPTIVO ===\n");
    printf("Criando dois processos filhos com loop infinito\n");
    printf("Execução por 15 segundos com preempção a cada 1 segundo\n\n");
    
    criar_filhos();
    escalonador_preemptivo();
    terminar_filhos();
    
    return 0;
}