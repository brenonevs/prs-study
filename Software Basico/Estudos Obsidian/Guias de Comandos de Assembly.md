
# Guia Completo de Comandos Fundamentais em Assembly x86-64

Este documento apresenta uma explicação clara e detalhada sobre os principais comandos utilizados na linguagem Assembly para a arquitetura x86-64, com foco nas instruções mais recorrentes: `mov`, `cmp`, `push`, `call` e suas variações. O conteúdo está organizado por instrução, com descrições de funcionamento, casos de uso típicos e observações importantes para quem está aprendendo ou revisando os fundamentos da linguagem de máquina.

---

## 1. `mov` — Transferência de Dados

### Função:

Move dados de uma origem para um destino.

### Sintaxe Geral:

```asm
mov[tamanho] origem, destino
```

### Sufixos de tamanho:

|Sufixo|Tamanho|Significado|
|---|---|---|
|`b`|8 bits|Byte|
|`w`|16 bits|Word|
|`l`|32 bits|Long|
|`q`|64 bits|Quadword|

### Tipos e variações:

- `movb` → Move 8 bits
    
- `movw` → Move 16 bits
    
- `movl` → Move 32 bits
    
- `movq` → Move 64 bits
    
- `movsbl`, `movzbl`, `movsbq`, `movzbq`, etc → Movimento com extensão de sinal ou zero (ver seção 5)
    

### Exemplos:

```asm
movb $0x41, %al     ; move 8 bits para AL
movl $10, %eax       ; move 32 bits para EAX
movq %rax, %rbx      ; move 64 bits entre registradores
movw $0x1234, %bx    ; move 16 bits para BX
```

### Observações:

- Ao escrever em `%eax`, os 32 bits superiores de `%rax` são automaticamente zerados.
    
- Pode-se mover entre registradores, da memória para registrador, e vice-versa.
    
- A instrução `lea` (Load Effective Address) é uma variação que carrega o endereço de memória calculado, não o valor apontado.
    

---

## 2. `cmp` — Comparação

### Função:

Compara dois operandos realizando uma subtração implícita e atualiza os **flags** do processador (ZF, SF, CF, OF), mas **não altera os operandos**.

### Sintaxe:

```asm
cmp[tamanho] operando1, operando2   ; operando2 - operando1
```

### Sufixos de tamanho:

|Sufixo|Tamanho|Significado|
|---|---|---|
|`b`|8 bits|Byte|
|`w`|16 bits|Word|
|`l`|32 bits|Long|
|`q`|64 bits|Quadword|

### Exemplos:

```asm
cmpb $0, (%r12)     ; compara o byte apontado por %r12 com 0
cmpl %eax, %ebx     ; compara EBX - EAX
cmpq %rax, %rbx     ; compara RBX - RAX
```

### Tipos de comparação:

- `cmpb`, `cmpw`, `cmpl`, `cmpq` → Comparam operandos de 8, 16, 32 e 64 bits
    
- Utilizadas antes de instruções de salto condicional como `je`, `jne`, `jg`, `jl`, etc.
    

---

## 3. `push` — Empilhar valor na pilha

### Função:

Empurra (salva) um valor na pilha, decrementando `%rsp` e armazenando o valor no novo topo.

### Sintaxe:

```asm
push[tamanho] operando
```

### Sufixos e tipos:

- `pushb` não existe diretamente — push só aceita 16, 32 ou 64 bits (depende do modo)
    
- `pushw` → Empilha 16 bits (modo compatibilidade)
    
- `pushl` → Empilha 32 bits (modo compatibilidade)
    
- `pushq` → Empilha 64 bits (modo x86-64)
    

### Exemplos:

```asm
pushq %rbp          ; salva o ponteiro de base na pilha
pushq $0x12345678   ; empilha um valor literal
```

### Observações:

- Usado no prólogo de funções para salvar registradores.
    
- Mantém o alinhamento da pilha.
    
- Pode ser usado para empilhar valores literais, endereços, ou valores de registradores.
    

---

## 4. `call` — Chamada de função

### Função:

Salta para uma função e salva o endereço de retorno (próxima instrução) na pilha.

### Sintaxe:

```asm
call destino
```

### Exemplos:

```asm
call printf         ; chama a função printf
```

### Contexto:

- Usado para transferir controle para funções externas ou internas.
    
- A função chamada retorna via `ret`, que usa o endereço previamente salvo na pilha.
    

---

## 5. `jmp` e Saltos Condicionais

### `jmp` — Salto incondicional

Salta para o endereço especificado.

```asm
jmp destino
```

### Saltos Condicionais (com base nos flags do `cmp` ou `test`):

|Instrução|Significado|Condição|
|---|---|---|
|`je` / `jz`|jump if equal / zero|ZF = 1|
|`jne` / `jnz`|jump if not equal / not zero|ZF = 0|
|`jg` / `jnle`|jump if greater (signed)|ZF = 0 e SF = OF|
|`jge`|jump if greater or equal (signed)|SF = OF|
|`jl`|jump if less (signed)|SF ≠ OF|
|`jle`|jump if less or equal (signed)|ZF = 1 ou SF ≠ OF|
|`ja`|jump if above (unsigned)|CF = 0 e ZF = 0|
|`jae`|jump if above or equal (unsigned)|CF = 0|
|`jb`|jump if below (unsigned)|CF = 1|
|`jbe`|jump if below or equal (unsigned)|CF = 1 ou ZF = 1|

### Observações:

- Utilizados após instruções como `cmp`, `test`, ou diretamente após uma condição booleana.
    
- Podem ser usados com rótulos (`L1`, `end_loop`, etc.) ou com endereços.
    

---

## 6. Instruções auxiliares de movimentação com extensão de tamanho

### `movsX` — Move com extensão de sinal

|Instrução|Origem → Destino|Ação|
|---|---|---|
|`movsbl`|8 bits → 32 bits|Estende byte com sinal|
|`movsbq`|8 bits → 64 bits|Estende byte com sinal|
|`movswl`|16 bits → 32 bits|Estende word com sinal|
|`movslq`|32 bits → 64 bits|Estende long com sinal|

### `movzX` — Move com extensão zero (zero-extension)

|Instrução|Origem → Destino|Ação|
|---|---|---|
|`movzbl`|8 bits → 32 bits|Preenche com zeros|
|`movzbq`|8 bits → 64 bits|Preenche com zeros|

### Exemplos:

```asm
movsbl (%r12), %eax     ; lê byte com sinal e estende para 32 bits
movzbl (%r12), %eax     ; lê byte sem sinal e estende para 32 bits
movsbq (%r12), %rax     ; lê byte com sinal e estende para 64 bits
```

---

## Considerações Finais

- Os registradores têm tamanhos diferentes: `%rax` (64), `%eax` (32), `%ax` (16), `%al` (8).
    
- A ABI (Application Binary Interface) define onde os argumentos de funções devem estar:
    
    - `%rdi`, `%rsi`, `%rdx`, `%rcx`, `%r8`, `%r9` para inteiros/pointers
        
    - `%xmm0` a `%xmm7` para ponto flutuante
        
- Em funções variádicas como `printf`, tipos menores que `int` devem ser promovidos para `int` (por isso usamos `movsbl` com `%c`).
    

Este documento cobre as bases fundamentais e mais usadas em Assembly para programadores que lidam com código de baixo nível, sistemas operacionais, compiladores ou engenharia reversa. Para comandos adicionais (como `lea`, `ret`, `pop`, instruções lógicas e aritméticas), recomenda-se complementar com materiais como a Intel® Software Developer's Manual ou a documentação do NASM e GAS.