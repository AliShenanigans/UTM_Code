# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 13:46:40 2023

@author: ali_d

Fairness According to Airbus 

I used the global fairness metric from airbus i.e geometric/arithmetic mean


I used their paper to inform my 'cost' function.
Airbus paper has only delay time. 
I have added additional flight distance and a linear combination -
that enables operators to provide weights to indicate their preference for delay
time or additional journey length. (higher means it impacts more in a negative way)

I think the threshold values should be central and or based on user type....

The variables below will have a big impact on the outcome of the simulation
so we need to study what may be best placed there

I also like to think of 'cost' as an inconvenience score more than actual cost...
because that way its easier to factor in fairness tokens etc etc

"""
from math import *
from numpy import *
from matplotlib.pyplot import *
import random
'--- Input Variables ---'
Lua = 5000                    #maximum route length UA is capable of in m
Lr = 1000                     #length of desired flight plan in m
juice=Lua-Lr                  #remaining juice
n = 50                        #number of operators in sim
#consider factoring in a juice safety limit...
'--- Define Threshold Values ---'
Did = 5                       #Airbus uses 1
#Delay Indiference up to...
Dit=20                        #Delay becomes intolerable
#airbus doesnt consider length of route...
Lid = juice*(1/8)             #Legth indiference
# 1/3 of remaining juice in tank
Lit=juice*(1/3)               #extra length becomes intolerable
#--------------------------------
maxDelay = 60                 #max delay in random generator
maxReroute = 1000             #max additional journey length
#--------------------------------
def metricCost(Did,Dit,D):
    'output the cost function for a certain metric'
    a = sqrt(Did) - Did
    B = Dit + sqrt(Did)-Did-Dit**2
    if D< Did:
        P = sqrt(D)
    elif Did <= D <= Dit:
        P = D + a
    else: # D > Dit:
        P = D**2+B
    return P

def globalFairness(P):
    '''
    This is the airbus method
    P is a list of costs
    '''
    ep=1e-10 #small number to prevent multiply or divide my 0
    multiply=1
    n = len(P)
    add=0
    for i in P:
        #print(multiply)
        multiply = (multiply)*(i+ep)
        add += i+ep
        
    geometric_mean = (multiply)**(1/n)
    arithmetic_mean=add/n
    E = geometric_mean / arithmetic_mean
    return E
'''       
#below is only used to visualise the piecewise cost function shape
delayCosts=[]
reRouteCosts=[]
delay = arange(0,300) #0 to 3 hours 
addedLength=arange(0,0.5*Lua) #0 to half the ua's total capability

for i in delay:
    d = metricCost(Did,Dit,i)
    delayCosts.append(d)
for i in addedLength:
    l = metricCost(Lid,Lit,i)
    reRouteCosts.append(l)


#this makes plots for what the cost functions look like
fig, axs = subplots(2, 1)
subplot(2,1,1)
plot(delay,delayCosts, '-b')
xlabel('Ground delay in minutes')
ylabel('Cost to operator')
title('Delay cost function')

subplot(2,1,2)
plot(addedLength,reRouteCosts, '--r')    
xlabel('Additional length in meters')
ylabel('Cost to operator')
title('Additional distance cost function')
'''

'''
Below is all about generating random values
to substitude data in the mean time
'''
#generate metrics to test the outcomes...
#the values for delay in mins and extra distance travelled in meters
#must be fed from the sim data eventually
def randomDelay():
    #minutes to wait before take off
    mins = random.randint(0,maxDelay) #from no delay up to 2 hours
    return mins
    
def randomLength():
    #additional meters added to route 
    meters = random.randint(0,maxReroute)
    return meters

def RandomWeights():
    #Assuming users can provide preferences in terms of their preference
    #they will need to input a value between 0 and 1 for each metric
    #in the mean time use this to generate random values for their preference
    #Wlen + Wdel must always sum to 1.
    Wlen = round(random.random(),3) #length weight
    Wdel = round(1-Wlen,3)  #delay weight
    return Wlen, Wdel

'''
Below functions calculate individual fairness costs
'''
def fairnessCheck(Did,Dit,mins,Lid,Lit,meters):
    #cost of delay
    delayCost = metricCost(Did,Dit,mins)
    #cost of extra route length
    extraDistanceCost = metricCost(Lid,Lit,meters)
    return delayCost, extraDistanceCost

'''
Below combines percieved cost of additional journey length
vs ground delay based on user preference
'''

def TotalCost(Wlen,Wdel,delaycost,distancecost):
    combined = Wdel*delaycost+Wlen*distancecost
    return combined

def normalisedCost(totalCosts):
    maxc=max(totalCosts)
    minc=min(totalCosts)
    n_list=[] #list of normalised values
    for i in totalCosts:
        z=(i-minc)/(maxc-minc)
        n_list.append(round(z,3))
    return n_list
    

#--- Run Sims Here ---#
c=0
delayTimes=[]           #mins
extraDistances=[]       #meters
delayCosts=[]           #incured cost from delay
distanceCosts=[]        #incurred cost from reroute
totalCosts=[]           #linear combination of delay
                        # and reroute cost using user defined weights
C=[]

while c<n:
    c+=1
    #generate values for delay time 
    #delay mins
    mins =randomDelay()
    delayTimes.append(mins)
    #generate values for extra journey distance
    #extra journey length
    meters = randomLength()
    extraDistances.append(meters)
    #get the user preference for weight vs delay
    Wlen, Wdel = RandomWeights()
    
    #run fairnessCheck on individual
    delaycost, distancecost = fairnessCheck(Did,Dit,mins,Lid,Lit,meters)
    #collate result
    delayCosts.append(delaycost)
    distanceCosts.append(distancecost)
    
    #calculate combined cose based on user preference
    total=TotalCost(Wlen,Wdel,delaycost,distancecost) 
    totalCosts.append(round(total,3))
    
    #id of operator in list
    C.append(c)
    '''
    print('user is delayed ', mins, 'mins, with an additional', meters,' m travel distance')
    print('user weights are Wdelay=', Wdel, 'Wextralength= ',Wlen)
    print('user percieves cost as: ', total )
    print(' ')
    '''
    #--END LOOP---
    
#normalise combined cost  
normalised = normalisedCost(totalCosts)    
    
    
E_delay = globalFairness(delayCosts)
print('Global fairness is rated ',round(E_delay,3))
print('(0 is unfair, 1 is fair)')

subplots(1,2)    
subplot(1,2,1)
scatter(delayTimes,delayCosts)
xlabel('Mins delayed')
ylabel('Unweighted cost')
subplot(1,2,2)
scatter(extraDistances,distanceCosts)
xlabel('Extra meters')
ylabel('Unweighted cost')

fig,ax = subplots()
ax.scatter(delayTimes,normalised, color="pink", 
        marker="o")
ax.set_xlabel('Mins delayed (min)')

ax2=ax.twiny()
ax2.scatter(extraDistances,normalised, color="red", 
        marker="o")
ax2.set_xlabel('Extra meters travelled (m)')
ax.set_ylabel('Normalised percieved cost')