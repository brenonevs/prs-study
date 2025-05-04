# 👀 Introdução ao Assembly x86-64

Assembly é uma linguagem de baixo nível que permite controlar diretamente o processador. Aqui focamos na arquitetura x86-64, comum em computadores modernos com processadores de 64 bits.

---

## 🧰 Registradores em x86-64

|Registrador|Descrição|
|---|---|
|RAX|Acumulador (retorno de função)|
|RBX|Base|
|RCX|Contador (loops)|
|RDX|Dados|
|RSI|Source Index|
|RDI|Destination Index|
|RBP|Base Pointer (stack frame)|
|RSP|Stack Pointer (topo da pilha)|
|RIP|Instruction Pointer|
|R8–R15|Registradores extras|

---

## ⚙️ Instruções Básicas

### Movimentação de dados:

```asm
MOV RAX, 5
MOV RBX, RAX
```

### Aritmética:

```asm
ADD RAX, RBX
SUB RAX, 1
IMUL RBX
IDIV RBX
```

### Comparação e Saltos:

```asm
CMP RAX, RBX
JE igual
JNE diferente
JG maior
JL menor
```

---

## 🧥 Pilha (Stack)

### Instruções:

```asm
PUSH RAX
POP RBX
```

### Estrutura de função:

```asm
funcao:
    PUSH RBP
    MOV RBP, RSP
    ; corpo da função
    MOV RSP, RBP
    POP RBP
    RET
```

---

## 📜 Declaração de Dados

```asm
section .data
mensagem db "Oi, mundo!", 0

section .bss
variavel resb 8
```

---

## 🔁 Exemplo: Loop

### C:

```c
for (int i = 0; i < 5; i++) {
    puts("Oi");
}
```

### Assembly:

```asm
MOV RCX, 5
.loop:
    ; chamada puts omitida
    DEC RCX
    JNZ .loop
```

---

## 🔄 Exemplo de função: C → Assembly

### C:

```c
int soma(int a, int b) {
    return a + b;
}
```

### Assembly:

```asm
soma:
    MOV EAX, EDI
    ADD EAX, ESI
    RET
```

---

## 🔬 Flags

|Flag|Nome|Função|
|---|---|---|
|ZF|Zero Flag|Ativada se o resultado for zero|
|SF|Sign Flag|Ativada se o resultado for negativo|
|CF|Carry Flag|Overflow sem sinal (unsigned)|
|OF|Overflow Flag|Overflow com sinal (signed)|

---

## 🧪 Experimente

```bash
gcc -S -O0 -o fat.s fat.c
```

---

## 💡 Desafio

### C:

```c
int dobro(int x) {
    return x * 2;
}
```

**Argumento:** `EDI`  
**Retorno:** `EAX`