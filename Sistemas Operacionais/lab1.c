#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    int N = 0;

    pid_t pid_filho = fork(); 

    if (pid_filho < 0) {
        perror("Erro no fork");
        exit(1);
    }

    if (pid_filho == 0) {
        pid_t pid_neto = fork();

        if (pid_neto < 0) {
            perror("Erro no fork do neto");
            exit(1);
        }

        if (pid_neto == 0) {
            for (int i = 0; i < 100; i++) {
                N += 5;
                printf("[NETO] Iteração %d | N = %d | PID = %d | PPID = %d\n", i + 1, N, getpid(), getppid());
                usleep(5000);
            }
            exit(0);
        } else {
            for (int i = 0; i < 100; i++) {
                N += 2;
                printf("[FILHO] Iteração %d | N = %d | PID = %d | PPID = %d\n", i + 1, N, getpid(), getppid());
                usleep(5000);
            }
            waitpid(pid_neto, NULL, 0);
            exit(0);
        }

    } else {
        for (int i = 0; i < 100; i++) {
            N++;
            printf("[PAI] Iteração %d | N = %d | PID = %d | PPID = %d\n", i + 1, N, getpid(), getppid());
            usleep(5000);
        }
        waitpid(pid_filho, NULL, 0);
    }

    return 0;
}
