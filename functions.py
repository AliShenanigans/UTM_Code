# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 13:46:40 2023

@author: ali_d
"""
from functions import *
from math import *
from numpy import *
from matplotlib.pyplot import *
import random
import csv


'''
Next are the functions we need for our metrics:
'''
#---- INDIVIDUAL METRICS ----#
def stepPenaltyFunction(LTid, LTit,DTid, DTit,L,D, Cl, Cd):
    '''
    Return the penalty score for an individual...
    
    Tid = indifference threshold (centrally assigned)
    Tit = intollerable threshold (centrally assigned)
    v = value (extra distance (L) or delay time (D) allocated)
    Cl = user coefficient for length variance
    Cd = user defined coefficient for delay variance 
    construct the step Penalty function:
    '''
    #First determine length penalty
    #a and b are used to make the step function continuous at thresholds
    aL = sqrt(LTid) - LTid
    BL = LTit + sqrt(LTit)-LTid-(LTit)**2
    
    aD = sqrt(DTid) - DTid
    BD = DTit + sqrt(DTit)-DTid-(DTit)**2
    
    if L< LTid:
        'indifferent to length'
        PL = sqrt(L)
        if D< DTid:
            option ='indifferent to delay and length'
            PD = sqrt(D)
        elif DTid <= D <= DTit:
            option ='indifferent to length and not delay'
            PD = D + aD
        else:
            option ='indifferent to length and intollerable delay'
            PD = D**2+BD
        #print('PL=',PL, 'PD=', PD)
        
    elif LTid <= L <= LTit:
        'no longer indifferent to Length - but tollerable'
        PL = L + aL
        if D< DTid:
            option ='no longer indifferent to Length, indifferent to delay'
            PD = sqrt(D)
        elif DTid <= D <= DTit:
            option ='no longer indifferent to Length or delay'
            PD = D + aD
        else:
            option ='no longer indifferent to Length and intollerable delay'
            PD = D**2+BD
        #print('PL=',PL, 'PD=', PD)
    
    else:
        'intollerable length'
        PL = L**2 +BL
        if D< DTid:
            option ='intollerable Length, indifferent to delay'
            PD = sqrt(D)
        elif DTid <= D <= DTit:
            option ='intollerable Length, no longer indifferent delay'
            PD = D + aD
        else:
            option ='intollerable length and delay'
            PD = D**2+BD
        #print('PL=',PL, 'PD=', PD)
    #print(option, 'PL=',PL, 'PD=', PD)    
    #total penalty is a linear combination of the 2 variables
    
    P = Cd*PD + Cl*PL
    #print('Cd=', Cd, 'Cl=', Cl, 'P=',P)
    return round(P,3)

def saturatedPenalty(Cl,Cd,MADT,MAEL,LTid,LTit,DTid,DTit):
    '''
    Quantify the saturation penalty for an individual
    operator (i.e the penalty at which the operator wont fly)
    '''
    # MADT Max allowable delay time for given operator
    # MAEL Max allowable extra length to route for given operator
   
    #                          LTid, LTit,DTid, DTit,L,D, Cl, Cd
    Psat = stepPenaltyFunction(LTid, LTit,DTid, DTit,MAEL,MADT, Cl, Cd)
    return round(Psat,3)

def relativePenalty(Cl,Cd,delayTime, MADT,extraLen, MAEL,LTid,DTid,LTit,DTit,):
    '''
    Dimensionless penalty for each operator...
    This enables to compare different relative values for 
    the incurred penalty among different flights.
    Normalised using the saturation penalty Psat
    '''
    # MADT Max allowable delay time for given operator
    # MAEL Max allowable extra length to route for given operator
    
    #                Cl,Cd,MADT,MAEL,LTid,LTit,DTid,DTit
    Psat = saturatedPenalty(Cl,Cd,MADT,MAEL,LTid,LTit,DTid,DTit)
    #('Psat=', Psat)
    P = stepPenaltyFunction(LTid, LTit,DTid, DTit,extraLen,delayTime, Cl, Cd)
    y = ep=1e-10 #small number to prevent from going to 1 if saturated
    #print('P=', P)
    P_rel = P/(Psat+y)
    #y to stop division by zero ...
    #print('Prel=',P_rel)
    return round(P_rel,3)

def relativeUtility(P_rel):
    '''
    Where P_rel is the relative penalty...
    not a list...
    
    Dimensionless utility function -
    needs to be defined to provide a common context
    to compare the utility of different flights
    Utility functions are defined to measure the relative satisfaction
    '''
    phi= 1-P_rel
    U = 1-phi
    return U


#---- GLOBAL METRICS ----#
def globalSatisfaction(utilityScores):
    '''
    This satisfaction metric reflects the overall, average satisfaction
    level achieved for a set of n flights based on the utility function.
    The weakness of this metric is that the overall satisfaction of a set
    of two flights would be the same in cases where both flights 
    achieved the same level of utility as well as in situations where 
    one flight achieves a much higher utility than the other.
    Max satisfaction =1 

    '''
    n = len(utilityScores)
    sumU=sum(utilityScores)
    S = sumU/n
    return round(S,3)
    
def globalFairness(P, Psat):
    #P is a list of all the operator penalty scores
    #P_sat is a list of all the saturation scores
    multiply=1
    n = len(P)
    add=0
    y =1e-5
    
    for i in range(0,len(P)):
        phi = P[i]/(Psat[i]+y)
        ''''PHI MUST BE LESS THAN 1
        Otherwise the penalty is bigger
        than the saturation 
        SEE MADT and MAEL
        '''
        #print('P=',P[i],'Psat=',Psat[i])
        #print('Psat=',Psat[i], 'phi=',phi)
        #print('phi=',phi)
        u = (1-phi)
        #print('u=',u)
        #print(' ')
        multiply = (multiply)*(u)
        #print('multiply=',multiply)
        #print('multiply=',multiply)
        add += u
    #print(add, multiply)    
    geometric_mean = (multiply)**(1/n)
    #print('n=',n)
    arithmetic_mean=add/n
    #print('arithmetic_mean=',arithmetic_mean)
    #print('geometric_mean=',geometric_mean)
    
    F = round(geometric_mean / arithmetic_mean,3)
    return F, geometric_mean, arithmetic_mean


def globalEquity(P):
    '''
    This is the equity method
    P is a list of penalty values
    '''
    y =1e-5 #small number to prevent multiply or divide my 0
    multiply=1
    n = len(P)
    add=0
    
    for i in P:
        #print(multiply)
        multiply = (multiply)*(i+y)
        add += i+y
        
    geometric_mean = (multiply)**(1/n)
    arithmetic_mean=add/n
    E = round(geometric_mean / arithmetic_mean,3)
    return E, geometric_mean, arithmetic_mean

#---------------------------------------------------------------
'here are functions to help interpret data from plots'

def linearRegression(x,y):
    from sklearn.linear_model import LinearRegression
    #1d for now, would be good to make 2d
    x = array(x).reshape((-1, 1))
    y=array(y)
    model = LinearRegression()
    model.fit(x, y)
    model = LinearRegression().fit(x, y)
    r_sq = model.score(x, y)
    y_pred = model.predict(x)    
    return y_pred, round(r_sq,3)

#---------------------------------------------------------------   
