#include <stdio.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    char *nome = (argc > 1) ? argv[1] : "Processo";
    int contador = 0;
    
    while(1) {
        printf("%s executando... contador: %d\n", nome, ++contador);
        usleep(100000);
    }
    
    return 0;
}