#!/usr/bin/python
# -*- coding: utf-8 -*-

from pathlib import Path
import sys
import csv


def verificar_argumentos():
    """Validação dos argumentos passados via comando"""
    arquivo_origem = Path(sys.argv[1])
    if len(sys.argv) != 3:
        sys.exit("Quantidade inválida de argumentos.")
    if not arquivo_origem.is_file():
        sys.exit("Arquivo de origem não encontrado.")
    else:
        return True


def definir_argumentos():
    if verificar_argumentos():
        global caminho_arquivo_entrada
        global caminho_arquivo_saida
        caminho_arquivo_entrada = sys.argv[1]
        caminho_arquivo_saida = sys.argv[2]
    else:
        sys.exit(1)


def converter_layout_para_csv():
    """ Coleta detalhes de um arquivo com formatação padronizada e cria um CSV com elas.
    Lê o arquivo de origem linha por linha retornando as informações específicas encontradas.
    Com as informações retornadas, escreve novas linhas no CSV de destino. """
    forma_lancamento = ''
    esc_cabecalho_inferior = True
    with open(getCaminhoArquivoEntrada()) as file:
        for linha in file:
            if linha[7:-233] == '0':
                inscricao_empresa, nome_empresa, nome_banco = ler_header_arquivo(linha)
                escrever_cabecalho_superior()
                escrever_detalhes_superior(inscricao_empresa, nome_empresa, nome_banco)
            elif linha[7:-233] == "1":
                forma_lancamento = ler_header_lote(linha)
            elif linha[7:-233] == "3":
                if esc_cabecalho_inferior:
                    escrever_cabecalho_inferior()
                    esc_cabecalho_inferior = False
                nome_favorecido, data_pagamento, valor_pagamento, seu_numero = ler_detalhes_arquivo(linha)
                escrever_detalhes_relatorio(nome_favorecido, data_pagamento, valor_pagamento,
                                            seu_numero, forma_lancamento)
            else:
                pass


def ler_header_arquivo(linha_atual):
    inscricao_empresa = linha_atual[18:-208]
    nome_empresa = linha_atual[72:-139]
    nome_banco = linha_atual[102:-109]
    return inscricao_empresa, nome_empresa, nome_banco


def ler_header_lote(linha_atual):
    forma_lancamento = linha_atual[11:-228]
    return forma_lancamento


def ler_detalhes_arquivo(linha_atual):
    nome_favorecido = linha_atual[43:-168]
    data_pagamento = linha_atual[93:-140]
    valor_pagamento = linha_atual[119:-107]
    seu_numero = linha_atual[73:-148]
    return nome_favorecido, data_pagamento, valor_pagamento, seu_numero


def escrever_cabecalho_superior():
    with open(getCaminhoArquivoSaida(), 'w+') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';')
        spamwriter.writerow(['Empresa responsável pelo Pagamento'] + ['Num. Inscrição'] + ['Nome do Banco'])


def escrever_detalhes_superior(inscricao_empresa, nome_empresa, nome_banco):
    inscrica_formatada = formatar_cnpj(inscricao_empresa)
    with open(getCaminhoArquivoSaida(), 'a+') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';')
        spamwriter.writerow([nome_empresa] + [inscrica_formatada] + [nome_banco])
        spamwriter.writerow('')


def escrever_cabecalho_inferior():
    with open(getCaminhoArquivoSaida(), 'a+') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';')
        spamwriter.writerow(['Nome Favorecido'] + ['Data de Pagamento'] + ['Valor da Pagamento'] + \
                            ['Seu Número'] + ['Forma de Lançamento'])


def escrever_detalhes_relatorio(nome_favorecido, data_pagamento, valor_pagamento, seu_numero, forma_lancamento):
    data_formatada = formatar_data(data_pagamento)
    valor_formatado = formatar_valor(valor_pagamento)
    with open(getCaminhoArquivoSaida(), 'a+') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';')
        spamwriter.writerow([nome_favorecido] + [data_formatada] + ["$" + valor_formatado] + \
                            [seu_numero] + [forma_lancamento])


def formatar_data(data):
    # Formatar data para o padrão dd/MM/aaaa
    return "%s/%s/%s" % (data[:2], data[2:4], data[4:])


def formatar_cnpj(cnpj):
    # Formatar CNPJ para o padrão XX.XXX.XXX/XXXX-XX
    return "%s.%s.%s/%s-%s" % (cnpj[0:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:14])


def formatar_valor(valor):
    """Formatar número recebido para xx,yy"""
    string_com_virgula = adicionar_virgula_casas_decimais(valor)
    string_com_ponto = trocar_virgula_por_ponto(string_com_virgula)
    numero_float = converter_string_para_float(string_com_ponto)
    string_float = converter_float_para_string(numero_float)
    numero_formatado = trocar_ponto_por_virgula(string_float)
    return numero_formatado


def converter_string_para_float(valor_string):
    return (float)(valor_string)


def converter_float_para_string(numero_float):
    return (str)(numero_float)


def trocar_ponto_por_virgula(valor_string):
    return valor_string.replace('.', ',')


def trocar_virgula_por_ponto(valor_string):
    return valor_string.replace(',', '.')


def adicionar_virgula_casas_decimais(valor_string):
    string_com_virgula = valor_string[:-2] + "," + valor_string[13:]
    return string_com_virgula


def getCaminhoArquivoEntrada():
    return caminho_arquivo_entrada


def getCaminhoArquivoSaida():
    return caminho_arquivo_saida


def main():
    definir_argumentos()
    converter_layout_para_csv()


if __name__ == "__main__":
    main()
