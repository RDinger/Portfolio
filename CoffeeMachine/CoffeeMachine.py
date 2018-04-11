# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 12:01:10 2018


Descr:
Command line program that mimics, very simply, a display screen of a coffeemachine.
Uses libraries time (declared within a method), AddSensor, and sys

@author: Remy H
CMorganaaa@gmail.com
"""
from sys import exit
from AddSensor import readMilk, updateMilk, readSugar, updateSugar

class CoffeeMachine:
    
    coffeeTypes = ("Americano","Cappachino","Espresso","Wiener Melange")

    def __init__(self,coffeeType, milk= False, sugar= False):

        while coffeeType != None:
            if coffeeType in CoffeeMachine.coffeeTypes:
                self.coffeeType = coffeeType
                break
            else:
                coffeeType=input('Kies uw koffie: ')

        if milk == None or self.coffeeType=='Cappachino':
            self.milk = False
        else:
            self.milk = milk
        if sugar == None:
            self.sugar = False
        else:
            self.sugar = sugar
        self.Display(coffeeType,sugar,milk)

    def checkAdditives(self,milk,sugar):

        if self.milk == True:
            self.enoughMilk=readMilk() 
            if self.enoughMilk == False: 
                print('Onvoldoende melk. Vul bij of waarschuw leverancier.')
                self.milk = False
        else:
            pass
        
        if self.sugar == True:
            self.enoughSugar=readSugar() #
            if self.enoughSugar == False: 
                print('Onvoldoende suiker. Vul bij of waarschuw leverancier.')
                self.Sugar = False
        else:
            pass

        self.promptUser()
        
    
    def promptUser(self):
       
        while True:
            prompt = input('Maak uw keuze: 1) start koffie, 2)annuleer keuze: ')
            if (prompt == '1') or (prompt == '2'):
                break
            
        if (prompt == '1'):
            self.Prepare()
        else:
            print('Bestelling geannuleerd.')
            exit()
        
    
    def Prepare(self):
        
        import time
        print('Voorbereiden van {}'.format(self.coffeeType))
        for i in range(1,11): 
            print('--',end='')
            #print('{}0% done...'.format(i))
            time.sleep(1)
        if self.milk == True:
            updateMilk(self.enoughMilk)
        if self.sugar == True:
            updateSugar(self.enoughSugar)
        print('\nNeem uw {}.'.format(self.coffeeType))
        exit()
        
    def Display(self,coffeeType,sugar,milk):
        
        print("\tUw keuze")
        print("-----------------------")
        print("Gekozen koffie: {}".format(self.coffeeType))
        print("Met suiker: {}".format(self.sugar))
        print("Met melk: {}".format(self.milk))
        self.checkAdditives(milk,sugar)


if __name__=="__main__":
    x=CoffeeMachine("Cappachino",True,True)

