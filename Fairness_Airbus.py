# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 13:46:40 2023

@author: ali_d

Fairness According to Airbus 

I used the global fairness metric from airbus i.e geometric/arithmetic mean


This code is informed by the PhD thesis that the Airbus paper uses..
The airbus paper only selected the equity  metric... 
But this is a better representation of overall fairness in my opinion

This method uses delay time and additional distance travelled as a result
of reroute / negotiation...

This version also enables you to select the penalty function;
be it the distance formula used in the Thesis reference or the 
step function employed by airbus
The latter needs centralised thresholds whereas the former
does not...
I think the threshold values should be central and or based on user type....


The sim needs to ingest the following variables to run: 
-length of desired flight plan flight plan in m
-Delay mins for allocated take off (mins)
-Additional length of allocated route (m)   
-User weight for delay
-User weight for additional route 

I also like to think of 'Penalty' as an inconvenience score more than actual Penalty...
because that way its easier to factor in fairness tokens etc etc

"""
from math import *
from numpy import *
from matplotlib.pyplot import *
import random
import csv

'--- Input Variables ---'     #note some of these will be hard coded
Lua = 5000                    #maximum route length UA is capable of in m
Lr = 1000                     #length of desired flight plan in m
juice=Lua-Lr                  #remaining juice
n = 100                        #number of operators in sim
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
def stepPenaltyFunction(Did,Dit,D):
    '''
    Did = distance indifference threshold
    Dit = distance intollerable threshold
    D = actual extra distance
    construct the step Penalty function for a certain metric
    i.e Airbus function
    '''
    a = sqrt(Did) - Did
    B = Dit + sqrt(Did)-Did-Dit**2
    if D< Did:
        P = sqrt(D)
    elif Did <= D <= Dit:
        P = D + a
    else: # D > Dit:
        P = D**2+B
    return P

def pythagPenaltyFunction(Wlen,Wdel,delayTime,extraLen):
    '''
    dimensionless penalty function:
    
    construct the Penalty function BOTH metrics at once
    Uses the Thesis example i.e distance function
    extraLen= extra meters in new route
    delayTime = mins delayed to take off
    
    '''
    if extraLen <= 0 and delayTime ==0:
        # if length is preference / shorter and no delay then no penalty
        P = 0
    else:
        P=sqrt(Wlen*(extraLen)**2+Wdel*(delayTime)**2)
        
    return P 

def saturatedPenalty(Wlen,Wdel,MADT,MAEL):
    'quantify worst penalty the operator would still fly'
    # MADT Max allowable delay time for given operator
    # MAEL Max allowable extra length to route for given operator
    Psat = pythagPenaltyFunction(Wlen,Wdel,MADT,MAEL)
    return Psat

def relativePenalty(Wlen,Wdel,delayTime, MADT,extraLen, MAEL):
    '''
    This enables to compare different relative values for 
    the incurred penalty among different flights.
    '''
    # MADT Max allowable delay time for given operator
    # MAEL Max allowable extra length to route for given operator
    Psat = saturatedPenalty(Wlen,Wdel,MADT,MAEL)
    P = pythagPenaltyFunction(Wlen,Wdel,delayTime,extraLen)
    y = ep=1e-10 #small number to prevent from going to 1 if saturated
    
    P_rel = P/(Psat+y)
    return P_rel

def relativeUtility(P_rel):
    '''
    Dimensionless utility function -
    needs to be defined to provide a common context
    to compare the utility of different flights
    Utility functions are defined to measure the relative satisfaction
    '''
    phi= 1-Prel
    U = 1-phi
    return U

def globalSatisfaction(utilityScores):
    '''
    This satisfaction metric reflects the overall, average satisfaction
    level achieved for a set of n flights based on the utility function.
    The weakness of this metric is that the overall satisfaction of a set
    of two flights would be the same in cases where both flights 
    achieved the same level of utility as well as in situations where 
    one flight achieves a much higher utility than the other.

    '''
    n = len(utilityScores)
    sumU=sum(utilityScored)
    S = sumU/n
    return S
    
def globalFairness(P, Psat):
    #P is a list of all the operator penalty scores
    #P_sat is a list of all the saturation scores
    multiply=1
    n = len(P)
    add=0
    y =1e-10
    
    for i in range(0,len(P)):
        phi = P[i]/(Psat[i]+y)
        #print('phi=',phi)
        u = (1-phi)
        multiply = (multiply)*(u)
        #print(multiply)
        add += u
        
    geometric_mean = (multiply)**(1/n)
    arithmetic_mean=add/n
    E = geometric_mean / arithmetic_mean
    return F, geometric_mean, arithmetic_mean


def globalEquity(P):
    '''
    This is the equity method
    P is a list of penalty values
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
    return E, geometric_mean, arithmetic_mean


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
Below functions calculate individual fairness penalty
'''
def fairnessCheck(Did,Dit,mins,Lid,Lit,meters):
    #penalty of delay
    delayPenaltyStep = stepPenaltyFunction(Did,Dit,mins)
    #penalty of extra route length
    extraDistancePenalty = stepPenaltyFunction(Lid,Lit,meters)
    return delayPenaltyStep, extraDistancePenalty

'''
Below combines percieved penalty of additional journey length
vs ground delay based on user preference
'''

def TotalPenalty(Wlen,Wdel,delay_penalty,distance_penalty):
    'linear combination of the 2 step function penalties (Airbus Method)'
    combined = Wdel*delay_penalty+Wlen*distance_penalty
    return combined

def normalisedPenalty(totalPenalty):
    maxc=max(totalPenalty)
    minc=min(totalPenalty)
    n_list=[] #list of normalised values
    for i in totalPenalty:
        z=(i-minc)/(maxc-minc)
        n_list.append(round(z,3))
    return n_list


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
    
#--- Run Sims Here ---#
c=0
delayTimes=[]            # mins
extraDistances=[]        # meters
delayPenaltySteps=[]     # incured Penalty from delay (step function method)
distancePenaltys=[]      # incurred Penalty from reroute (step function method)
totalPenaltys_step=[]    # linear combination of delay (step function method)
                         # and reroute Penalty using user defined weights 
totalPenaltys_pythag=[]  # total penalty when using pythag method
totalPenaltys_pythagN=[] # total normalised penalty socred when using pythag method
Wlens = []               # assigned weights for length 
Wdels = []               # assigned weights for delay 
C=[]

while c<n:
    c+=1
    #generate values 
    #-------------------------
    #weight
    Wlen, Wdel = RandomWeights()
    Wlens.append(Wlen)
    Wdels.append(Wdel)
    
    #generate values for delay time 
    #delay mins
    mins =randomDelay()
    delayTimes.append(mins)
    
    #generate values for extra journey distance
    #extra journey length
    meters = randomLength()
    extraDistances.append(meters) 
    #-------------------------
    
    #run fairnessCheck on individual
    #step penalty function
    delayPenaltyStep, distancePenalty = fairnessCheck(Did,Dit,mins,Lid,Lit,meters)    
    #pythag penalty function
    penaltyPythag = pythagPenaltyFunction(Wlen,Wdel,mins,meters)
    totalPenaltys_pythag.append(penaltyPythag)
    'normalised'
    penaltys_pythagN=relativePenalty(Wlen,Wdel,mins, 3*60,meters, 0.4*Lua)
    totalPenaltys_pythagN.append(penaltys_pythagN)
    
    #collate result
    delayPenaltySteps.append(delayPenaltyStep)
    distancePenaltys.append(distancePenalty)
    
    #calculate combined penalty based on user preference
    total=TotalPenalty(Wlen,Wdel,delayPenaltyStep,distancePenalty) 
    totalPenaltys_step.append(round(total,3))
    
    #id of operator in list
    C.append(c)
    '''
    print('user is delayed ', mins, 'mins, with an additional', meters,' m travel distance')
    print('user weights are Wdelay=', Wdel, 'Wextralength= ',Wlen)
    print('user percieves penalty as: ', total )
    print(' ')
    '''
    #--END LOOP---
    
#CALCULATE GLOBAL METRICS

#---------------- Equity ----------------#    
#normalise combined penalty(for step function linear combination method)
normalisedTotalStepPenalty = normalisedPenalty(totalPenaltys_step)    
normalised_delayPenaltyStep = normalisedPenalty(delayPenaltySteps)
normalised_distancePenaltyStep = normalisedPenalty(distancePenaltys)  
#---step function penalty function---    
E_step, geo_mean, ari_mean = globalEquity(totalPenaltys_step) #Unnormalised equity score with step function
#normalised scored give a different value... 
EN_step, geo_meanN, ari_meanN = globalEquity(normalisedTotalStepPenalty)
EN_delay, geo_meanN_d, ari_meanN_d = globalEquity(normalised_delayPenaltyStep)
EN_distance, geo_meanN_l, ari_meanN_l = globalEquity(normalised_distancePenaltyStep)  

#---pythag. function penalty function---
E_pythag, geometric_mean_pythag, arithmetic_mean_pythag = globalEquity(totalPenaltys_pythag)
E_pythagN, geometric_mean_pythagN, arithmetic_mean_pythagN = globalEquity(totalPenaltys_pythagN)

#---------------- Satisfaction ----------------#    



#---------------- Fairness ----------------#    

print('Global Equity is rated ',round(E_step,3))
#equal distribution of inconvenience/ Penalty
#print('Global normalised equity is rated ',round(EN_step,3)) #This is less good for some reason I think...
print('(0 is unequal distribution of the global penalty, 1 is equal distribution of the global penalty)')
print(' ')
#delay stats 
print('Total global delay incurred is', sum(delayTimes),' mins / ', round(sum(delayTimes)/60,3), 'hours')
print('Average global ground delay incurred is', mean(delayTimes),'mins')
print('The standard deviation in delay times is ', round(std(delayTimes),3), 'mins')
print(' ')
#added route length stats 
print('Total global addittional distance travelled is', sum(extraDistances), 'm / ', sum(extraDistances)/1000, 'km')
print('Average additional global re-route length incurred is', mean(extraDistances),'m')
print('The standard deviation in additional route length ', round(std(extraDistances),3), 'm')

#------------------------------------------------
#WRITE TO CSV  

header = ['Equity (step)', 'Equity (pythag.)', 'Satisfaction (step)', 
          'Satisfaction (pythag.)','Fairness (step)', 
          'Fairness (pythag.)', 'Total Global Delay (mins)',
          'Average Total Delay','Standard Deviation in Delay Incurred',
          'Total global additional route length', 
          'Total average additional route length', 
          'Standard deviation in additional route length' ]
#12 headers
data = [round(E_step,3), round(E_pythag,3), 'Satisfaction (step)', 
        'Satisfaction (pythag.)','Fairness (step)','Fairness (pythag.)',
        sum(delayTimes),mean(delayTimes),round(std(delayTimes),3),
        sum(extraDistances), mean(extraDistances),round(std(extraDistances))]
with open('data.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    # write the header
    writer.writerow(header)
    # write the data
    writer.writerow(data)

#NEED TO PUT THE ABOVE IN A LOOP TO GET BULK DATA

#-----------------------------------------------------------------------------
#----- from here is just graphs ----------


#-----------------------------------------------------------------------------
#      --VISUALISE PENALTY FUNCTIONS FOR N OPERATORS--
#below is only used to visualise the piecewise penalty function shape
delayPenaltyStep=[]         #airbus step penalty function (delay only)
reRoutePenaltyStep=[]       #airbus step penalty function (extra distance only)
totalPenaltyStep = []       #combination step penalty
totalPenaltyPythag_n=[]     #thesis combined penalty function
saturatedPenaltys=[]         #thesis saturated penalty scores 

delay=linspace(0,5*60,2500)  #0 to 5 hours 
addedLength=arange(0,0.5*Lua) #0 to half the ua's total capability
Wdelay=[]
Wlength=[]

for i in delay:
    d_s = stepPenaltyFunction(Did,Dit,i)
    delayPenaltyStep.append(d_s)
    
    wl,wd = RandomWeights()
    #Wdelay.append(1) #if unweighted
    #Wlength.append(1)
    Wdelay.append(wd)
    Wlength.append(wl)

    l_s = stepPenaltyFunction(Lid,Lit,i)
    reRoutePenaltyStep.append(l_s)


for i in range(0,len(delay)):
    #pythag method
    #print(Wlens[i],Wdels[i],delayTimes[i],extraDistances[i])
    penalty_p = pythagPenaltyFunction(Wlength[i],Wdelay[i],delay[i],addedLength[i])
    saturatedPenalty(Wlength[i],Wdelay[i],Lua,60*2) #set the max limits
    P_rel=relativePenalty(Wlength[i],Wdelay[i],delay[i], 60*2,addedLength[i], Lua*0.4)
    totalPenaltyPythag_n.append(P_rel)
    
    #combine the step function method with the same weightings...
    penalty_s = TotalPenalty(Wlength[i],Wdelay[i],delayPenaltyStep[i],reRoutePenaltyStep[i])
    totalPenaltyStep.append(penalty_s)
    
totalPenaltyStep_n=normalisedPenalty(totalPenaltyStep)

#------------------------------------------------------
# PINK AND BLUE ARE BASED ON THE NUMBER OF USERS IN THE AIRSPACE
#  Look at distribution of delay and additional distance 
#+ linear regressions
# BLUE GRAPH
'''
    The blue graph shows the incurred delay time and additional travel
    imposed on users and how this value changes with the number of users
    in the airspace. Its meaningless for now because the delay times 
    andextra distance travelled was generated randomally... BUT...    
    im putting this here because i expect delay time and extra distance
    travelled will get worse with more users in the airspace
'''
#delay time vs user id
subplots(1,2)    
suptitle('Incurred Delay and Additional Distance')
delayTime_R,r_time = linearRegression(C,delayTimes)
subplot(1,2,1)
scatter(C,delayTimes, color='cyan', label= 'Delay Time')
plot(C,delayTime_R, color='blue', label= f'Linear Reg. R= {r_time}')
legend( loc='upper left')
xlabel('User ID #')
ylabel('delay time (mins)')

#extra distance travelled vs user id
subplot(1,2,2)
delayDistance_R,r_distance = linearRegression(C,extraDistances)
scatter(C,extraDistances, color='cyan', label='Extra Distance')
plot(C,delayDistance_R, color='blue', label= f'Linear Reg. R= {r_time}')
legend( loc='upper left')
xlabel('User ID #')
ylabel('additional travel (m)')
#------------------------------------------------------
# Look at normalised Penaltys of delay and extra travel  
# + geometric and arithmetic mean of total Penalty function
# normalised delay time and total means (geo and ari)
# RED AND PINK GRAPH
'''
    The red and pink graph graph shows the incurred delay and 
    distance penalt score (using the step function method) 
    imposed on users. The top axis is meters and the bottom axis
    is mins. The graph also shows the arithmetic and geometric
    means... which are an indication of equality in this case.
    i.e it should indicate how the penalty scores and impacted by the
    2 metrics...
    red doesnt look right to me...
    
'''
fig,ax = subplots()
ax.scatter(delayTimes,normalised_delayPenaltyStep, color="purple", label='Delay Penalty Normalised',
        marker="o")
ax.set_xlabel('Mins delayed (min)')
ax.plot(delayTimes, [geo_meanN_d]*len(delayTimes), color='darkorchid', marker='*',label='Normalised Delay Time Geometric Mean')
ax.plot(delayTimes, [ari_meanN_d]*len(delayTimes), color='orchid', marker='.',label='Normalised Delay Time Arithmetic Mean')

#normalised extra distance travelled and total means (geo and ari)
ax2=ax.twiny()
ax2.scatter(extraDistances,normalised_distancePenaltyStep, color="red",label='Distance Penalty Normalised', 
        marker="o")

ax2.plot(extraDistances, [geo_meanN_l]*len(extraDistances), color='darkorange', marker='*',label='Normalised Extra Distance Geometric Mean')
ax2.plot(extraDistances, [ari_meanN_l]*len(extraDistances), color='tomato', marker='.',label='Normalised Extra Distance Arithmetic Mean')
ax2.set_xlabel('Extra meters travelled (m)')
ax.set_ylabel('Normalised percieved Penalty')

#below combines the legends from both axes
lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc=0)

#-----------------------------------------------------
#Visualise penalty functions with bulk data!

#this makes plots for what the penalty functions look like
# 1. STEP FUNCTION ALONE
fig, axs = subplots(2, 1)
suptitle('Not Normalised Step Penalty Functions')
axs[0].scatter(delay,delayPenaltyStep, color='lime')
axs[0].set_title('Delay Step Penalty')
axs[0].set_xlabel('Ground delay in minutes')
axs[0].set_ylabel('Penalty to operator')

axs[1].scatter(addedLength,reRoutePenaltyStep, color='forestgreen') 
axs[1].set_title('Extra Route Length Penalty')   
axs[1].set_xlabel('Additional length in meters')
axs[1].set_ylabel('Penalty to operator')

#----------------------
# 2. VIEW BOTH TOTAL NORMALISED FUNCTIONS 
fig, axs = subplots(2, 2)
suptitle('Normalised Step vs Pythag. Penalty Functions')
axs[0,0].scatter(delay,totalPenaltyPythag_n,  color='gold')
axs[0,0].set_xlabel('Ground delay in minutes')
axs[0,0].set_ylabel('Penalty to operator')

axs[1,0].scatter(addedLength,totalPenaltyPythag_n,  color='wheat')
axs[1,0].set_xlabel('Additional length in meters')
axs[1,0].set_ylabel('Penalty to operator')


axs[0,1].scatter(delay,totalPenaltyStep_n, color='lightcoral')
axs[0,1].set_ylabel('Ground delay in minutes')
axs[0,1].set_xlabel('Penalty to operator')


axs[1,1].scatter(addedLength,totalPenaltyStep_n, color='rosybrown')
axs[1,1].set_xlabel('Additional length in meters')
axs[1,1].set_ylabel('Penalty to operator')
#-----------------------------------------------------------------------------
