#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <signal.h>

void opcao_a() {
    printf("Filho: Entrando em loop infinito\n");
    while(1) {
    }
}

void opcao_b() {
    printf("Filho: Dormindo por 3 segundos\n");
    sleep(3);
    printf("Filho: Acordei! Terminando.\n");
}

void opcao_c() {
    printf("Filho: Executando programa sleep 5\n");
    execvp("sleep", (char*[]){"sleep", "5", NULL});
    perror("execvp failed");
}

void opcao_d() {
    printf("Filho: Executando programa sleep 15\n");
    execvp("sleep", (char*[]){"sleep", "15", NULL});
    perror("execvp failed");
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Uso: %s <a|b|c|d>\n", argv[0]);
        printf("a - loop infinito\n");
        printf("b - sleep 3 segundos\n");
        printf("c - execvp sleep 5\n");
        printf("d - execvp sleep 15\n");
        return 1;
    }
    
    pid_t pid = fork();
    
    if (pid == 0) {
        switch(argv[1][0]) {
            case 'a': opcao_a(); break;
            case 'b': opcao_b(); break;
            case 'c': opcao_c(); break;
            case 'd': opcao_d(); break;
            default: printf("Opção inválida\n"); exit(1);
        }
        exit(0);
    } else if (pid > 0) {
        printf("Pai: Filho criado com PID %d\n", pid);
        
        sleep(10);
        
        if (kill(pid, 0) == 0) {
            printf("Pai: Filho ainda está vivo. Matando processo...\n");
            kill(pid, SIGKILL);
        } else {
            printf("Pai: Filho já terminou naturalmente.\n");
        }
        
        wait(NULL);
        printf("Pai: Terminando.\n");
    } else {
        perror("fork failed");
        return 1;
    }
    
    return 0;
}