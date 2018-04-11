# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 15:51:09 2018

Descr:
Script to check the amount of additives for the coffeemachine (milk and sugar).
This mimics the sensors in the machine to monitor the level of milk and sugar.
Mimicking is done using two textfiles, milk.txt and sugar.txt with just one line each:
100 which represents the percentage off additives available.

@author: Remy H
CMorganaaa@gmail.com
"""
import os

MIN_AMOUNT_MILK = 20
MIN_AMOUNT_SUGAR = 20

MILKFILE = 'milk.txt'
SUGARFILE = 'sugar.txt'

def readMilk():
    if os.stat(MILKFILE).st_size == 0:
        return False
    else:
        with open (MILKFILE, 'r') as File:
            for row in File:
                currentValueMilk = int(row)
            if currentValueMilk < MIN_AMOUNT_MILK or currentValueMilk == 0:
                File.close()
                return False
            else:
                File.close()
                return currentValueMilk



def updateMilk(currentValue):

    with open (MILKFILE, 'w') as File:
        if not isinstance(currentValue,int):
            return False
        elif currentValue <= 0:
            return False
        else:
            newValue= currentValue - MIN_AMOUNT_MILK
            File.write(str(newValue))
    File.close()


def readSugar():

    # check size of file. If 0 (empty) pass False
    if os.stat(SUGARFILE).st_size == 0:
        return False

    # otherwise, open file and read content
    else:
        with open (SUGARFILE, 'r') as File:
            for row in File:
                currentValueSugar = int(row)

                # check if enough is available
                if currentValueSugar < MIN_AMOUNT_SUGAR or currentValueSugar == 0:
                    File.close()
                    return False
                else:
                    File.close()
                    return currentValueSugar


def updateSugar(currentValueSugar):

    with open (SUGARFILE, 'w') as File:
        if not isinstance(currentValueSugar,int):
            return False
        elif currentValueSugar <= 0:
            return False
        else:
            newValueSugar= currentValueSugar - MIN_AMOUNT_SUGAR
            File.write(str(newValueSugar))
    File.close()
