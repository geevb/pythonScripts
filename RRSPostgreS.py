import psycopg2
import psycopg2.extras
import uuid
from datetime import datetime
from pprint import pprint
from getpass import getpass
import math

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
        search = "(num_quartos BETWEEN %i AND %i) AND (acessibilidade = %s) AND (mat_idade_idoso = %s)" % (1, num_quartos, answers['haDeficientes'], answers['haIdosos'])
        query = query + search
        print(query)
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        return records

    def getHouseById(self, id):
        self.cursor.execute('SELECT * FROM public.HOUSES WHERE id=%i', [id])
        return self.cursor.fetchone()

class view:
    def kek(self):
        print('kek')

class loggedUser:
    def __init__(self, loggedEmail):
        pass

class editUserInfo:
    def __init__(self, loggedUserInfo, controller):
        pass

    def deleteAccount(self, loggedUserInfo):
        print('kek') 
          
class controller:
    def __init__(self):
        self.ui = view()
        self.db = DatabaseConnection()

    def getAnswers(self):
        nome = input('Por favor, insira seu nome: ')
        numPessoasGrupo = input('Quantas pessoas estão no seu grupo? ')
        haIdosos = input('Possui pessoas idosas? S ou N ')
        haCriancas = input('Possui crianças? S ou N ')
        haEstudantes = input('Alguma pessoa do grupo está estudando atualmente? S ou N ')
        haDeficientes = input('Possui pessoas com algum tipo de deficiência? S ou N ')
        localizacao = input('Por favor, insira o seu endereço ')
        renda = input('Quanto de renda o grupo gera? ')
        return {
            'nome' : nome, 
            'numPessoas' : int(numPessoasGrupo), 
            'haIdosos' : (haIdosos == 'S'),
            'haCriancas' : (haCriancas == 'S'),
            'haEstudantes' : (haEstudantes == 'S'),
            'haDeficientes' : (haDeficientes == 'S'),
            'localizacao' : localizacao,
            'renda' : float(renda)
        }

    def calculateMatchingValue(self, house, answers):
        peso_numQuartos = 0.8
        peso_manuntencao = 1
        peso_acessibilidade = 1
        mat_idade = 0.5
        mat_renda = 0.9
        mat_escolaridade = 0.5
        localizacao_escola = 0.5
        localizacao_ocupacao = 0.8
        localizacao_saude = 0.6
        valManuntencao = (mat_renda * answers['renda']) if house['manutencao'] else 0

        return (
            (house['num_quartos'] * peso_numQuartos) + 
            (int(house['manutencao']) * peso_manuntencao) + 
            (int(house['acessibilidade']) * peso_acessibilidade) + 
            (int(house['mat_idade_idoso']) * mat_idade) + 
            (int(house['mat_idade_crianca']) * mat_idade) + 
            (int(house['mat_escolaridade']) * mat_escolaridade)
            # (valManuntencao)
        )

               


    def getBestOption(self):
        answers = self.getAnswers()
        houses = self.db.getHouses(answers)
        idAndMatch = {}
        for house in houses:
            idAndMatch[house['id']] = self.calculateMatchingValue(house, answers)
        
        print(idAndMatch)

        # matchinValue = self.calculateMatchingValue()


    def loginMenu(self):
        pass

if __name__ == '__main__':
    ctrl = controller()
    ctrl.getBestOption()
