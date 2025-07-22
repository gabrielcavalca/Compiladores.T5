grammar LA;

// Lexer

// Palavras-chave
PALAVRA_CHAVE :
    'algoritmo' | 'fim_algoritmo' | 'declare' | 'leia' | 'escreva'
    | 'literal' | 'inteiro' | 'real' | 'logico' | 'constante'
    | 'verdadeiro' | 'falso' | 'se' | 'entao' | 'senao' | 'fim_se'
    | 'caso' | 'seja' | 'fim_caso' | 'para' | 'ate' | 'faca' | 'fim_para'
    | 'enquanto' | 'fim_enquanto' | 'registro' | 'fim_registro' | 'tipo'
    | 'procedimento' | 'fim_procedimento' | 'funcao' | 'fim_funcao'
    | 'retorne' | 'var' | 'e' | 'ou' | 'nao' | 'subLiteral' | 'pot' ;

// Literais
NUM_INT : [0-9]+ ;
NUM_REAL : [0-9]+ '.' [0-9]+ ;

CADEIA_NAO_FECHADA : '"' (~["\n])* ('\n'|EOF);
CADEIA : '"' (~["\n\r] | '""')* '"' ;

// Comentários

COMENTARIO : '{' ~[}\n]* '}' -> skip ;  
COMENTARIO_NAO_FECHADO : '{' ~[}\n]* ('\n'|EOF) ; 

// Espaços em branco
WS : [ \t\r\n]+ -> skip ;

// Símbolos e operadores pontuais
ASPAS : '"' ;
ABREPAR : '(' ;
FECHAPAR : ')' ;
VIRG : ',' ;
DOIS_PONTOS : ':' ;
ATRIBUICAO : '<-' ;
IGUAL: '=';
OP_RELACIONAL : '<=' | '>=' | '<>' | '<' | '>' ;
OP_ARITMETICO : '+' | '-' | '*' | '/' | '%' ;
PONTO : '.' ;
E_COMERCIAL : '&' ;
ABRE_COLCHETE : '[' ;
FECHA_COLCHETE : ']' ;
CIRCUNFLEXO : '^' ;
PONTOS : '..' ;

// Identificadores
IDENT : [a-zA-Z_] [a-zA-Z0-9_]* ;


CARACTERE_INVALIDO : [@#$!|] ;
ERRO : . ;



// Parser

programa
    : declaracoes_preliminares? bloco_algoritmo 'fim_algoritmo'
    ;

declaracoes_preliminares
    : (declaracao | declaracao_tipo | declaracao_procedimento | declaracao_funcao | declaracao_constante) * ;

bloco_algoritmo
    : 'algoritmo' corpo_algoritmo ;

corpo_algoritmo
    : (comando | declaracao | declaracao_constante | declaracao_tipo)* ;

declaracao
    : 'declare' lista_variaveis
    ;

declaracao_funcao
    : 'funcao' IDENT ABREPAR parametros? FECHAPAR ':' tipo_base (COMENTARIO)?
      declaracoes_locais?
      comandos
      'fim_funcao'
    ;

declaracao_constante
    : 'constante' IDENT ':' tipo_base IGUAL valor_constante (COMENTARIO)?
    ;

valor_constante
    : NUM_INT
    | NUM_REAL
    | CADEIA
    | 'verdadeiro'
    | 'falso'
    ;

declaracao_procedimento
    : 'procedimento' IDENT ABREPAR parametros? FECHAPAR (COMENTARIO)?
      declaracoes_locais?
      comandos
      'fim_procedimento'
    ;
parametros
    : parametro (',' parametro)*
    ;

parametro
    : ('var')? IDENT ':' (tipo_base | tipo_identificado)
    ;

declaracoes_locais
    : ('declare' lista_variaveis)+
    ;

declaracao_tipo
    : 'tipo' IDENT ':' (tipo_registro | tipo_identificado)
    ;

lista_variaveis
    : variavel (',' variavel)*
    ;

variavel
    : IDENT (ABRE_COLCHETE (NUM_INT | IDENT) FECHA_COLCHETE)? (',' IDENT (ABRE_COLCHETE (NUM_INT | IDENT) FECHA_COLCHETE)?)* ':' tipo
    ;

tipo
    : '^'? tipo_base     #tipoPrimitivo
    | '^'? tipo_identificado         #tipoIdentificado
    | tipo_registro      #tipoRegistro
    ;

tipo_identificado
    : '^'? IDENT
    ;

tipo_base
    : '^'? ('literal' | 'inteiro' | 'real' | 'logico')
    ;

tipo_registro
    : 'registro' lista_campos 'fim_registro'
    ;

lista_campos
    : campo (';'? campo)*  // ; opcional entre campos
    ;

campo
    : IDENT (',' IDENT)* ':' tipo_base
    ;

acesso_campo
    : IDENT ('.' IDENT)+
    ;

acesso_array
    : IDENT ABRE_COLCHETE expressao FECHA_COLCHETE
    ;

comando
    : atribuicao
    | leitura
    | escrita 
    | comandose
    | comandocaso
    | comandopara
    | comandoenquanto
    | comandofaca
    | chamada_procedimento
    | retorne;

retorne
    : 'retorne' expressao
    ;

chamada_procedimento
    : IDENT ABREPAR lista_expressao? FECHAPAR
    ;

comandofaca
    : 'faca' comandos 'ate' expressao
    ;

comandoenquanto
    : 'enquanto' expressao 'faca' comandos 'fim_enquanto'
    ;

comandopara
    : 'para' IDENT '<-' expressao 'ate' expressao 'faca' comandos 'fim_para'
    ;
    
comandocaso
    : 'caso' expressao 'seja' selecao* ('senao' comandos)? 'fim_caso';

selecao
    : constantes ':' comandos
    ;

constantes
    : constante (',' constante)*
    ;

constante
    : NUM_INT
    | NUM_INT PONTOS NUM_INT
    ;

comandose
    : 'se' expressao 'entao' comandos ('senao' comandos)? 'fim_se'
    ;

comandos
    : comando*
    ;

leitura
    : 'leia' '(' lista_identificadores ')'
    ;

lista_identificadores
    : (IDENT | acesso_campo | acesso_array) (',' (IDENT | acesso_campo | acesso_array))*
    ;

atribuicao
    : (IDENT | acesso_campo | acesso_array | CIRCUNFLEXO IDENT) ATRIBUICAO expressao ;

escrita
    : 'escreva' '(' expressao (',' expressao)* ')' ;

subliteral
    : 'subLiteral' ABREPAR expressao ',' NUM_INT ',' NUM_INT FECHAPAR
    ;

potencia
    : 'pot' ABREPAR expressao ',' expressao FECHAPAR
    ;

expressao
    : expressao_logica
    ;

expressao_logica
    : expressao_relacional ('e' expressao_relacional | 'ou' expressao_relacional)*
    ;

expressao_relacional
    : expressao_aritmetica ((OP_RELACIONAL | IGUAL) expressao_aritmetica)?
    ;

expressao_aritmetica
    : termo (( '+' | '-' ) termo)*
    ;

termo
    : fator (( '*' | '/' | '%' ) fator)*
    ;

fator
    : '-' fator                  
    | 'nao' fator       
    | '&' (IDENT | acesso_campo)         
    | ABREPAR expressao FECHAPAR
    | CIRCUNFLEXO IDENT
    | chamada_funcao
    | potencia
    | acesso_campo
    | acesso_array
    | IDENT
    | NUM_INT
    | NUM_REAL
    | CADEIA
    | subliteral
    | 'verdadeiro'
    | 'falso'
    ;

chamada_funcao
    : IDENT ABREPAR lista_expressao? FECHAPAR
    ;

lista_expressao
    : expressao (',' expressao)*
    ;
