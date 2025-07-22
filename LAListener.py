# Generated from LA.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .LAParser import LAParser
else:
    from LAParser import LAParser

# This class defines a complete listener for a parse tree produced by LAParser.
class LAListener(ParseTreeListener):

    # Enter a parse tree produced by LAParser#programa.
    def enterPrograma(self, ctx:LAParser.ProgramaContext):
        pass

    # Exit a parse tree produced by LAParser#programa.
    def exitPrograma(self, ctx:LAParser.ProgramaContext):
        pass


    # Enter a parse tree produced by LAParser#declaracoes_preliminares.
    def enterDeclaracoes_preliminares(self, ctx:LAParser.Declaracoes_preliminaresContext):
        pass

    # Exit a parse tree produced by LAParser#declaracoes_preliminares.
    def exitDeclaracoes_preliminares(self, ctx:LAParser.Declaracoes_preliminaresContext):
        pass


    # Enter a parse tree produced by LAParser#bloco_algoritmo.
    def enterBloco_algoritmo(self, ctx:LAParser.Bloco_algoritmoContext):
        pass

    # Exit a parse tree produced by LAParser#bloco_algoritmo.
    def exitBloco_algoritmo(self, ctx:LAParser.Bloco_algoritmoContext):
        pass


    # Enter a parse tree produced by LAParser#corpo_algoritmo.
    def enterCorpo_algoritmo(self, ctx:LAParser.Corpo_algoritmoContext):
        pass

    # Exit a parse tree produced by LAParser#corpo_algoritmo.
    def exitCorpo_algoritmo(self, ctx:LAParser.Corpo_algoritmoContext):
        pass


    # Enter a parse tree produced by LAParser#declaracao.
    def enterDeclaracao(self, ctx:LAParser.DeclaracaoContext):
        pass

    # Exit a parse tree produced by LAParser#declaracao.
    def exitDeclaracao(self, ctx:LAParser.DeclaracaoContext):
        pass


    # Enter a parse tree produced by LAParser#declaracao_funcao.
    def enterDeclaracao_funcao(self, ctx:LAParser.Declaracao_funcaoContext):
        pass

    # Exit a parse tree produced by LAParser#declaracao_funcao.
    def exitDeclaracao_funcao(self, ctx:LAParser.Declaracao_funcaoContext):
        pass


    # Enter a parse tree produced by LAParser#declaracao_constante.
    def enterDeclaracao_constante(self, ctx:LAParser.Declaracao_constanteContext):
        pass

    # Exit a parse tree produced by LAParser#declaracao_constante.
    def exitDeclaracao_constante(self, ctx:LAParser.Declaracao_constanteContext):
        pass


    # Enter a parse tree produced by LAParser#valor_constante.
    def enterValor_constante(self, ctx:LAParser.Valor_constanteContext):
        pass

    # Exit a parse tree produced by LAParser#valor_constante.
    def exitValor_constante(self, ctx:LAParser.Valor_constanteContext):
        pass


    # Enter a parse tree produced by LAParser#declaracao_procedimento.
    def enterDeclaracao_procedimento(self, ctx:LAParser.Declaracao_procedimentoContext):
        pass

    # Exit a parse tree produced by LAParser#declaracao_procedimento.
    def exitDeclaracao_procedimento(self, ctx:LAParser.Declaracao_procedimentoContext):
        pass


    # Enter a parse tree produced by LAParser#parametros.
    def enterParametros(self, ctx:LAParser.ParametrosContext):
        pass

    # Exit a parse tree produced by LAParser#parametros.
    def exitParametros(self, ctx:LAParser.ParametrosContext):
        pass


    # Enter a parse tree produced by LAParser#parametro.
    def enterParametro(self, ctx:LAParser.ParametroContext):
        pass

    # Exit a parse tree produced by LAParser#parametro.
    def exitParametro(self, ctx:LAParser.ParametroContext):
        pass


    # Enter a parse tree produced by LAParser#declaracoes_locais.
    def enterDeclaracoes_locais(self, ctx:LAParser.Declaracoes_locaisContext):
        pass

    # Exit a parse tree produced by LAParser#declaracoes_locais.
    def exitDeclaracoes_locais(self, ctx:LAParser.Declaracoes_locaisContext):
        pass


    # Enter a parse tree produced by LAParser#declaracao_tipo.
    def enterDeclaracao_tipo(self, ctx:LAParser.Declaracao_tipoContext):
        pass

    # Exit a parse tree produced by LAParser#declaracao_tipo.
    def exitDeclaracao_tipo(self, ctx:LAParser.Declaracao_tipoContext):
        pass


    # Enter a parse tree produced by LAParser#lista_variaveis.
    def enterLista_variaveis(self, ctx:LAParser.Lista_variaveisContext):
        pass

    # Exit a parse tree produced by LAParser#lista_variaveis.
    def exitLista_variaveis(self, ctx:LAParser.Lista_variaveisContext):
        pass


    # Enter a parse tree produced by LAParser#variavel.
    def enterVariavel(self, ctx:LAParser.VariavelContext):
        pass

    # Exit a parse tree produced by LAParser#variavel.
    def exitVariavel(self, ctx:LAParser.VariavelContext):
        pass


    # Enter a parse tree produced by LAParser#tipoPrimitivo.
    def enterTipoPrimitivo(self, ctx:LAParser.TipoPrimitivoContext):
        pass

    # Exit a parse tree produced by LAParser#tipoPrimitivo.
    def exitTipoPrimitivo(self, ctx:LAParser.TipoPrimitivoContext):
        pass


    # Enter a parse tree produced by LAParser#tipoIdentificado.
    def enterTipoIdentificado(self, ctx:LAParser.TipoIdentificadoContext):
        pass

    # Exit a parse tree produced by LAParser#tipoIdentificado.
    def exitTipoIdentificado(self, ctx:LAParser.TipoIdentificadoContext):
        pass


    # Enter a parse tree produced by LAParser#tipoRegistro.
    def enterTipoRegistro(self, ctx:LAParser.TipoRegistroContext):
        pass

    # Exit a parse tree produced by LAParser#tipoRegistro.
    def exitTipoRegistro(self, ctx:LAParser.TipoRegistroContext):
        pass


    # Enter a parse tree produced by LAParser#tipo_identificado.
    def enterTipo_identificado(self, ctx:LAParser.Tipo_identificadoContext):
        pass

    # Exit a parse tree produced by LAParser#tipo_identificado.
    def exitTipo_identificado(self, ctx:LAParser.Tipo_identificadoContext):
        pass


    # Enter a parse tree produced by LAParser#tipo_base.
    def enterTipo_base(self, ctx:LAParser.Tipo_baseContext):
        pass

    # Exit a parse tree produced by LAParser#tipo_base.
    def exitTipo_base(self, ctx:LAParser.Tipo_baseContext):
        pass


    # Enter a parse tree produced by LAParser#tipo_registro.
    def enterTipo_registro(self, ctx:LAParser.Tipo_registroContext):
        pass

    # Exit a parse tree produced by LAParser#tipo_registro.
    def exitTipo_registro(self, ctx:LAParser.Tipo_registroContext):
        pass


    # Enter a parse tree produced by LAParser#lista_campos.
    def enterLista_campos(self, ctx:LAParser.Lista_camposContext):
        pass

    # Exit a parse tree produced by LAParser#lista_campos.
    def exitLista_campos(self, ctx:LAParser.Lista_camposContext):
        pass


    # Enter a parse tree produced by LAParser#campo.
    def enterCampo(self, ctx:LAParser.CampoContext):
        pass

    # Exit a parse tree produced by LAParser#campo.
    def exitCampo(self, ctx:LAParser.CampoContext):
        pass


    # Enter a parse tree produced by LAParser#acesso_campo.
    def enterAcesso_campo(self, ctx:LAParser.Acesso_campoContext):
        pass

    # Exit a parse tree produced by LAParser#acesso_campo.
    def exitAcesso_campo(self, ctx:LAParser.Acesso_campoContext):
        pass


    # Enter a parse tree produced by LAParser#acesso_array.
    def enterAcesso_array(self, ctx:LAParser.Acesso_arrayContext):
        pass

    # Exit a parse tree produced by LAParser#acesso_array.
    def exitAcesso_array(self, ctx:LAParser.Acesso_arrayContext):
        pass


    # Enter a parse tree produced by LAParser#comando.
    def enterComando(self, ctx:LAParser.ComandoContext):
        pass

    # Exit a parse tree produced by LAParser#comando.
    def exitComando(self, ctx:LAParser.ComandoContext):
        pass


    # Enter a parse tree produced by LAParser#retorne.
    def enterRetorne(self, ctx:LAParser.RetorneContext):
        pass

    # Exit a parse tree produced by LAParser#retorne.
    def exitRetorne(self, ctx:LAParser.RetorneContext):
        pass


    # Enter a parse tree produced by LAParser#chamada_procedimento.
    def enterChamada_procedimento(self, ctx:LAParser.Chamada_procedimentoContext):
        pass

    # Exit a parse tree produced by LAParser#chamada_procedimento.
    def exitChamada_procedimento(self, ctx:LAParser.Chamada_procedimentoContext):
        pass


    # Enter a parse tree produced by LAParser#comandofaca.
    def enterComandofaca(self, ctx:LAParser.ComandofacaContext):
        pass

    # Exit a parse tree produced by LAParser#comandofaca.
    def exitComandofaca(self, ctx:LAParser.ComandofacaContext):
        pass


    # Enter a parse tree produced by LAParser#comandoenquanto.
    def enterComandoenquanto(self, ctx:LAParser.ComandoenquantoContext):
        pass

    # Exit a parse tree produced by LAParser#comandoenquanto.
    def exitComandoenquanto(self, ctx:LAParser.ComandoenquantoContext):
        pass


    # Enter a parse tree produced by LAParser#comandopara.
    def enterComandopara(self, ctx:LAParser.ComandoparaContext):
        pass

    # Exit a parse tree produced by LAParser#comandopara.
    def exitComandopara(self, ctx:LAParser.ComandoparaContext):
        pass


    # Enter a parse tree produced by LAParser#comandocaso.
    def enterComandocaso(self, ctx:LAParser.ComandocasoContext):
        pass

    # Exit a parse tree produced by LAParser#comandocaso.
    def exitComandocaso(self, ctx:LAParser.ComandocasoContext):
        pass


    # Enter a parse tree produced by LAParser#selecao.
    def enterSelecao(self, ctx:LAParser.SelecaoContext):
        pass

    # Exit a parse tree produced by LAParser#selecao.
    def exitSelecao(self, ctx:LAParser.SelecaoContext):
        pass


    # Enter a parse tree produced by LAParser#constantes.
    def enterConstantes(self, ctx:LAParser.ConstantesContext):
        pass

    # Exit a parse tree produced by LAParser#constantes.
    def exitConstantes(self, ctx:LAParser.ConstantesContext):
        pass


    # Enter a parse tree produced by LAParser#constante.
    def enterConstante(self, ctx:LAParser.ConstanteContext):
        pass

    # Exit a parse tree produced by LAParser#constante.
    def exitConstante(self, ctx:LAParser.ConstanteContext):
        pass


    # Enter a parse tree produced by LAParser#comandose.
    def enterComandose(self, ctx:LAParser.ComandoseContext):
        pass

    # Exit a parse tree produced by LAParser#comandose.
    def exitComandose(self, ctx:LAParser.ComandoseContext):
        pass


    # Enter a parse tree produced by LAParser#comandos.
    def enterComandos(self, ctx:LAParser.ComandosContext):
        pass

    # Exit a parse tree produced by LAParser#comandos.
    def exitComandos(self, ctx:LAParser.ComandosContext):
        pass


    # Enter a parse tree produced by LAParser#leitura.
    def enterLeitura(self, ctx:LAParser.LeituraContext):
        pass

    # Exit a parse tree produced by LAParser#leitura.
    def exitLeitura(self, ctx:LAParser.LeituraContext):
        pass


    # Enter a parse tree produced by LAParser#lista_identificadores.
    def enterLista_identificadores(self, ctx:LAParser.Lista_identificadoresContext):
        pass

    # Exit a parse tree produced by LAParser#lista_identificadores.
    def exitLista_identificadores(self, ctx:LAParser.Lista_identificadoresContext):
        pass


    # Enter a parse tree produced by LAParser#atribuicao.
    def enterAtribuicao(self, ctx:LAParser.AtribuicaoContext):
        pass

    # Exit a parse tree produced by LAParser#atribuicao.
    def exitAtribuicao(self, ctx:LAParser.AtribuicaoContext):
        pass


    # Enter a parse tree produced by LAParser#escrita.
    def enterEscrita(self, ctx:LAParser.EscritaContext):
        pass

    # Exit a parse tree produced by LAParser#escrita.
    def exitEscrita(self, ctx:LAParser.EscritaContext):
        pass


    # Enter a parse tree produced by LAParser#subliteral.
    def enterSubliteral(self, ctx:LAParser.SubliteralContext):
        pass

    # Exit a parse tree produced by LAParser#subliteral.
    def exitSubliteral(self, ctx:LAParser.SubliteralContext):
        pass


    # Enter a parse tree produced by LAParser#potencia.
    def enterPotencia(self, ctx:LAParser.PotenciaContext):
        pass

    # Exit a parse tree produced by LAParser#potencia.
    def exitPotencia(self, ctx:LAParser.PotenciaContext):
        pass


    # Enter a parse tree produced by LAParser#expressao.
    def enterExpressao(self, ctx:LAParser.ExpressaoContext):
        pass

    # Exit a parse tree produced by LAParser#expressao.
    def exitExpressao(self, ctx:LAParser.ExpressaoContext):
        pass


    # Enter a parse tree produced by LAParser#expressao_logica.
    def enterExpressao_logica(self, ctx:LAParser.Expressao_logicaContext):
        pass

    # Exit a parse tree produced by LAParser#expressao_logica.
    def exitExpressao_logica(self, ctx:LAParser.Expressao_logicaContext):
        pass


    # Enter a parse tree produced by LAParser#expressao_relacional.
    def enterExpressao_relacional(self, ctx:LAParser.Expressao_relacionalContext):
        pass

    # Exit a parse tree produced by LAParser#expressao_relacional.
    def exitExpressao_relacional(self, ctx:LAParser.Expressao_relacionalContext):
        pass


    # Enter a parse tree produced by LAParser#expressao_aritmetica.
    def enterExpressao_aritmetica(self, ctx:LAParser.Expressao_aritmeticaContext):
        pass

    # Exit a parse tree produced by LAParser#expressao_aritmetica.
    def exitExpressao_aritmetica(self, ctx:LAParser.Expressao_aritmeticaContext):
        pass


    # Enter a parse tree produced by LAParser#termo.
    def enterTermo(self, ctx:LAParser.TermoContext):
        pass

    # Exit a parse tree produced by LAParser#termo.
    def exitTermo(self, ctx:LAParser.TermoContext):
        pass


    # Enter a parse tree produced by LAParser#fator.
    def enterFator(self, ctx:LAParser.FatorContext):
        pass

    # Exit a parse tree produced by LAParser#fator.
    def exitFator(self, ctx:LAParser.FatorContext):
        pass


    # Enter a parse tree produced by LAParser#chamada_funcao.
    def enterChamada_funcao(self, ctx:LAParser.Chamada_funcaoContext):
        pass

    # Exit a parse tree produced by LAParser#chamada_funcao.
    def exitChamada_funcao(self, ctx:LAParser.Chamada_funcaoContext):
        pass


    # Enter a parse tree produced by LAParser#lista_expressao.
    def enterLista_expressao(self, ctx:LAParser.Lista_expressaoContext):
        pass

    # Exit a parse tree produced by LAParser#lista_expressao.
    def exitLista_expressao(self, ctx:LAParser.Lista_expressaoContext):
        pass


