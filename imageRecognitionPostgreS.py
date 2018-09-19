import psycopg2
import psycopg2.extras
import uuid
from datetime import datetime
from pprint import pprint
from getpass import getpass

class DatabaseConnection:
    def __init__(self):
        try:
            self.connection = psycopg2.connect("dbname=geevb user=geevb")
            self.cursor = self.connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
        except:
            pprint("Cannot connect")
    
    def insertNewUser(self, userEmail, userPassword):
        currentDate = (datetime.now()).strftime('%Y/%m/%d')
        self.cursor.execute('INSERT INTO public.users (email, password, dt_created, dt_last_login) VALUES (%s,%s,%s, %s) RETURNING user_id', (userEmail, userPassword, currentDate, None))
        insertedId = self.cursor.fetchone()[0]
        self.cursor.execute('INSERT INTO public.users_info (user_id, alias, rating, ranking, balance) VALUES (%s,%s,%s,%s,%s)', (insertedId, '', 0.0, 0, 0.0))
        self.connection.commit()

    def selectAllOnTable(self, tableName):
        self.cursor.execute('SELECT * FROM public.' + tableName)
        records = self.cursor.fetchall()
        print(records)
    
    def getUserByEmail(self, email):
        self.cursor.execute('SELECT * FROM public.USERS WHERE email LIKE \'' + email + '\'')
        return self.cursor.fetchone()

    def isRegistered(self, email, password):
        self.cursor.execute('SELECT * FROM public.USERS WHERE email=\'' + email + '\' AND password=\'' + str(password) + '\'')
        records = self.cursor.fetchall()
        return len(records) == 1

    def emailAlreadyRegistered(self, email):
        self.cursor.execute('SELECT * FROM public.USERS WHERE email LIKE \'' + email + '\'')
        records = self.cursor.fetchall()
        return len(records) == 1

    def updateDtLogin(self, email):
        currentDate = (datetime.now()).strftime('%Y/%m/%d')
        self.cursor.execute('UPDATE public.USERS SET dt_last_login=%s WHERE email=%s', (currentDate, email))
        self.connection.commit()
    
    def getUserInfoById(self, userId):
        self.cursor.execute('SELECT * FROM public.USERS_INFO WHERE user_id=%s', [userId])
        return self.cursor.fetchone()

    def changeAlias(self, userId, newAlias):
        self.cursor.execute('UPDATE public.USERS_INFO SET alias=%s WHERE user_id=%s', (newAlias, userId))
        self.connection.commit()
    
    def getCurrentAlias(self, userId):
        self.cursor.execute('SELECT * FROM public.USERS_INFO WHERE user_id=%s', [userId])
        response = self.cursor.fetchone()
        return response[4]

    def getCurrentPassword(self, userId):
        self.cursor.execute('SELECT * FROM public.USERS WHERE user_id=%s', [userId])
        response = self.cursor.fetchone()
        return response[1]

    def changePassword(self, userId, password):
        self.cursor.execute('UPDATE public.USERS SET password=%s WHERE user_id=%s', (password, userId))
        self.connection.commit()
    
    def deleteAccount(self, userId):
        self.cursor.execute('DELETE FROM public.USERS_INFO WHERE user_id=%s', [userId])
        self.cursor.execute('DELETE FROM public.USERS WHERE user_id=%s', [userId])
        self.connection.commit()

class view:
    def welcomeMessage(self):
        print("Welcome to the Database Prototype for Brand Image Recognition")

    def getNewUserEmail(self):
        return input('Please enter your e-mail: ')

    def changeUserPassword(self, oldPswr):
        oldPswr2 = getpass('Please confirm your old password: ')
        if(oldPswr == oldPswr2):
            while True:
                pswrd = getpass('Please enter your new password: ')
                pswrd2 = getpass('Please enter your new password once more: ')
                if(pswrd == pswrd2):
                    return pswrd
                else:
                    print('Passwords entered do not match, please enter again. \n')
        print('Password does not match. Closing.')


    def getNewUserPassword(self):
        while True:
            pswrd = getpass('Please enter your password: ')
            pswrd2 = getpass('Please enter your password once more: ')
            if(pswrd == pswrd2):
                return pswrd
            else:
                print('Passwords entered do not match, please enter again. \n')

    def showLoginOptions(self):
        resp = input('Would you like to: \n1) Login \n2) Create Account \n0) Exit \n\nR: ')
        return int(resp)
    
    def thanksForRegistering(self):
        print('\nThank you for registering!')
    
    def optionsMainMenu(self):
        print('What would you like to do next? \n1)Recognize something \n2)Change account info \n0) Exit')

    def showChangeAccOptions(self):
        resp = input('Would you like to: \n1) Change Alias \n2) Change password \n3) Delete account \n4) Go back\n\nR: ')
        return int(resp)
    
    def askForCredentials(self):
        email = input('Email: ')
        pswrd = getpass('Password: ')
        return(email, pswrd)
    
    def emailAlreadyUsed(self, email):
        print('This email ' + email + ' is in use already!')
        return input('Please enter another email: ')

    def showUserMainMenuOptions(self, loggedUserInfo):
        resp = input('\nWelcome! ' + loggedUserInfo.email + '\n\nWhat would you like to do next? \n1) Recognize something \n2) Change account info \n0) Exit \n\nR: ')
        return int(resp)
    
    def invalidUser(self):
        print('Email or Password is invalid! \nBye Bye!')

    def getNewAlias(self, currentAlias):
        print('Your current alias is: ' + str(currentAlias) + '!\n')
        return input('Would you like to change it to: ')

    def aliasChangeSucess(self):
        print('>>> Alias successfully changed! <<<')

    def passwordChangeSucess(self):
        print('>>> Password successfully changed! <<<')
    
    def confirmAccountDeletion(self):
        while True:
            resp = input('Are you sure you want to delete your account? ( Y or N ) \nR: ')
            if(resp == 'Y' or resp == 'N'):
                return resp
            print('Invalid option, try again!')

class loggedUser:
    def __init__(self, loggedEmail):
        self.db = DatabaseConnection()
        user = self.db.getUserByEmail(loggedEmail)
        self.email = loggedEmail
        self.db.updateDtLogin(loggedEmail)

        self.userId = user[0]
        userInfo = self.db.getUserInfoById(user[0])
        self.rating = userInfo[1]
        self.ranking = userInfo[2]
        self.balance = userInfo[3]
        self.alias = userInfo[4]

class editUserInfo:
    def __init__(self, loggedUserInfo, controller):
        self.ctr = controller
        self.ui = view()
        self.db = DatabaseConnection()
        self.userInfo = loggedUserInfo
        self.getChangeAccOptions()

    def getChangeAccOptions(self):
        option = self.ui.showChangeAccOptions()
        if option == 1:
            self.changeAlias(self.userInfo)
        elif option == 2:
            self.changePassword(self.userInfo)
        elif option == 3:
            self.deleteAccount(self.userInfo)
        self.ctr.userMainMenu(self.userInfo)

    def changeAlias(self, loggedUserInfo):
        oldAlias = self.db.getCurrentAlias(self.userInfo.userId)
        newAlias = self.ui.getNewAlias(oldAlias)
        self.db.changeAlias(self.userInfo.userId, newAlias)
        self.ui.aliasChangeSucess()
    
    def changePassword(self, loggedUserInfo):
        oldPswrd = self.db.getCurrentPassword(self.userInfo.userId)
        newPaswrd = self.ui.changeUserPassword(oldPswrd)
        if(newPaswrd):
            self.db.changePassword(self.userInfo.userId, newPaswrd)
            self.ui.passwordChangeSucess()

    def deleteAccount(self, loggedUserInfo):
        resp = self.ui.confirmAccountDeletion()
        if(resp == 'Y'):
            print('Deleting... Bye bye...')
            self.db.deleteAccount(self.userInfo.userId)
            exit()     
          
class controller:
    def __init__(self):
        self.ui = view()
        self.db = DatabaseConnection()

    def changePassword(self, loggedUserInfo):
        pass

    def userMainMenu(self, loggedUserInfo):
        option = self.ui.showUserMainMenuOptions(loggedUserInfo)
        if option == 1:
            print('Recognized, check Database to see more info!\n')
            pass
        elif option == 2:
            editUserInfo(loggedUserInfo, self)
        elif option == 0:
            exit()
        else:
            print('Invalid option, try again!\n')
            self.userMainMenu(loggedUserInfo)


    def loginMenu(self):
        self.ui.welcomeMessage()
        option = self.ui.showLoginOptions()
        if option == 1:
            credentials = self.ui.askForCredentials()
            if(self.db.isRegistered(credentials[0], credentials[1])):
                loggedUserInfo = loggedUser(credentials[0])
                self.userMainMenu(loggedUserInfo)
            else:
                self.ui.invalidUser()
        elif option == 2:
            email = self.ui.getNewUserEmail()
            while True:
                if(self.db.emailAlreadyRegistered(email)):
                    email = self.ui.emailAlreadyUsed(email)
                else:
                    break
            pswrd = self.ui.getNewUserPassword()
            self.db.insertNewUser(email, pswrd)
            self.ui.thanksForRegistering()
            self.loginMenu()
        elif option == 0:
            exit()
        else:
            print('Invalid option, try again!\n')
            self.loginMenu()

if __name__ == '__main__':
    ctrl = controller()
    ctrl.loginMenu()
