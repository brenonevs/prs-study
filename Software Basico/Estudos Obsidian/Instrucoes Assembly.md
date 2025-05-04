
# Instruções Assembly x86-64 — Guia Completo com Base no Manual SBINST64

Este documento reúne todas as instruções apresentadas no material "sbinst64.pdf", explicando sua função, sintaxe e uso no contexto da linguagem Assembly para a arquitetura x86-64 (sintaxe AT&T), com comentários técnicos e observações de uso prático.

---

## 🔧 Registradores Gerais

|Bits|Nome|Função típica|
|---|---|---|
|64|`%rax`|valor de retorno|
|64|`%rbx`|callee-saved|
|64|`%rcx`|4º argumento|
|64|`%rdx`|3º argumento|
|64|`%rsi`|2º argumento|
|64|`%rdi`|1º argumento|
|64|`%r8`–`%r15`|argumentos extras / saved|
|64|`%rbp`|frame pointer|
|64|`%rsp`|stack pointer|

Cada registrador tem versões de 32, 16 e 8 bits:

- Exemplo: `%rax` (64 bits), `%eax` (32), `%ax` (16), `%al` / `%ah` (8)
    

---

## 🧱 MOV — Transferência de Dados

```asm
mov{b,w,l,q} origem, destino
```

- Move o valor de `origem` para `destino`
    
- Sufixos:
    
    - `b`: byte (8 bits)
        
    - `w`: word (16 bits)
        
    - `l`: long (32 bits)
        
    - `q`: quadword (64 bits)
        

### Variantes:

- `movabsq`: usado para mover uma constante de 64 bits para registrador.
    

---

## ➕ Operações Aritméticas

```asm
add op1, op2   ; op2 ← op2 + op1
sub op1, op2   ; op2 ← op2 - op1
imul op1, op2  ; op2 ← op1 * op2
inc op1        ; op1 ← op1 + 1
dec op1        ; op1 ← op1 - 1
neg op1        ; op1 ← -op1 (complemento a dois)
```

---

## 🔐 Operações Lógicas

```asm
and op1, op2   ; op2 ← op2 & op1
or  op1, op2   ; op2 ← op2 | op1
xor op1, op2   ; op2 ← op2 ^ op1
not op1        ; op1 ← ~op1
```

---

## 🔍 Comparações

```asm
cmp op1, op2   ; compara op2 - op1 (sem alterar operandos)
test op1, op2  ; verifica bits comuns (op1 & op2), afeta flags
```

---

## ⏩ Deslocamentos (Shift)

```asm
shl $n, op1    ; shift lógico para a esquerda (<<)
shr $n, op1    ; shift lógico para a direita (>> zero-fill)
sar $n, op1    ; shift aritmético à direita (>> com sinal)
```

---

## 📍 LEAQ — Load Effective Address

```asm
leaq fonte, destino
```

Carrega o **endereço calculado** da fonte em `destino`. Muito útil para aritmética de ponteiros.

---

## 🔄 Extensões de Tamanho

### Com sinal:

```asm
movsb[w][l][q] op1, op2   ; estende 8 bits com sinal
movsw[l][q]  op1, op2     ; estende 16 bits com sinal
movslq       op1, op2     ; estende 32 → 64 bits com sinal
```

### Sem sinal:

```asm
movzb[w][l][q] op1, op2   ; estende 8 bits com zero
movzw[l][q]    op1, op2   ; estende 16 bits com zero
```

---

## 🎯 Desvios Condicionais

### Para igualdade:

```asm
je / jz    ; se igual (ZF = 1)
jne / jnz  ; se diferente (ZF = 0)
```

### Sem sinal:

```asm
ja / jnbe  ; se acima (CF = 0 e ZF = 0)
jae / jnb  ; se acima ou igual (CF = 0)
jb / jnae  ; se abaixo (CF = 1)
jbe / jna  ; se abaixo ou igual (CF = 1 ou ZF = 1)
```

### Com sinal:

```asm
jg / jnle  ; se maior (ZF = 0 e SF = OF)
jge / jnl  ; se maior ou igual (SF = OF)
jl / jnge  ; se menor (SF ≠ OF)
jle / jng  ; se menor ou igual (ZF = 1 ou SF ≠ OF)
```

---

## 🚀 Controle de Fluxo

```asm
jmp destino    ; salto incondicional
call destino   ; chama função (empilha endereço de retorno)
ret            ; retorna (usa topo da pilha como endereço)
int valor      ; interrupção (sistema ou debug)
```

---

## 🧮 Instruções de Ponto Flutuante

### Registradores: `%xmm0` a `%xmm15`

- Argumentos: `%xmm0` a `%xmm7`
    
- Retorno: `%xmm0`
    

### Movimentação:

```asm
movs{s,d} op1, op2       ; move float (SS) ou double (SD)
```

### Conversão:

```asm
cvtss2sd op1, op2        ; float → double
cvtsd2ss op1, op2        ; double → float
cvtsi2ss/op2             ; int → float
ttss2si / ttsd2si / siq  ; float/double → int/long
```

### Aritmética:

```asm
add{s,d} op1, op2
sub{s,d} op1, op2
mul{s,d} op1, op2
div{s,d} op1, op2
```

### Comparação:

```asm
ucomis{s,d} op1, op2     ; compara (sem sinal)
```

---

Este guia consolida todas as instruções do arquivo `sbinst64.pdf` com explicações estendidas para facilitar o aprendizado, revisão e consulta prática no desenvolvimento em Assembly com sintaxe AT&T na arquitetura x86-64.