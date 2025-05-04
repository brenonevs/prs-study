
# Tutorial: Como Iniciar o Desenvolvimento de um Código em Assembly (x86-64)

Este tutorial detalha passo a passo como iniciar e estruturar um programa simples em Assembly para arquitetura x86-64, com base em dois exemplos que replicam comportamentos da linguagem C.

---

## 1. Introdução

Assembly é uma linguagem de baixo nível que interage diretamente com a arquitetura da CPU. Por isso, é comum usarmos convenções de chamada de sistema e organizações de pilha definidas por convenções como a **System V AMD64 ABI** (em sistemas Unix/Linux de 64 bits).

---

## 2. Estrutura Básica de um Programa Assembly

Um programa Assembly é dividido em três seções principais:

### 2.1. Seção `.data`

Armazena variáveis estáticas e strings constantes:

```asm
.data
S2:    .byte 65, 108, 111, 32, 123, 103, 97, 108, 101, 114, 97, 125, 33, 0
Sf:    .string "%c"
Sf2:   .string "\n"
```

### 2.2. Seção `.text`

Contém o código executável. É onde implementamos a função `main`.

```asm
.text
.globl main
main:
```

---

## 3. Prólogo da Função `main`

Este trecho prepara a pilha para a execução segura da função:

```asm
pushq %rbp
movq %rsp, %rbp
subq $16, %rsp
movq %rbx, -8(%rbp)   ; salva rbx
movq %r12, -16(%rbp)  ; salva r12
```

---

## 4. Inicialização de Ponteiro

A variável `pc`, que aponta para o início da string `S2`, é representada em Assembly com um registrador:

```asm
movq $S2, %r12
```

Usamos `%r12` para armazenar esse ponteiro.

---

## 5. Loop Principal

O loop percorre cada caractere da string até encontrar `\0`:

```asm
L1:
  cmpb $0, (%r12)
  je L2
```

Esse trecho verifica se o caractere atual é nulo (`\0`) para encerrar o loop.

### 5.1. Ignorando chaves (`{` e `}`)

No C, fazemos:

```c
if ((*pc != 123) && (*pc !=125)) {
```

Em Assembly:

```asm
cmpb $123, (%r12)
je L3
cmpb $125, (%r12)
je L3
```

### 5.2. Impressão de Caracteres

Caso não seja uma chave, imprime-se o caractere com `printf("%c", *pc)`:

```asm
movsbl (%r12), %eax      ; carrega caractere e extende
movq $Sf, %rdi           ; 1º parâmetro: string de formato
movl %eax, %esi          ; 2º parâmetro: caractere
movl $0, %eax
call printf
```

### 5.3. Avança ponteiro

```asm
addq $1, %r12
jmp L1
```

### 5.4. Label de Skip

Se o caractere era uma chave, também incrementa o ponteiro:

```asm
L3:
  addq $1, %r12
  jmp L1
```

---

## 6. Impressão de Nova Linha

Ao final do loop:

```asm
L2:
movq $Sf2, %rdi
movl $0, %eax
call printf
```

---

## 7. Epílogo da Função `main`

Restaura os registradores e retorna:

```asm
movq $0, %rax            ; valor de retorno
movq -16(%rbp), %r12     ; recupera r12
movq -8(%rbp), %rbx      ; recupera rbx
leave
ret
```

---

## 8. Compilando o Programa

Salve o arquivo como `program.s` e compile usando:

```bash
gcc -no-pie -o program program.s
```

- O flag `-no-pie` evita que o programa seja compilado com endereçamento relativo (Position Independent Executable).
    

Execute com:

```bash
./program
```

---

## 9. Comparando os Dois Códigos

- **Código 1** filtra os caracteres `{` e `}`.
    
- **Código 2** imprime todos os caracteres da string.
    
- Ambos usam o mesmo padrão de prólogo, uso de `printf`, e epílogo.
    

---

## 10. Conclusão

Este tutorial demonstrou como traduzir lógica C simples para Assembly, usando manipulação de ponteiros, uso de `printf`, e controle de fluxo com `jmp`, `cmp` e `je`. É essencial seguir a convenção de chamada e gerenciar a pilha corretamente para garantir execução segura e previsível.

---

## Apêndice: Registradores Relevantes

| Registrador | Uso Típico               |
| ----------- | ------------------------ |
| `%rdi`      | 1º argumento para função |
| `%rsi`      | 2º argumento para função |
| `%rax`      | valor de retorno         |
| `%rbp`      | base da pilha            |
| `%rsp`      | topo da pilha            |
| `%r         |                          |