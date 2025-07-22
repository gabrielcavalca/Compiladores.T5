# 🔍 Gerador de Código - Linguagem Algorítmica (LA)

Este projeto implementa um **gerador de código C** a partir de programas escritos na **linguagem algorítmica LA** (desenvolvida pelo Prof. Jander, DC/UFSCar). O compilador lê um arquivo com código fonte em LA, realiza a análise léxica, sintática e semântica, e **gera código equivalente em C** como saída.

## 👥 Autores

**Disciplina:** Construção de Compiladores  
**Trabalho:** T5 - Gerador de Código

| Nome | RA |
|------|-----|
| Nataly Cristina da Silva | 812719 |
| Gabriel Cavalca Leite | 813615 |

## 📋 Descrição do Projeto

O projeto combina o **analisador léxico, sintático, semântico** e o **gerador de código** em um único executável. A partir de um programa válido em LA, o compilador gera um arquivo `.c` com código equivalente, pronto para ser compilado com `gcc`.

O comportamento do compilador é o seguinte:

- 📌 Se o código de entrada contiver **erros léxicos, sintáticos ou semânticos**, esses erros são listados no arquivo de saída.
- ✅ Se **não houver erros**, o código em C gerado é salvo no arquivo de saída.

## ⚙️ Pré-requisitos e Dependências

### Requisitos do Sistema:
- **Python 3.x** (versão 3.6 ou superior)
- **ANTLR4** (biblioteca Python antlr4-python3-runtime)
- **Java** (para executar corretor automático)
- **Git** (para clonar o repositório)
- **GCC** (para compilar e executar o código gerado)

### Instalação das Dependências:
```bash
# Instalar ANTLR4 para Python
pip install antlr4-python3-runtime

# Verificar instalações
python3 --version
java -version
gcc --version
```

## 📥 Como Baixar o Projeto

### Passo 1: Clonar o Repositório
```bash
# Clonar o repositório do GitHub
git clone [https://github.com/gabrielcavalca/Compiladores.T3.git
](https://github.com/gabrielcavalca/Compiladores.T5.git)

# Navegar para o diretório do projeto
cd Compiladores.T5
```

### Passo 2: Verificar Arquivos
```bash
# Listar arquivos do projeto
ls -la

# Verificar se os arquivos necessários estão presentes:
# - compilador.py
# - LAParser.py
# - LALexer.py  
# - LAListener.py
```

## 🔧 Como Compilar

**✅** Todos os arquivos Python já estão prontos no repositório.

### Passo 1: Instalar Dependências
```bash
# Instalar ANTLR4 para Python (única dependência necessária)
pip install antlr4-python3-runtime
```

### Passo 2: Testar Instalação
```bash
# Verificar se o analisador executa corretamente
python3 compilador.py
# Deve mostrar a mensagem de uso do programa
```

> **✅ Projeto Pronto:** Todos os arquivos necessários (LAParser.py, LALexer.py, LAListener.py) já estão incluídos no repositório, gerados a partir da gramática ANTLR4.

## 🚀 Como Executar

### Sintaxe Básica:
```bash
python3 compilador.py <arquivo_entrada> <arquivo_saida>
```
##### ⚠️ Observações Importantes:
O compilador NÃO imprime no terminal. Toda a saída é salva no arquivo de saída.

A saída será:

- Código em C, se não houver erro.

- Mensagens de erro, se houver problemas léxicos/sintáticos/semânticos.

### Passo 1: Teste de Funcionamento (Opcional)
```bash
# Exemplo de Execução Manual:
# Exemplo: python3 compilador.py exemplos/teste1.la temp/saida.c
```

**Obs:** Este é apenas um teste opcional. Os arquivos de entrada reais estão nos casos de teste fornecidos pelo professor.

### Passo 2: Execução com Corretor Automático (Recomendada)

**O corretor automático e casos de teste são fornecidos pelo professor.**

```bash
java -jar "compiladores-corretor-automatico-1.0-SNAPSHOT-jar-with-dependencies.jar" \
    "python3 /caminho/absoluto/para/compilador.py" \
    /usr/bin \
    "/caminho/para/pasta/temp" \
    "/caminho/para/casos-de-teste" \
    "813615, 812719" \
    "t5"
```

> **📁 Importante:** Os resultados serão salvos na pasta `/temp` especificada no comando. Substitua os caminhos pelos caminhos reais no seu sistema.

## 📝 Estrutura do Projeto

```
Compiladores.T5/
├── compilador.py    # Arquivo principal do analisador
├── LAParser.py               # Parser gerado pelo ANTLR4
├── LALexer.py               # Lexer gerado pelo ANTLR4
├── LAListener.py            # Listener gerado pelo ANTLR4
├── README.md                # Este arquivo
└── outros arquivos...
```
