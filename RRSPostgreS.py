import psycopg2
import psycopg2.extras
import uuid
from datetime import datetime
from pprint import pprint
from getpass import getpass
import math
import operator

class DatabaseConnection:
    def __init__(self):
        try:
            self.connection = psycopg2.connect("dbname=geevb user=geevb")
            self.cursor = self.connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
        except:
            pprint("Cannot connect")

    def getHouses(self, answers):
        query = 'SELECT * FROM public.HOUSES WHERE '
        num_quartos = math.ceil(answers['numPessoas'] / 2)
        podePagar = "" if answers['podePagar'] == True else "OR (manutencao = %s)" % (False)
        search = "(ocupada = %s) AND ((num_quartos BETWEEN %i AND %i) OR (acessibilidade = %s) OR (mat_idade_idoso = %s) OR (mat_idade_crianca = %s) OR (mat_escolaridade = %s) %s)" % (False, 1, num_quartos, answers['haDeficientes'], answers['haIdosos'], answers['haCriancas'], answers['haEstudantes'], podePagar)
        query = query + search
        print(query)
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        return records

    def getHouseById(self, id):
        self.cursor.execute('SELECT * FROM public.HOUSES WHERE id=%i', [id])
        return self.cursor.fetchone()
          
class controller:
    def __init__(self):
        self.db = DatabaseConnection()

    def getAnswers(self):
        nome = input('Por favor, insira seu nome: ')
        numPessoasGrupo = input('Quantas pessoas estão no seu grupo? ')
        haIdosos = input('Possui pessoas idosas? S ou N ')
        haCriancas = input('Possui crianças? S ou N ')
        haEstudantes = input('Alguma pessoa do grupo está estudando atualmente? S ou N ')
        haDeficientes = input('Possui pessoas com algum tipo de deficiência? S ou N ')
        podePagar = input('O grupo teria a possibilidade de arcar com a manuntenção da residência? S ou N ')
        renda = input('Quanto de renda o grupo gera? ')
        localizacao = input('Por favor, insira o seu endereço ')
        return {
            'nome' : nome, 
            'numPessoas' : int(numPessoasGrupo), 
            'haIdosos' : (haIdosos == 'S'),
            'haCriancas' : (haCriancas == 'S'),
            'haEstudantes' : (haEstudantes == 'S'),
            'haDeficientes' : (haDeficientes == 'S'),
            'localizacao' : localizacao,
            'renda' : float(renda),
            'podePagar' : (podePagar == 'S')
        }
    
    def getPesoLocalizacaoEscola(self, localizacao):
        if(localizacao == 'a'):
            return 0.9

        if(localizacao == 'b'):
            return 0.5

        if(localizacao == 'c'):
            return 0.1

    def getPesoLocalizacaoSaude(self, localizacao):
        if(localizacao == 'c'):
            return 0.9

        if(localizacao == 'a'):
            return 0.5

        if(localizacao == 'b'):
            return 0.1

    def getPesoLocalizacaoOcupacao(self, localizacao):
        if(localizacao == 'b'):
            return 0.9

        if(localizacao == 'c'):
            return 0.5
            
        if(localizacao == 'a'):
            return 0.1
        

    def calculateMatchingValue(self, house, answers):
        peso_numQuartos = 0.8
        peso_manuntencao = 1
        peso_acessibilidade = 1
        mat_idade = 0.5
        mat_renda = 0.9
        mat_escolaridade = 0.5
        valueProximidadeEscola = self.getPesoLocalizacaoEscola(house['localizacao']) if (answers['haEstudantes']) else 0
        localizacao_escola = 0.5 * valueProximidadeEscola
        valueProximidadeOcupacao = self.getPesoLocalizacaoOcupacao(house['localizacao']) if (answers['renda'] > 0) else 0
        localizacao_ocupacao = 0.8 * valueProximidadeOcupacao
        valueProximidadeSaude = self.getPesoLocalizacaoSaude(house['localizacao']) if (answers['haIdosos'] or answers['haDeficientes']) else 0
        localizacao_saude = 0.6 * valueProximidadeSaude

        valManuntencao = (mat_renda * answers['renda']) if house['manutencao'] else 0

        return (
            (house['num_quartos'] * peso_numQuartos) + 
            (int(house['manutencao']) * peso_manuntencao) + 
            (int(house['acessibilidade']) * peso_acessibilidade) + 
            (int(house['mat_idade_idoso']) * mat_idade) + 
            (int(house['mat_idade_crianca']) * mat_idade) + 
            (int(house['mat_escolaridade']) * mat_escolaridade) +
            localizacao_escola +
            localizacao_ocupacao +
            localizacao_saude
            # (valManuntencao)
        )

    def getBestOption(self):
        answers = self.getAnswers()
        houses = self.db.getHouses(answers)
        idAndMatch = {}
        for house in houses:
            idAndMatch[house['id']] = self.calculateMatchingValue(house, answers)

        sortedMatches = sorted(idAndMatch.items(), key=operator.itemgetter(1), reverse=True)
        print(sortedMatches)
        return sortedMatches

if __name__ == '__main__':
    ctrl = controller()
    ctrl.getBestOption()
