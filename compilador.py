#!/usr/bin/env python3

import sys
import os
import subprocess
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from LALexer import LALexer
from LAParser import LAParser
from LAListener import LAListener

# Lista de tipos válidos (de acordo com a gramática)
TIPOS_VALIDOS = {'literal', 'inteiro', 'real', 'logico'}

class MeuErroListener(ErrorListener):
    def __init__(self):
        super(MeuErroListener, self).__init__()
        self.erros = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        simbolo = offendingSymbol.text
        if simbolo == "<EOF>":
            simbolo = "EOF"
        
        # Verificar erros léxicos específicos
        if hasattr(recognizer, 'symbolicNames'):
            # É um lexer
            if offendingSymbol.type == LALexer.CADEIA_NAO_FECHADA:
                self.erros.append(f"Linha {line}: cadeia literal nao fechada")
                return
            elif offendingSymbol.type == LALexer.CARACTERE_INVALIDO:
                self.erros.append(f"Linha {line}: {simbolo} - simbolo nao identificado")
                return
            elif offendingSymbol.type == LALexer.COMENTARIO_NAO_FECHADO:
                self.erros.append(f"Linha {line}: comentario nao fechado")
                return
        
        # Erro sintático
        self.erros.append(f"Linha {line}: erro sintatico proximo a {simbolo}")

class AnalisadorSemantico(LAListener):
    def __init__(self, token_stream):
        self.simbolos = {}   # dicionário nome -> tipo
        self.erros = []
        self.tokens = token_stream
        self.tipos_definidos = {}  # Para armazenar tipos personalizados como registros
        self.campos_registro = {}  # Para armazenar campos de registros
        self.funcoes = {}  # Para armazenar informações sobre funções
        self.procedimentos = {}  # Para armazenar informações sobre procedimentos
        self.escopo_atual = 'global'  # Para controlar escopo
        self.simbolos_locais = {}  # Para armazenar símbolos do escopo local atual
        self.constantes = {}  # Para armazenar constantes declaradas

    def tipo_expressao(self, ctx):
        """Determina o tipo de uma expressão"""
        from LAParser import LAParser

        if isinstance(ctx, LAParser.ExpressaoContext):
            return self.tipo_expressao(ctx.expressao_logica())

        elif isinstance(ctx, LAParser.Expressao_logicaContext):
            tipos = [self.tipo_expressao(child) for child in ctx.expressao_relacional()]
            if len(tipos) == 1:
                return tipos[0]
            if all(t == 'logico' for t in tipos):
                return 'logico'
            else:
                return None

        elif isinstance(ctx, LAParser.Expressao_relacionalContext):
            if ctx.getChildCount() == 1:
                return self.tipo_expressao(ctx.expressao_aritmetica(0))
            else:
                tipo_esq = self.tipo_expressao(ctx.expressao_aritmetica(0))
                tipo_dir = self.tipo_expressao(ctx.expressao_aritmetica(1))
                if tipo_esq in ('inteiro','real') and tipo_dir in ('inteiro','real'):
                    return 'logico'
                if tipo_esq == tipo_dir:
                    return 'logico'
                return None

        elif isinstance(ctx, LAParser.Expressao_aritmeticaContext):
            tipos = [self.tipo_expressao(term) for term in ctx.termo()]
            tipo_acumulado = tipos[0]
            for t in tipos[1:]:
                if tipo_acumulado in ('inteiro','real') and t in ('inteiro','real'):
                    tipo_acumulado = 'real' if 'real' in (tipo_acumulado, t) else 'inteiro'
                elif tipo_acumulado == 'literal' and t == 'literal':
                    tipo_acumulado = 'literal'
                else:
                    return None
            return tipo_acumulado

        elif isinstance(ctx, LAParser.TermoContext):
            tipos = [self.tipo_expressao(fat) for fat in ctx.fator()]
            tipo_acumulado = tipos[0]
            for t in tipos[1:]:
                if tipo_acumulado in ('inteiro','real') and t in ('inteiro','real'):
                    tipo_acumulado = 'real' if 'real' in (tipo_acumulado, t) else 'inteiro'
                else:
                    return None
            return tipo_acumulado

        elif isinstance(ctx, LAParser.FatorContext):
            if ctx.IDENT():
                nome = ctx.IDENT().getText()
                tipo_var = self.simbolos.get(nome)
                if tipo_var is None:
                    # Verifica se está no escopo local
                    tipo_var = self.simbolos_locais.get(nome)
                if tipo_var is None:
                    token = ctx.IDENT().getSymbol()
                    self.erros.append(f"Linha {token.line}: identificador {nome} nao declarado")
                return tipo_var

            if ctx.NUM_INT():
                return 'inteiro'
            if ctx.NUM_REAL():
                return 'real'
            if ctx.CADEIA():
                return 'literal'
            if ctx.getText() in ('verdadeiro', 'falso'):
                return 'logico'
            if ctx.ABREPAR():
                return self.tipo_expressao(ctx.expressao())
            if ctx.getChildCount() == 2 and ctx.getChild(0).getText() == '-':
                return self.tipo_expressao(ctx.fator())
            if ctx.getChildCount() == 2 and ctx.getChild(0).getText().lower() == 'nao':
                t = self.tipo_expressao(ctx.fator())
                return 'logico' if t == 'logico' else None

            return None
        else:
            return None

    def eh_compativel(self, tipo_var, tipo_exp):
        if tipo_var == tipo_exp:
            return True
        if tipo_var == 'real' and tipo_exp == 'inteiro':
            return True
        return False

    def enterDeclaracao(self, ctx):
        """Processa declaração de variáveis"""
        for var_ctx in ctx.lista_variaveis().variavel():
            tipo_ctx = var_ctx.tipo()
            
            # Verifica se é um registro inline ou tipo simples
            if hasattr(tipo_ctx, 'tipo_registro') and tipo_ctx.tipo_registro():
                # Registro inline - cria tipo temporário
                nome_tipo_temp = f"registro_inline_{id(var_ctx)}"
                campos = {}
                
                for campo_ctx in tipo_ctx.tipo_registro().lista_campos().campo():
                    tipo_campo = campo_ctx.tipo_base().getText()
                    
                    # Verifica se tipo do campo é válido
                    if tipo_campo not in TIPOS_VALIDOS and tipo_campo not in self.tipos_definidos:
                        token_tipo = campo_ctx.tipo_base().start
                        self.erros.append(f"Linha {token_tipo.line}: tipo {tipo_campo} nao declarado")
                        continue
                    
                    # Adiciona todos os identificadores do campo
                    for ident in campo_ctx.IDENT():
                        nome_campo = ident.getText()
                        campos[nome_campo] = tipo_campo
                
                self.tipos_definidos[nome_tipo_temp] = 'registro'
                self.campos_registro[nome_tipo_temp] = campos
                tipo_texto = nome_tipo_temp
            else:
                # Tipo simples ou customizado
                tipo_texto = tipo_ctx.getText().replace("^", "")
                
                if tipo_texto not in TIPOS_VALIDOS and tipo_texto not in self.tipos_definidos:
                    token_tipo = tipo_ctx.start
                    self.erros.append(f"Linha {token_tipo.line}: tipo {tipo_texto} nao declarado")
            
            # Extrair nomes das variáveis
            variable_names = self.extract_variable_names(var_ctx)
            
            for nome_var in variable_names:
                if nome_var in self.simbolos or nome_var in self.simbolos_locais:
                    # Encontra o token correspondente
                    for i in range(var_ctx.getChildCount()):
                        child = var_ctx.getChild(i)
                        if hasattr(child, 'getText') and child.getText() == nome_var:
                            if hasattr(child, 'getSymbol'):
                                token_var = child.getSymbol()
                                self.erros.append(f"Linha {token_var.line}: identificador {nome_var} ja declarado")
                            break
                else:
                    if self.escopo_atual == 'global':
                        self.simbolos[nome_var] = tipo_texto
                    else:
                        self.simbolos_locais[nome_var] = tipo_texto

    def extract_variable_names(self, var_ctx):
        """Extrai nomes de variáveis do contexto"""
        variable_names = []
        children = [var_ctx.getChild(i) for i in range(var_ctx.getChildCount())]
        
        i = 0
        while i < len(children):
            child = children[i]
            if hasattr(child, 'getSymbol') and child.getSymbol().type == LALexer.IDENT:
                # Verifica se não é tamanho de array
                if i + 1 < len(children) and hasattr(children[i + 1], 'getText') and children[i + 1].getText() == '[':
                    # Pula o [, o tamanho e o ]
                    variable_names.append(child.getText())
                    i += 3  # pula [, tamanho, ]
                elif i > 0 and hasattr(children[i - 1], 'getText') and children[i - 1].getText() == '[':
                    # É tamanho de array, pula
                    i += 1
                elif hasattr(children[i - 1], 'getText') and children[i - 1].getText() in ['[', ']']:
                    # É parte de declaração de array, pula
                    i += 1
                else:
                    variable_names.append(child.getText())
                    i += 1
            else:
                i += 1
                
        return variable_names

    def enterAtribuicao(self, ctx):
        """Verifica atribuições"""
        lado_esquerdo = ctx.getChild(0)
        
        # Verifica se é acesso a campo (reg.nome)
        if hasattr(lado_esquerdo, 'getRuleIndex'):
            from LAParser import LAParser
            if lado_esquerdo.getRuleIndex() == LAParser.RULE_acesso_campo:
                # É acesso a campo, já será validado pelo enterAcesso_campo
                return
            elif lado_esquerdo.getRuleIndex() == LAParser.RULE_acesso_array:
                # É acesso a array (vetor[i]), verifica se o vetor foi declarado
                if hasattr(lado_esquerdo, 'IDENT'):
                    nome_array = lado_esquerdo.IDENT().getText()
                    tipo_var = self.simbolos.get(nome_array) or self.simbolos_locais.get(nome_array)
                    if tipo_var is None:
                        token_var = lado_esquerdo.IDENT().getSymbol()
                        self.erros.append(f"Linha {token_var.line}: identificador {nome_array} nao declarado")
                return
        
        # Verifica se é um ponteiro (CIRCUNFLEXO IDENT - dois nós separados)
        if hasattr(lado_esquerdo, 'getSymbol') and lado_esquerdo.getSymbol().text == '^':
            # Próximo nó deve ser o IDENT
            if ctx.getChildCount() > 1:
                segundo_no = ctx.getChild(1)
                if hasattr(segundo_no, 'getText'):
                    nome_var = segundo_no.getText()
                else:
                    nome_var = ""
            else:
                nome_var = ""
        else:
            lado_esquerdo_texto = lado_esquerdo.getText()
            # Verifica se é acesso a array (contém colchetes)
            if '[' in lado_esquerdo_texto and ']' in lado_esquerdo_texto:
                # É acesso a array como string, extrai o nome da variável
                nome_var = lado_esquerdo_texto.split('[')[0]
            # Verifica se é acesso a campo (contém ponto)
            elif '.' in lado_esquerdo_texto:
                # É acesso a campo, será validado em enterAcesso_campo
                return
            # Verifica se é um ponteiro como string completa
            elif lado_esquerdo_texto.startswith('^'):
                nome_var = lado_esquerdo_texto[1:]
            # Verifica se é endereçamento (&IDENT)
            elif lado_esquerdo_texto.startswith('&'):
                nome_var = lado_esquerdo_texto[1:]
            else:
                nome_var = lado_esquerdo_texto
        
        # Verifica se variável foi declarada
        if nome_var:  # Só verifica se nome_var não é vazio
            tipo_var = self.simbolos.get(nome_var) or self.simbolos_locais.get(nome_var)
            if tipo_var is None:
                # Tenta encontrar o token correto para a mensagem de erro
                token_var = None
                if hasattr(lado_esquerdo, 'getSymbol'):
                    token_var = lado_esquerdo.getSymbol()
                elif ctx.getChildCount() > 1 and hasattr(ctx.getChild(1), 'getSymbol'):
                    token_var = ctx.getChild(1).getSymbol()
                
                if token_var:
                    self.erros.append(f"Linha {token_var.line}: identificador {nome_var} nao declarado")

            # Verifica compatibilidade de tipos
            tipo_exp = self.tipo_expressao(ctx.expressao())
            if tipo_var is not None and tipo_exp is not None and not self.eh_compativel(tipo_var, tipo_exp):
                token_var = None
                if hasattr(lado_esquerdo, 'getSymbol'):
                    token_var = lado_esquerdo.getSymbol()
                elif ctx.getChildCount() > 1 and hasattr(ctx.getChild(1), 'getSymbol'):
                    token_var = ctx.getChild(1).getSymbol()
                
                if token_var:
                    self.erros.append(f"Linha {token_var.line}: atribuicao nao compativel para {nome_var}")

    def enterLeitura(self, ctx):
        """Verifica comando leia"""
        lista_ids = ctx.lista_identificadores()
        for child in lista_ids.children:
            if hasattr(child, 'getText') and child.getText() != ',':
                nome = child.getText()
                if nome not in self.simbolos and nome not in self.simbolos_locais:
                    if hasattr(child, 'getSymbol'):
                        token_id = child.getSymbol()
                        self.erros.append(f"Linha {token_id.line}: identificador {nome} nao declarado")

    def enterEscrita(self, ctx):
        """Verifica comando escreva"""
        for exp in ctx.expressao():
            self.tipo_expressao(exp)
    
    def enterDeclaracao_procedimento(self, ctx):
        """Processa declaração de procedimento para análise semântica"""
        nome = ctx.IDENT().getText()
        
        # Armazena informações do procedimento
        self.procedimentos[nome] = {'parametros': []}
        
        # Processa parâmetros
        if ctx.parametros():
            for param_ctx in ctx.parametros().parametro():
                param_nome = param_ctx.IDENT().getText()
                if param_ctx.tipo_base():
                    param_tipo = param_ctx.tipo_base().getText()
                else:
                    param_tipo = param_ctx.tipo_identificado().getText()
                self.procedimentos[nome]['parametros'].append((param_nome, param_tipo))
                
                # Adiciona parâmetro ao escopo local
                self.simbolos_locais[param_nome] = param_tipo
        
        # Muda escopo
        self.escopo_atual = nome
    
    def exitDeclaracao_procedimento(self, ctx):
        """Finaliza análise semântica do procedimento"""
        self.escopo_atual = 'global'
        self.simbolos_locais = {}
    
    def enterChamada_procedimento(self, ctx):
        """Verifica chamada de procedimento"""
        nome = ctx.IDENT().getText()
        
        # Verifica se o procedimento foi declarado
        if nome not in self.procedimentos:
            token = ctx.IDENT().getSymbol()
            self.erros.append(f"Linha {token.line}: identificador {nome} nao declarado")
            return
        
        # Verifica número de argumentos
        num_args = 0
        if ctx.lista_expressao():
            num_args = len(ctx.lista_expressao().expressao())
        
        num_params = len(self.procedimentos[nome]['parametros'])
        if num_args != num_params:
            token = ctx.IDENT().getSymbol()
            self.erros.append(f"Linha {token.line}: incompatibilidade de parametros na chamada de {nome}")

    def enterDeclaracao_tipo(self, ctx):
        """Processa declarações de tipo (registros)"""
        nome_tipo = ctx.IDENT().getText()
        
        # Verifica se já foi declarado
        if nome_tipo in self.tipos_definidos:
            token = ctx.IDENT().getSymbol()
            self.erros.append(f"Linha {token.line}: tipo {nome_tipo} ja declarado")
            return
        
        # Verifica se é tipo_registro ou tipo_identificado
        # ctx tem: 'tipo' IDENT ':' (tipo_registro | tipo_identificado)
        if len(ctx.children) >= 4:
            tipo_def = ctx.children[3]  # quarto elemento (tipo_registro ou tipo_identificado)
            
            # Se for um registro, processa os campos
            if hasattr(tipo_def, 'lista_campos'):  # é tipo_registro
                campos = {}
                for campo_ctx in tipo_def.lista_campos().campo():
                    tipo_campo = campo_ctx.tipo_base().getText()
                    
                    # Verifica se tipo do campo é válido
                    if tipo_campo not in TIPOS_VALIDOS and tipo_campo not in self.tipos_definidos:
                        token_tipo = campo_ctx.tipo_base().start
                        self.erros.append(f"Linha {token_tipo.line}: tipo {tipo_campo} nao declarado")
                        continue
                    
                    # Adiciona todos os identificadores do campo
                    for ident in campo_ctx.IDENT():
                        nome_campo = ident.getText()
                        campos[nome_campo] = tipo_campo
                
                self.tipos_definidos[nome_tipo] = 'registro'
                self.campos_registro[nome_tipo] = campos
            
            # Se for tipo identificado (typedef simples)
            else:  # é tipo_identificado
                tipo_base = tipo_def.getText()
                if tipo_base not in TIPOS_VALIDOS and tipo_base not in self.tipos_definidos:
                    token_tipo = tipo_def.start
                    self.erros.append(f"Linha {token_tipo.line}: tipo {tipo_base} nao declarado")
                else:
                    self.tipos_definidos[nome_tipo] = tipo_base

    def enterAcesso_campo(self, ctx):
        """Verifica acesso a campos de registro"""
        # ctx.getText() retorna algo como "reg.nome"
        acesso_texto = ctx.getText()
        partes = acesso_texto.split('.')
        
        if len(partes) >= 2:
            nome_var = partes[0]
            nome_campo = partes[1]
            
            # Verifica se a variável foi declarada
            tipo_var = self.simbolos.get(nome_var) or self.simbolos_locais.get(nome_var)
            if tipo_var is None:
                token = ctx.start
                self.erros.append(f"Linha {token.line}: identificador {nome_var} nao declarado")
                return
            
            # Verifica se o tipo da variável é um registro
            if tipo_var not in self.campos_registro:
                token = ctx.start
                self.erros.append(f"Linha {token.line}: {nome_var} nao e do tipo registro")
                return
            
            # Verifica se o campo existe no registro
            if nome_campo not in self.campos_registro[tipo_var]:
                token = ctx.start
                self.erros.append(f"Linha {token.line}: campo {nome_campo} nao existe no registro {tipo_var}")

    def enterAcesso_array(self, ctx):
        """Verifica acesso a arrays"""
        # ctx é algo como "vetor[i]"
        nome_array = ctx.IDENT().getText()
        
        # Verifica se o array foi declarado
        tipo_var = self.simbolos.get(nome_array) or self.simbolos_locais.get(nome_array)
        if tipo_var is None:
            token = ctx.IDENT().getSymbol()
            self.erros.append(f"Linha {token.line}: identificador {nome_array} nao declarado")
            return
        
        # Verifica se o índice é válido (deve ser inteiro)
        tipo_indice = self.tipo_expressao(ctx.expressao())
        if tipo_indice is not None and tipo_indice != 'inteiro':
            token = ctx.start
            self.erros.append(f"Linha {token.line}: indice de array deve ser inteiro")

class GeradorCodigo(LAListener):
    def __init__(self):
        self.codigo = []
        self.declaracoes = []
        self.defines = []  # Para #define das constantes
        self.tipos_structs = []  # Para typedef structs
        self.funcoes = []
        self.procedimentos = []
        self.tabela_simbolos = {}
        self.escopo_atual = 'global'
        self.em_funcao = False
        self.em_procedimento = False
        self.nivel_escopo = 0
        self.constantes = {}
        self.contextos_processados = set()  # Para evitar processamento duplo
        self.bloqueando_automatico = False  # Flag para bloquear processamento automático
        
    def adicionar_codigo(self, linha, indent=0):
        """Adiciona uma linha de código com indentação"""
        linha_formatada = '\t' * indent + linha
        
        if self.em_funcao:
            self.funcoes.append(linha_formatada)
        elif self.em_procedimento:
            self.procedimentos.append(linha_formatada)
        else:
            self.codigo.append(linha_formatada)
    
    def adicionar_declaracao(self, linha):
        """Adiciona uma declaração de variável"""
        self.declaracoes.append('\t' + linha)
    
    def traduzir_tipo(self, tipo_la, eh_parametro=False):
        """Traduz tipo da linguagem LA para C"""
        tipos = {
            'inteiro': 'int',
            'real': 'float', 
            'literal': 'char*' if eh_parametro else 'char',
            'logico': 'int'
        }
        
        # Remove ponteiro se existir
        if tipo_la.startswith('^'):
            tipo_base = tipo_la[1:]
            if tipo_base in tipos:
                base_tipo = tipos[tipo_base]
                if tipo_base == 'literal' and eh_parametro:
                    return 'char**'  # ponteiro para string
                else:
                    return base_tipo + '*'
            else:
                return tipo_base + '*'
        
        return tipos.get(tipo_la, tipo_la)
    
    def obter_formato_printf(self, tipo):
        """Retorna o formato correto para printf/scanf baseado no tipo"""
        formatos = {
            'int': '%d',
            'float': '%f',
            'char': '%s',
            'char*': '%s'
        }
        return formatos.get(tipo, '%d')
    
    def exitPrograma(self, ctx):
        """Fim do programa - gera código completo"""
        # Gera as funções primeiro
        codigo_final = []
        codigo_final.extend(['#include <stdio.h>', '#include <stdlib.h>', '#include <string.h>', ''])
        
        # Adiciona defines das constantes
        codigo_final.extend(self.defines)
        if self.defines:
            codigo_final.append('')  # Linha em branco após defines
        
        # Adiciona typedefs de structs
        codigo_final.extend(self.tipos_structs)
        if self.tipos_structs:
            codigo_final.append('')  # Linha em branco após typedefs
        
        # Adiciona funções e procedimentos
        codigo_final.extend(self.funcoes)
        codigo_final.extend(self.procedimentos)
        
        # Função main
        codigo_final.append('int main() {')
        codigo_final.extend(self.declaracoes)
        codigo_final.extend(self.codigo)
        codigo_final.append('\treturn 0;')
        codigo_final.append('}')
        
        self.codigo = codigo_final
    
    def enterDeclaracao(self, ctx):
        """Processa declaração de variáveis"""
        if not self.em_funcao and not self.em_procedimento:
            self.processar_declaracao_variaveis(ctx.lista_variaveis())
    
    def enterDeclaracao_constante(self, ctx):
        """Processa declaração de constantes"""
        nome_constante = ctx.IDENT().getText()
        valor_constante = ctx.valor_constante()
        
        # Determina o valor da constante
        if valor_constante.NUM_INT():
            valor = int(valor_constante.NUM_INT().getText())
        elif valor_constante.NUM_REAL():
            valor = float(valor_constante.NUM_REAL().getText())
        elif valor_constante.CADEIA():
            valor = valor_constante.CADEIA().getText()
        elif valor_constante.getText() == 'verdadeiro':
            valor = 1
        elif valor_constante.getText() == 'falso':
            valor = 0
        else:
            valor = valor_constante.getText()
        
        # Armazena a constante
        self.constantes[nome_constante] = valor
        
        # Gera #define em C
        if isinstance(valor, str) and valor.startswith('"'):
            # String literal
            self.defines.append(f'#define {nome_constante} {valor}')
        else:
            # Valor numérico
            self.defines.append(f'#define {nome_constante} {valor}')

    def enterDeclaracao_tipo(self, ctx):
        """Processa declaração de tipos (structs)"""
        nome_tipo = ctx.IDENT().getText()
        
        if ctx.tipo_registro():
            # Gera typedef struct
            campos = []
            for campo_ctx in ctx.tipo_registro().lista_campos().campo():
                tipo_campo_c = self.traduzir_tipo(campo_ctx.tipo_base().getText())
                
                # Processa todos os identificadores do campo
                for ident in campo_ctx.IDENT():
                    nome_campo = ident.getText()
                    if tipo_campo_c == 'char':
                        campos.append(f'\t{tipo_campo_c} {nome_campo}[80];')
                    else:
                        campos.append(f'\t{tipo_campo_c} {nome_campo};')
            
            # Adiciona typedef struct nas declarações globais
            struct_def = f'typedef struct {{\n' + '\n'.join(campos) + f'\n}} {nome_tipo};'
            self.tipos_structs.append(struct_def)
        
        elif ctx.tipo_identificado():
            # Typedef simples
            tipo_base = self.traduzir_tipo(ctx.tipo_identificado().getText())
            typedef_def = f'typedef {tipo_base} {nome_tipo};'
            self.tipos_structs.append(typedef_def)
    
    def processar_declaracao_variaveis(self, ctx_lista):
        """Processa lista de variáveis"""
        for variavel_ctx in ctx_lista.variavel():
            tipo_ctx = variavel_ctx.tipo()
            tipo_c = self.processar_tipo(tipo_ctx)
            
            # Debug: print dos tipos
            # print(f"DEBUG: tipo_ctx.getText() = '{tipo_ctx.getText()}'")
            # print(f"DEBUG: tipo_c = '{tipo_c}'")
            
            # Primeira variável
            nome = variavel_ctx.IDENT(0).getText()
            
            # Verifica se é array
            if variavel_ctx.ABRE_COLCHETE():
                tamanho = variavel_ctx.NUM_INT(0).getText() if variavel_ctx.NUM_INT() else variavel_ctx.IDENT(1).getText()
                if tipo_c == 'char':
                    self.adicionar_declaracao(f'{tipo_c} {nome}[80];')
                else:
                    self.adicionar_declaracao(f'{tipo_c} {nome}[{tamanho}];')
            else:
                if tipo_c == 'char':
                    self.adicionar_declaracao(f'{tipo_c} {nome}[80];')
                else:
                    self.adicionar_declaracao(f'{tipo_c} {nome};')
            
            self.tabela_simbolos[nome] = tipo_c
            
            # Variáveis adicionais na mesma linha
            for i in range(1, len(variavel_ctx.IDENT())):
                nome_extra = variavel_ctx.IDENT(i).getText()
                if tipo_c == 'char':
                    self.adicionar_declaracao(f'{tipo_c} {nome_extra}[80];')
                else:
                    self.adicionar_declaracao(f'{tipo_c} {nome_extra};')
                self.tabela_simbolos[nome_extra] = tipo_c

    def processar_tipo(self, ctx_tipo):
        """Processa contexto de tipo"""
        # Verifica se é um registro inline
        if hasattr(ctx_tipo, 'tipo_registro') and ctx_tipo.tipo_registro():
            # Gera struct inline
            campos = []
            for campo_ctx in ctx_tipo.tipo_registro().lista_campos().campo():
                tipo_campo_c = self.traduzir_tipo(campo_ctx.tipo_base().getText())
                
                # Processa todos os identificadores do campo
                for ident in campo_ctx.IDENT():
                    nome_campo = ident.getText()
                    if tipo_campo_c == 'char':
                        campos.append(f'\t{tipo_campo_c} {nome_campo}[80];')
                    else:
                        campos.append(f'\t{tipo_campo_c} {nome_campo};')
            
            # Retorna definição de struct inline
            struct_def = 'struct {\n' + '\n'.join(campos) + '\n}'
            return struct_def
        
        # Usa o texto completo do contexto para preservar ^ de ponteiros
        tipo_texto = ctx_tipo.getText()
        
        return self.traduzir_tipo(tipo_texto)
    
    def enterDeclaracao_funcao(self, ctx):
        """Processa declaração de função"""
        self.em_funcao = True
        nome = ctx.IDENT().getText()
        tipo_retorno = self.traduzir_tipo(ctx.tipo_base().getText())
        
        # Processa parâmetros
        parametros = []
        if ctx.parametros():
            for param_ctx in ctx.parametros().parametro():
                param_nome = param_ctx.IDENT().getText()
                if param_ctx.tipo_base():
                    param_tipo = self.traduzir_tipo(param_ctx.tipo_base().getText(), eh_parametro=True)
                else:
                    param_tipo = self.traduzir_tipo(param_ctx.tipo_identificado().getText(), eh_parametro=True)
                parametros.append(f'{param_tipo} {param_nome}')
                # Adiciona parâmetro à tabela de símbolos local
                self.tabela_simbolos[param_nome] = param_tipo.replace('*', '')
        
        params_str = ', '.join(parametros) if parametros else ''
        self.funcoes.append(f'{tipo_retorno} {nome}({params_str}) {{')
        
        # Salva declarações atuais
        self.declaracoes_temp = self.declaracoes
        self.declaracoes = []
        
        if ctx.declaracoes_locais():
            for decl_ctx in ctx.declaracoes_locais().lista_variaveis():
                self.processar_declaracao_variaveis(decl_ctx)
    
    def exitDeclaracao_funcao(self, ctx):
        """Finaliza declaração de função"""
        self.funcoes.extend(self.declaracoes)
        self.funcoes.append('}')
        self.funcoes.append('')
        self.declaracoes = self.declaracoes_temp
        self.em_funcao = False
    
    def enterDeclaracao_procedimento(self, ctx):
        """Processa declaração de procedimento"""
        self.em_procedimento = True
        nome = ctx.IDENT().getText()
        
        # Processa parâmetros
        parametros = []
        if ctx.parametros():
            for param_ctx in ctx.parametros().parametro():
                param_nome = param_ctx.IDENT().getText()
                if param_ctx.tipo_base():
                    param_tipo = self.traduzir_tipo(param_ctx.tipo_base().getText(), eh_parametro=True)
                else:
                    param_tipo = self.traduzir_tipo(param_ctx.tipo_identificado().getText(), eh_parametro=True)
                parametros.append(f'{param_tipo} {param_nome}')
                # Adiciona parâmetro à tabela de símbolos local
                self.tabela_simbolos[param_nome] = param_tipo.replace('*', '')
        
        params_str = ', '.join(parametros) if parametros else ''
        self.procedimentos.append(f'void {nome}({params_str}) {{')
        
        # Salva declarações atuais
        self.declaracoes_temp = self.declaracoes
        self.declaracoes = []
        
        if ctx.declaracoes_locais():
            for decl_ctx in ctx.declaracoes_locais().lista_variaveis():
                self.processar_declaracao_variaveis(decl_ctx)
    
    def exitDeclaracao_procedimento(self, ctx):
        """Finaliza declaração de procedimento"""
        self.procedimentos.extend(self.declaracoes)
        self.procedimentos.append('}')
        self.procedimentos.append('')
        self.declaracoes = self.declaracoes_temp
        self.em_procedimento = False
    
    def enterChamada_procedimento(self, ctx):
        """Processa chamada de procedimento"""
        nome = ctx.IDENT().getText()
        
        # Processa argumentos
        argumentos = []
        if ctx.lista_expressao():
            for expr_ctx in ctx.lista_expressao().expressao():
                arg = self.processar_expressao(expr_ctx)
                argumentos.append(arg)
        
        args_str = ', '.join(argumentos) if argumentos else ''
        linha = f'{nome}({args_str});'
        
        if self.em_funcao:
            self.funcoes.append(f'\t{linha}')
        elif self.em_procedimento:
            self.procedimentos.append(f'\t{linha}')
        else:
            self.adicionar_codigo(linha, 1)
    
    def enterRetorne(self, ctx):
        """Processa comando return"""
        expressao = self.processar_expressao(ctx.expressao())
        if self.em_funcao:
            self.funcoes.append(f'\treturn {expressao};')
        else:
            self.adicionar_codigo(f'return {expressao};', 1)
    
    def enterLeitura(self, ctx):
        """Processa comando de leitura"""
        # Se estamos bloqueando automático, não processa
        if self.bloqueando_automatico:
            return
            
        for ident_ctx in ctx.lista_identificadores().children:
            if hasattr(ident_ctx, 'getText'):
                nome = ident_ctx.getText()
                if nome != ',':
                    tipo = self.tabela_simbolos.get(nome, 'int')
                    formato = self.obter_formato_printf(tipo)
                    
                    if tipo == 'char':
                        linha = f'fgets({nome}, 80, stdin);'
                        self.adicionar_codigo(linha, 1)
                        # Remove a quebra de linha do fgets
                        linha = f'{nome}[strcspn({nome}, "\\n")] = \'\\0\';'
                    else:
                        linha = f'scanf("{formato}",&{nome});'
                    
                    self.adicionar_codigo(linha, 1)
    
    def enterEscrita(self, ctx):
        """Processa comando de escrita"""
        # Verifica se já foi processado manualmente
        ctx_id = (id(ctx), ctx.start.line, ctx.start.column)
        if ctx_id in self.contextos_processados:
            return
            
            # Verifica se é bloqueando automático, não processa
        if hasattr(self, 'bloqueando_automatico') and self.bloqueando_automatico:
            return
            
        expressoes = []
        formatos = []
        
        for expr_ctx in ctx.expressao():
            expr_text = self.processar_expressao(expr_ctx)
            
            # Verifica se é string literal
            if expr_text.startswith('"') and expr_text.endswith('"'):
                formatos.append('%s')
                expressoes.append(expr_text)
            # Verifica se é acesso a campo de struct (reg.nome)
            elif '.' in expr_text:
                # Para acesso a campos, assume que campos de char são strings (%s)
                # e campos int são inteiros (%d)
                partes = expr_text.split('.')
                if len(partes) == 2:
                    # Heurística: se o nome do campo sugere string, usa %s
                    nome_campo = partes[1]
                    if 'nome' in nome_campo.lower() or 'titulo' in nome_campo.lower() or 'descricao' in nome_campo.lower():
                        formatos.append('%s')
                    elif 'idade' in nome_campo.lower() or 'numero' in nome_campo.lower() or 'valor' in nome_campo.lower():
                        formatos.append('%d')
                    else:
                        # Default: %s para campos de string
                        formatos.append('%s')
                else:
                    formatos.append('%s')
                expressoes.append(expr_text)
            # Verifica se é variável conhecida
            elif expr_text in self.tabela_simbolos:
                tipo = self.tabela_simbolos[expr_text]
                formato = self.obter_formato_printf(tipo)
                formatos.append(formato)
                expressoes.append(expr_text)
            # Verifica se é constante
            elif expr_text in self.constantes:
                valor = self.constantes[expr_text]
                if valor.isdigit():
                    formatos.append('%d')
                else:
                    formatos.append('%s')
                expressoes.append(valor)
            # Expressão genérica
            else:
                # Tenta determinar o tipo da expressão
                if expr_text.replace('.','').replace('-','').isdigit() and '.' in expr_text:
                    formatos.append('%f')
                    expressoes.append(expr_text)
                elif expr_text.replace('-','').isdigit():
                    formatos.append('%d')
                    expressoes.append(expr_text)
                else:
                    # Para expressões complexas, tenta inferir o tipo das variáveis
                    formato_expr = self.inferir_tipo_expressao(expr_text)
                    formatos.append(formato_expr)
                    expressoes.append(expr_text)
        
        formato_str = ''.join(formatos)
        if expressoes:
            params = ','.join(expressoes)
            linha = f'printf("{formato_str}",{params});'
        else:
            linha = f'printf("{formato_str}");'
        
        self.adicionar_codigo(linha, 1)
    
    def inferir_tipo_expressao(self, expr_text):
        """Infere o tipo de uma expressão baseado nas variáveis envolvidas"""
        import re
        
        # Extrai identificadores da expressão (variáveis)
        identificadores = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expr_text)
        
        # Verifica o tipo das variáveis encontradas
        tem_real = False
        tem_inteiro = False
        
        for ident in identificadores:
            tipo = self.tabela_simbolos.get(ident, '')
            if tipo == 'float':
                tem_real = True
            elif tipo == 'int':
                tem_inteiro = True
        
        # Se tem pelo menos um real, a expressão é real
        if tem_real:
            return '%f'
        elif tem_inteiro:
            return '%d'
        else:
            return '%d'  # default

    def enterAtribuicao(self, ctx):
        """Processa atribuição"""
        # Se estamos bloqueando automático, não processa
        if self.bloqueando_automatico:
            return
            
        # Verifica se é ponteiro
        if ctx.getChildCount() >= 3 and ctx.getChild(0).getText() == '^':
            # É um ponteiro: ^IDENT <- expressao
            var = '*' + ctx.getChild(1).getText()
        else:
            # Atribuição normal
            var = ctx.children[0].getText()
            
        expr = self.processar_expressao(ctx.expressao())
        
        # Verifica se é atribuição para campo de string em struct
        if '.' in var and expr.startswith('"') and expr.endswith('"'):
            # É atribuição de string para campo de struct, usa strcpy
            linha = f'strcpy({var}, {expr});'
        else:
            linha = f'{var} = {expr};'
        
        self.adicionar_codigo(linha, 1)

    def enterComandose(self, ctx):
        """Processa comando if - processamento manual completo"""
        # Bloqueia processamento automático durante este comando
        self.bloqueando_automatico = True
        
        condicao = self.processar_expressao(ctx.expressao())
        
        # Abre o bloco if
        if self.em_funcao:
            self.funcoes.append(f'\tif ({condicao}) {{')
        elif self.em_procedimento:
            self.procedimentos.append(f'\tif ({condicao}) {{')
        else:
            self.adicionar_codigo(f'if ({condicao}) {{', 1)
        
        # Processa comandos do bloco THEN (primeiro bloco de comandos)
        comandos_then = ctx.comandos(0)
        for comando in comandos_then.comando():
            self.processar_comando_manual(comando)
        
        # Verifica se tem bloco ELSE
        if len(ctx.comandos()) > 1:
            # Abre o bloco else
            if self.em_funcao:
                self.funcoes.append('\t} else {')
            elif self.em_procedimento:
                self.procedimentos.append('\t} else {')
            else:
                self.adicionar_codigo('} else {', 1)
            
            # Processa comandos do bloco ELSE (segundo bloco de comandos)
            comandos_else = ctx.comandos(1)
            for comando in comandos_else.comando():
                self.processar_comando_manual(comando)
        
        # Fecha o bloco
        if self.em_funcao:
            self.funcoes.append('\t}')
        elif self.em_procedimento:
            self.procedimentos.append('\t}')
        else:
            self.adicionar_codigo('}', 1)
        
        # Reativa processamento automático
        self.bloqueando_automatico = False
    
    def enterComandocaso(self, ctx):
        """Processa comando caso (switch statement)"""
        # Marca este comando como processado manualmente
        cmd_id = f"caso_{ctx.start.line}_{ctx.start.column}"
        if not hasattr(self, 'contextos_processados'):
            self.contextos_processados = set()
        self.contextos_processados.add(ctx)
        
        # Processa a expressão do switch
        expr_result = self.processar_expressao(ctx.expressao())
        
        # Gera o switch
        if self.em_funcao:
            self.funcoes.append(f'\tswitch ({expr_result}) {{')
        elif self.em_procedimento:
            self.procedimentos.append(f'\tswitch ({expr_result}) {{')
        else:
            self.adicionar_codigo(f'switch ({expr_result}) {{', 1)
        
        # Processa cada seleção (case)
        for selecao in ctx.selecao():
            self.processar_selecao(selecao)
        
        # Processa o bloco senao (default) se existir
        if ctx.comandos():
            if self.em_funcao:
                self.funcoes.append('\t\tdefault:')
            elif self.em_procedimento:
                self.procedimentos.append('\t\tdefault:')
            else:
                self.adicionar_codigo('default:', 2)
            
            # Processa comandos do default
            for comando in ctx.comandos().comando():
                self.processar_comando_manual(comando)
            
            # Adiciona break para o default
            if self.em_funcao:
                self.funcoes.append('\t\t\tbreak;')
            elif self.em_procedimento:
                self.procedimentos.append('\t\t\tbreak;')
            else:
                self.adicionar_codigo('break;', 3)
        
        # Fecha o switch
        if self.em_funcao:
            self.funcoes.append('\t}')
        elif self.em_procedimento:
            self.procedimentos.append('\t}')
        else:
            self.adicionar_codigo('}', 1)
    
    def processar_selecao(self, selecao_ctx):
        """Processa uma seleção (case) do comando caso"""
        # Processa as constantes
        constantes = selecao_ctx.constantes()
        for constante in constantes.constante():
            if constante.NUM_INT():
                if len(constante.NUM_INT()) == 1:
                    # Constante simples: case N:
                    valor = constante.NUM_INT(0).getText()
                    if self.em_funcao:
                        self.funcoes.append(f'\t\tcase {valor}:')
                    elif self.em_procedimento:
                        self.procedimentos.append(f'\t\tcase {valor}:')
                    else:
                        self.adicionar_codigo(f'case {valor}:', 2)
                else:
                    # Faixa de valores: case N..M: (convertido para múltiplos cases)
                    inicio = int(constante.NUM_INT(0).getText())
                    fim = int(constante.NUM_INT(1).getText())
                    for valor in range(inicio, fim + 1):
                        if self.em_funcao:
                            self.funcoes.append(f'\t\tcase {valor}:')
                        elif self.em_procedimento:
                            self.procedimentos.append(f'\t\tcase {valor}:')
                        else:
                            self.adicionar_codigo(f'case {valor}:', 2)
        
        # Processa comandos da seleção
        for comando in selecao_ctx.comandos().comando():
            self.processar_comando_manual(comando)
        
        # Adiciona break
        if self.em_funcao:
            self.funcoes.append('\t\t\tbreak;')
        elif self.em_procedimento:
            self.procedimentos.append('\t\t\tbreak;')
        else:
            self.adicionar_codigo('break;', 3)
    
    def processar_comando_manual(self, comando_ctx):
        """Processa um comando individual manualmente"""
        if comando_ctx.escrita():
            self.processar_escrita_manual(comando_ctx.escrita())
        elif comando_ctx.leitura():
            self.processar_leitura_manual(comando_ctx.leitura())
        elif comando_ctx.atribuicao():
            self.processar_atribuicao_manual(comando_ctx.atribuicao())
        # Adicione outros tipos de comando conforme necessário
    
    def processar_escrita_manual(self, ctx):
        """Processa comando de escrita manualmente"""
        # Marca este contexto como processado
        ctx_id = (id(ctx), ctx.start.line, ctx.start.column)
        self.contextos_processados.add(ctx_id)
        
        expressoes = []
        formatos = []
        
        for expr_ctx in ctx.expressao():
            expr_text = self.processar_expressao(expr_ctx)
            
            # Verifica se é string literal
            if expr_text.startswith('"') and expr_text.endswith('"'):
                formatos.append('%s')
                expressoes.append(expr_text)
            # Verifica se é variável conhecida
            elif expr_text in self.tabela_simbolos:
                tipo = self.tabela_simbolos[expr_text]
                formato = self.obter_formato_printf(tipo)
                formatos.append(formato)
                expressoes.append(expr_text)
            # Verifica se é constante
            elif expr_text in self.constantes:
                valor = self.constantes[expr_text]
                if valor.isdigit():
                    formatos.append('%d')
                else:
                    formatos.append('%s')
                expressoes.append(valor)
            # Expressão genérica
            else:
                # Tenta determinar o tipo da expressão
                if expr_text.replace('.','').replace('-','').isdigit() and '.' in expr_text:
                    formatos.append('%f')
                    expressoes.append(expr_text)
                elif expr_text.replace('-','').isdigit():
                    formatos.append('%d')
                    expressoes.append(expr_text)
                else:
                    # Para expressões complexas, tenta inferir o tipo das variáveis
                    formato_expr = self.inferir_tipo_expressao(expr_text)
                    formatos.append(formato_expr)
                    expressoes.append(expr_text)
        
        formato_str = ''.join(formatos)
        if expressoes:
            params = ','.join(expressoes)
            linha = f'printf("{formato_str}",{params});'
        else:
            linha = f'printf("{formato_str}");'
        
        if self.em_funcao:
            self.funcoes.append(f'\t\t{linha}')
        elif self.em_procedimento:
            self.procedimentos.append(f'\t\t{linha}')
        else:
            self.adicionar_codigo(linha, 2)
    
    def processar_leitura_manual(self, ctx):
        """Processa comando de leitura manualmente"""
        for ident_ctx in ctx.lista_identificadores().children:
            if hasattr(ident_ctx, 'getText'):
                nome = ident_ctx.getText()
                if nome != ',':
                    tipo = self.tabela_simbolos.get(nome, 'int')
                    formato = self.obter_formato_printf(tipo)
                    
                    if tipo == 'char':
                        linha = f'fgets({nome}, 80, stdin);'
                        if self.em_funcao:
                            self.funcoes.append(f'\t\t{linha}')
                        elif self.em_procedimento:
                            self.procedimentos.append(f'\t\t{linha}')
                        else:
                            self.adicionar_codigo(linha, 2)
                        # Remove a quebra de linha do fgets
                        linha = f'{nome}[strcspn({nome}, "\\n")] = \'\\0\';'
                    else:
                        linha = f'scanf("{formato}",&{nome});'
                    
                    if self.em_funcao:
                        self.funcoes.append(f'\t\t{linha}')
                    elif self.em_procedimento:
                        self.procedimentos.append(f'\t\t{linha}')
                    else:
                        self.adicionar_codigo(linha, 2)
    
    def processar_atribuicao_manual(self, ctx):
        """Processa atribuição manualmente"""
        # Verifica se é ponteiro
        if ctx.getChildCount() >= 3 and ctx.getChild(0).getText() == '^':
            # É um ponteiro: ^IDENT <- expressao
            var = '*' + ctx.getChild(1).getText()
        else:
            # Atribuição normal
            var = ctx.children[0].getText()
            
        expr = self.processar_expressao(ctx.expressao())
        linha = f'{var} = {expr};'
        
        if self.em_funcao:
            self.funcoes.append(f'\t\t{linha}')
        elif self.em_procedimento:
            self.procedimentos.append(f'\t\t{linha}')
        else:
            self.adicionar_codigo(linha, 2)
    
    def exitComandose(self, ctx):
        """Não faz nada - processamento já realizado no enterComandose"""
        pass
    
    def enterComandopara(self, ctx):
        """Processa loop for"""
        var = ctx.IDENT().getText()
        inicio = self.processar_expressao(ctx.expressao(0))
        fim = self.processar_expressao(ctx.expressao(1))
        
        linha = f'for ({var} = {inicio}; {var} <= {fim}; {var}++) {{'
        
        if self.em_funcao:
            self.funcoes.append(f'\t{linha}')
        elif self.em_procedimento:
            self.procedimentos.append(f'\t{linha}')
        else:
            self.adicionar_codigo(linha, 1)
        
        self.nivel_escopo += 1
    
    def exitComandopara(self, ctx):
        """Finaliza loop for"""
        self.nivel_escopo -= 1
        
        if self.em_funcao:
            self.funcoes.append('\t}')
        elif self.em_procedimento:
            self.procedimentos.append('\t}')
        else:
            self.adicionar_codigo('}', 1)

    def enterComandoenquanto(self, ctx):
        """Processa loop while"""
        condicao = self.processar_expressao(ctx.expressao())
        linha = f'while ({condicao}) {{'
        
        if self.em_funcao:
            self.funcoes.append(f'\t{linha}')
        elif self.em_procedimento:
            self.procedimentos.append(f'\t{linha}')
        else:
            self.adicionar_codigo(linha, 1)
        
        self.nivel_escopo += 1
    
    def exitComandoenquanto(self, ctx):
        """Finaliza loop while"""
        self.nivel_escopo -= 1
        
        if self.em_funcao:
            self.funcoes.append('\t}')
        elif self.em_procedimento:
            self.procedimentos.append('\t}')
        else:
            self.adicionar_codigo('}', 1)

    def enterComandofaca(self, ctx):
        """Processa loop do-while"""
        if self.em_funcao:
            self.funcoes.append('\tdo {')
        elif self.em_procedimento:
            self.procedimentos.append('\tdo {')
        else:
            self.adicionar_codigo('do {', 1)
        
        self.nivel_escopo += 1
    
    def exitComandofaca(self, ctx):
        """Finaliza loop do-while"""
        self.nivel_escopo -= 1
        condicao = self.processar_expressao(ctx.expressao())
        
        # Para faca-ate, a condição já vem negada (nao (...)), então não negamos novamente
        if self.em_funcao:
            self.funcoes.append(f'\t}} while ({condicao});')
        elif self.em_procedimento:
            self.procedimentos.append(f'\t}} while ({condicao});')
        else:
            self.adicionar_codigo(f'}} while ({condicao});', 1)

    def processar_expressao(self, ctx):
        """Processa expressão e retorna código C"""
        if not ctx:
            return ""
        
        # Pega o texto original e faz algumas substituições
        texto = ctx.getText()
        
        # Não processa strings literais - só substitui operadores fora de strings
        if texto.startswith('"') and texto.endswith('"'):
            # É uma string literal, retorna sem modificações
            return texto
        
        # Substitui operadores lógicos de forma mais específica
        import re
        
        # Substitui "e" quando está entre operadores/números (não notação científica)
        # Padrão: qualquer caractere que não seja letra seguido de 'e' seguido de qualquer caractere que não seja dígito
        texto = re.sub(r'(\W)e(\W)', r'\1&&\2', texto)  # e entre não-letras
        texto = re.sub(r'^e(\W)', r'&&\1', texto)      # e no início
        texto = re.sub(r'(\W)e$', r'\1&&', texto)      # e no final
        
        # Casos específicos para números e operadores
        texto = re.sub(r'(\d)e(\d)', r'\1 && \2', texto)  # número e número
        texto = re.sub(r'(\))e(\()', r'\1 && \2', texto)  # ) e (
        texto = re.sub(r'(\))e(\w)', r'\1 && \2', texto)  # ) e palavra
        texto = re.sub(r'(\w)e(\()', r'\1 && \2', texto)  # palavra e (
        
        # Substitui ou e nao
        texto = re.sub(r'\bou\b', '||', texto)
        texto = re.sub(r'\bnao\b', '!', texto)
        
        # Outros operadores
        texto = texto.replace('<>', '!=')
        # Troca = por == apenas em comparações (não em atribuições como i=i+1)
        # Só substitui = por == quando está entre operandos (não assignment)
        import re
        texto = re.sub(r'(\w+)\s*=\s*(\w+)', r'\1 == \2', texto)  # var = var
        texto = re.sub(r'(\w+)\s*=\s*(\d+)', r'\1 == \2', texto)  # var = num
        texto = re.sub(r'(\d+)\s*=\s*(\w+)', r'\1 == \2', texto)  # num = var
        texto = re.sub(r'(\d+)\s*=\s*(\d+)', r'\1 == \2', texto)  # num = num
        texto = re.sub(r'\bverdadeiro\b', '1', texto)
        texto = re.sub(r'\bfalso\b', '0', texto)
        
        # Substitui constantes pelos seus valores
        for const_nome, const_valor in self.constantes.items():
            texto = re.sub(r'\b' + re.escape(const_nome) + r'\b', str(const_valor), texto)
        
        return texto

def main():
    if len(sys.argv) != 3:
        print("Uso: python compilador.py <arquivo_entrada> <arquivo_saida>")
        sys.exit(1)
    
    arquivo_entrada = sys.argv[1]
    arquivo_saida = sys.argv[2]
    
    try:
        # Lê o arquivo de entrada
        input_stream = FileStream(arquivo_entrada, encoding='utf-8')
        lexer = LALexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LAParser(token_stream)
        
        # Configura error listeners
        erro_listener = MeuErroListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(erro_listener)
        parser.removeErrorListeners()
        parser.addErrorListener(erro_listener)
        
        # Parse
        tree = parser.programa()
        
        # Se houve erros léxicos/sintáticos, escreve e termina
        if erro_listener.erros:
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                for erro in erro_listener.erros:
                    f.write(erro + '\n')
                f.write("Fim da compilacao\n")
            return
        
        # Análise semântica
        analisador_semantico = AnalisadorSemantico(token_stream)
        walker = ParseTreeWalker()
        walker.walk(analisador_semantico, tree)
        
        # Se houve erros semânticos, escreve e termina
        if analisador_semantico.erros:
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                for erro in analisador_semantico.erros:
                    f.write(erro + '\n')
                f.write("Fim da compilacao\n")
            return
        
        # Geração de código
        gerador = GeradorCodigo()
        walker = ParseTreeWalker()
        walker.walk(gerador, tree)
        
        # Escreve o código C no arquivo de saída
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            for linha in gerador.codigo:
                f.write(linha + '\n')
        
        # Se o arquivo de saída termina com .c, compila automaticamente para .out
        if arquivo_saida.endswith('.c'):
            # Usa rsplit para substituir apenas a última ocorrência de .c
            arquivo_executavel = arquivo_saida.rsplit('.c', 1)[0] + '.out'
            try:
                # Compila com gcc
                resultado = subprocess.run(['gcc', arquivo_saida, '-o', arquivo_executavel], 
                                         capture_output=True, text=True)
                if resultado.returncode != 0:
                    # Se houve erro na compilação, escreve erro no arquivo de saída
                    with open(arquivo_saida, 'w', encoding='utf-8') as f:
                        f.write(f"Erro na compilacao: {resultado.stderr}\n")
                        f.write("Fim da compilacao\n")
            except Exception as e:
                # Se gcc não está disponível, mantém apenas o código C
                pass
        
    except Exception as e:
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(f"Erro durante a compilacao: {str(e)}\n")
            f.write("Fim da compilacao\n")

if __name__ == '__main__':
    main()
