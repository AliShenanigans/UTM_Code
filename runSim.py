# -*- coding: utf-8 -*-
"""
Run Fairness Sim with Random Values
"""
from functions import *
from math import *
from numpy import *
from matplotlib.pyplot import *
import random
import csv

'--- Input Variables ---'     
Lua = 1000                    #maximum route length UA is capable of in m (Length UA / Lua)
Lr = 500                      #prefered flight plan in m (Length route / Lr)
juice=Lua-Lr                  #remaining juice after desired flight
n = 50                        #number of operators in sim
#consider factoring in a juice safety limit...

'--- Define Threshold Values for Step Penalty Function Method---'
'Global - centrally assigned threshold values assigned to each user'
#Delay Period Thresholds (mins)
#INDIFFERENCE
Did_r  = 20          #Delay Indifference Recreational (mins)
Did_ce = 5           #Delay Indifference Commercial eCommerce (mins)
Did_cs = 15          #Delay Indifference Commercial Survey (mins)

#INTOLERABLE
Dit_r  = 20          #Delay Intolerable Recreational (mins)
Dit_ce = 10          #Delay Intolerable Commercial eCommerce (mins)
Dit_cs = 15          #Delay Intolerable Commercial Survey (mins)                      #Delay becomes intolerable

#Additional Length Incurred Thresholds (m)
#INDIFFERENCE
Lid_r  = juice*(0.05)    #Extra Length Indifference Recreational (meters)
Lid_ce = juice*(0.1)    #Extra Length Indifference Commercial eCommerce (meters)
Lid_cs = 10              #Extra Length Indifference Commercial Survey (meters)

#INTOLERABLE
Lit_r  = juice*(0.1)    #Extra Length Indifference Recreational (meters)
Lit_ce = juice*(0.2)    #Extra Length Indifference Commercial eCommerce (meters)
Lit_cs = 15              #Extra Length Indifference Commercial Survey (meters)

'--- User Preferences ---'
'''
Below will likely change with each operator in the real slim...
'''
'use max of intollerable delays + extra 5 mins'
#for now assume if in fairness, not calcelled
MADT_rec  = 60 
MADT_ecom = 60
MADT_sur  = 60
'use max of intollerable extra lengths + extra 50 meters'
# Max allowable extra length to route for given operator
MAEL_rec =  150
MAEL_ecom = 150
MAEL_sur = 150

'''
Coefficients must add to 1, they are for users to indicate their preferences...
They should be assigned to each user independently...(i.e input to script)
for now they are randomally generated
'''
Cl =  round(random.random(),3)   # User indicated Length Coefficient
Cd = round(1-Cl,3)                        # User indicated delay Coefficient

#--------------------------------
'''
RANDOM DATA GENERATOR TO TEST OUTPUT OF FAIRNESS
Below we generate random data because I didnt have
test data when I initially wrote this script... can eventually delete
as delay time and additional route length will be outputs of the DSS
'''
maxDelay = 60         #max delay in random generator
maxReroute = 150     #max additional journey length

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

'''
delayTimes and extraDistances will be the simulated data for extra
imposed delay to take off and extra distance travelled per operator
We will also generate some random values for the weighting
coefficients to run the sim...
'''
c=0                    #counter
delayTimes=[]          # mins (random data)
extraDistances=[]      # meters (random data)
'use the same delay tmies and extra distances for all user types'
# RECREATIONAL USERS
Cls_rec = []           # assigned weights for length (recreational users)
Cds_rec = []           # assigned weights for delay  (recreational users)
users_rec = []          # IDs for recreational users
# ECOMMERCE USERS
Cls_ecom = []           # assigned weights for length (eCommerce users)
Cds_ecom = []           # assigned weights for delay  (eCommerce users)
users_ecom = []          # IDs for recreational users
# SURVEY USERS
Cls_sur = []           # assigned weights for length (Survey users)
Cds_sur = []           # assigned weights for delay  (Survey users)
users_sur = []          # IDs for recreational users


#This while loop will only work if there are n of each user type.... 
#otherwise they each need their own times and distances...
# !! I EXPECT THIS WILL NEED TO CHANGE !!#
while c<n:
    #print(c)
    #generate value for delay times and reroute lengths
    dt=random.randint(0,maxDelay)
    dl=random.randint(0,maxReroute)
    delayTimes.append(dt)
    extraDistances.append(dl)
    
    #generate random values for weighting coefficients
    'use the same coefficients for all user types for now...'
    cl = round(random.random(),3)
    cd = round(1-cl,3)
    Cls_rec.append(cl)
    Cds_rec.append(cd)
    Cls_ecom.append(cl)
    Cds_ecom.append(cd)
    Cls_sur.append(cl)
    Cds_sur.append(cd)
    
    #save operator ID and move to next operator
    'Assume same number of each user type in this sim'
    users_rec.append(c)
    users_ecom.append(c)
    users_sur.append(c)
    
    c+=1
'we now have a set of data to simulate....'

#----------------------------
'''
Next let's assemble the functions for each operator 
'''
#Recreational Users
Penalty_rec=[]    # list of all the operator penalty scored
Psat_rec = []     # list of all the operator saturation penalty values
Prel_rec = []     # list of all the normalised penalty scored (relative/dimensionless)
Urel_rec = []     # list of all the normalised relativity scores of the users


#eCommerce Users
Penalty_ecom=[]    # list of all the operator penalty scored
Psat_ecom = []     # list of all the operator saturation penalty values
Prel_ecom = []     # list of all the normalised penalty scored (relative/dimensionless)
Urel_ecom = []     # list of all the normalised relativity scores of the users
#Survey Users
Penalty_sur=[]    # list of all the operator penalty scored
Psat_sur = []     # list of all the operator saturation penalty values
Prel_sur = []     # list of all the normalised penalty scored (relative/dimensionless)
Urel_sur = []     # list of all the normalised relativity scores of the users


'''
The script is split up to allow a different number of each user...
Below we determine the penalty, saturation score, relative penalty and
relative utility for each user in the sim...
'''
'Recreational users' 
for i in range(0,len(users_rec)):
    #Penalty associated with recreational users
    penalty_rec = stepPenaltyFunction(Lid_r, Lit_r,Did_r, Dit_r,extraDistances[i],delayTimes[i], Cls_rec[i], Cds_rec[i])
    Penalty_rec.append(penalty_rec)
    
    #Saturation penalty for the recreational user:
    psat_rec= saturatedPenalty(Cls_rec[i],Cds_rec[i],MADT_rec,MAEL_rec,Lid_r,Lit_r,Did_r,Dit_r)
    Psat_rec.append(psat_rec)
    
    #Relative (Dimensionless) penalty for the recreational user:
    prel_rec = relativePenalty(Cls_rec[i],Cds_rec[i],delayTimes[i], MADT_rec,extraDistances[i], MAEL_rec,Lid_r,Did_r,Lit_r,Dit_r)
    Prel_rec.append(prel_rec)
    
    #Relative (Dimensionless) utility for the recreational user:
    urel_rec = relativeUtility(prel_rec)
    Urel_rec.append(urel_rec)


'eComerce users'    
for i in range(0,len(users_ecom)):    
    #Penalty associated with eCommerce operators
    penalty_ecom = stepPenaltyFunction(Lid_ce, Lit_ce,Did_ce, Dit_ce,extraDistances[i],delayTimes[i], Cls_ecom[i], Cds_ecom[i])
    Penalty_ecom.append(penalty_ecom)
        
    #Saturation penalty for the eCommerce operator:
    psat_ecom= saturatedPenalty(Cls_ecom[i],Cds_ecom[i],MADT_ecom,MAEL_ecom,Lid_ce,Lit_ce,Lid_ce,Dit_ce)
    Psat_ecom.append(psat_ecom)
    
    #Relative (Dimensionless) penalty for the eCommerce operator:
    prel_ecom = relativePenalty(Cls_ecom[i],Cds_ecom[i],delayTimes[i], MADT_ecom,extraDistances[i], MAEL_ecom,Lid_ce,Did_ce,Lit_ce,Dit_ce)
    Prel_ecom.append(prel_ecom)
    
    #Relative (Dimensionless) utility for the eCommerce operator:
    urel_ecom = relativeUtility(prel_ecom)
    Urel_ecom.append(urel_ecom)

'Survey users'       
for i in range(0,len(users_sur)): 
    #Penalty associated with survey operators 
    penalty_sur = stepPenaltyFunction(Lid_cs, Lit_cs,Did_cs, Dit_cs, extraDistances[i],delayTimes[i], Cls_sur[i], Cds_sur[i])
    Penalty_sur.append(penalty_sur)
    
    #Saturation penalty for the survey operator:
    psat_sur= saturatedPenalty(Cls_sur[i],Cds_sur[i],MADT_sur,MAEL_sur,Lid_cs,Lit_cs,Did_cs,Dit_cs)
    Psat_sur.append(psat_sur)
    
    'because the survey is so sensitive to small re-route distances... this number is not always between 0-1'
    #Relative (Dimensionless) penalty for the survey operator:
    prel_sur = relativePenalty(Cls_sur[i],Cds_sur[i],delayTimes[i], MADT_sur,extraDistances[i], MAEL_sur,Lid_cs,Did_cs,Lit_cs,Dit_cs)
    Prel_sur.append(prel_sur)

    #Relative (Dimensionless) utility for the eCommerce operator:
    urel_sur = relativeUtility(prel_sur)
    Urel_sur.append(urel_sur)


'''
Now we get to the global scoring!
'''
def calcGlobalMetrics():
    #---------------- Satisfaction ----------------#    
    '''
    Global Satisfaction is defined as the arithmetic mean of the global relative utility for a set of n operators / flights.
    The weakness of this metric stems from the arithmetic mean – that is:
    overall satisfaction of a set of two flights would be the same 
    in the case where two flights achieved the same level of utility 
    vs if one flight achieved a much higher utility than the other.
    Maximum Global Satisfaction = 1
    '''
    Sat_rec=globalSatisfaction(Urel_rec)   #satisfaction of Survey Operators
    Sat_ecom=globalSatisfaction(Urel_ecom) #satisfaction of eCommerce Operators
    Sat_sur=globalSatisfaction(Urel_sur)   #satisfaction of Survey Operators
    #---------------- Fairness ----------------#    
    '''
    THE RELATIVE METRIC - i.e calculated using normalised penalty
    The fairness metric is minimal when the relative penalty values are
    maximally spread out (no excessive penalty to few operators). In that 
    case, fairness goes towards the value zero.
    The metric is mostly concerned with describing how close 
    additional incurred penalties are to the saturation values globally. 

    1 when relative penalty is around the same (fair)
    0 when there is a big spread in relative penalty
    '''
    Fair_rec, gmf_rec, amf_rec = globalFairness(Penalty_rec, Psat_rec)
    Fair_ecom, gmf_ecom, amf_ecom  = globalFairness(Penalty_ecom, Psat_ecom)
    Fair_sur, gmf_sur, amf_sur  = globalFairness(Penalty_sur, Psat_sur)
    #---------------- Equity ----------------#    
    '''
    Calculated with un-normalised penalty
    This metric measures to what extent the incurred global penalty 
    has been equally distributed i.e has everyone been disadvantaged equally? 

    Note that equity can be considered as independent from fairness. 
    This metric is maximal (1) when the incurred global penalty has been
    equally distributed amongst all operators 
    (i.e everyone is equally inconvenienced). 
 
    unlike fairness, the equity metric cannot account for the same size penalty
    having a more or less impact on different operators...
    (THIS IS THE METRIC AIRBUS USE FOR FAIRNESS FYI)
 
    0 is unequal distribution of penalty
    1 is equal distribution of penalty
    '''
    E_rec, gme_rec, ame_rec = globalEquity(Penalty_rec)
    E_ecom, gme_ecom, ame_ecom = globalEquity(Penalty_ecom)
    E_sur, gme_sur, ame_sur = globalEquity(Penalty_sur)
    
    return Sat_rec, Sat_ecom, Sat_sur, Fair_rec, Fair_ecom, Fair_sur, E_rec, E_ecom, E_sur, gme_rec,gmf_rec,gme_ecom, gme_sur, gmf_rec, gmf_ecom, gmf_sur, ame_rec,amf_rec,ame_ecom, ame_sur, amf_rec, amf_ecom, amf_sur


Sat_rec, Sat_ecom, Sat_sur, Fair_rec, Fair_ecom, Fair_sur, E_rec, E_ecom, E_sur, gme_rec,gmf_rec,gme_ecom, gme_sur, gmf_rec, gmf_recom, gmf_sur, ame_rec,amf_rec,ame_ecom, ame_sur, amf_rec, amf_recom, amf_sur = calcGlobalMetrics()
#------------------------------------------------
#WRITE TO CSV  
import pandas as pd
header = ['Equity (rec)', 'Equity (ecom)','Equity (sur)', 'Satisfaction (rec)', 
          'Satisfaction (ecom.)','Satisfaction (sur)','Fairness (rec)', 
          'Fairness (ecom)','Fairness (sur)', 'Total Global Delay (mins)',
          'Average Total Delay','Standard Deviation in Delay Incurred',
          'Total global additional route length', 
          'Total average additional route length', 
          'Standard deviation in additional route length' ]
#12 headers
data = [E_rec,E_ecom,E_sur, Sat_rec, Sat_ecom, Sat_sur,
        Fair_rec,Fair_ecom,Fair_sur,
        sum(delayTimes),mean(delayTimes),round(std(delayTimes),3),
        sum(extraDistances), mean(extraDistances),round(std(extraDistances))]


with open('data.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    # write the header
    writer.writerow(header)
    # write the data
    writer.writerow(data)

#--------------------------------------\\---------------------------------------#
#                              from here is graphs 
#--------------------------------------\\---------------------------------------#
                        
#   below is only used to visualise the piecewise penalty function shape
#                                !! MADE UP DATA !!

def viewStepRecGraph():
    
    
    #make random data points
    x = linspace(0,60,100) #time     (d)
    y = linspace(0,150,100)  #distance (l)
    
    #create empty lists
    xs=[]
    ys=[]
    z_rec = []
    z_ecom = []
    z_sur = []
    
    
    for i in range(0,len(x)):
        for j in range(0,len(y)):
            xs.append(x[i])
            ys.append(y[j])
    

    Cl=Cd=0.5
    for i in range(0,len(xs)):
        #(LTid, LTit,DTid, DTit,L,D, Cl, Cd):
            penalty_rec= stepPenaltyFunction(Lid_r, Lit_r,Did_r, Dit_r,ys[i],xs[i], Cl, Cd)
            penalty_ecom= stepPenaltyFunction(Lid_ce, Lit_ce,Did_ce, Dit_ce,ys[i],xs[i], Cl, Cd)
            penalty_sur = stepPenaltyFunction(Lid_cs, Lit_cs,Did_cs, Dit_cs,ys[i],xs[i], Cl, Cd)
            
            z_rec.append(penalty_rec)
            z_ecom.append(penalty_ecom)
            z_sur.append(penalty_sur)
            
    '''
    ax.scatter(xs, ys, z_sur, label='Survey', alpha=0.4, s=0.1, color='peachpuff')
    ax.scatter(xs, ys, z_rec, label='Recreational', alpha=0.5, s=0.1, color='salmon')
    ax.scatter(xs, ys, z_ecom, label = 'eCommerce', alpha=0.6, s=0.1, color='orangered')
    ax.view_init(10,angle)
    ax.set_xlabel('Time Delayed (mins)')
    ax.set_ylabel('Extra Distance (meters)')
    ax.set_zlabel('Percieved Penalty (dimensionless)')
    '''    
    
    fig, ax = subplots(1,2,figsize=(10,10),subplot_kw=dict(projection='3d'))
    
    sc1 = ax[0].scatter(xs, ys, z_sur, label='Survey', alpha=0.9, s=0.1, color='pink')
    sc2 = ax[0].scatter(xs, ys, z_rec, label='Recreational', alpha=0.5, s=0.2, color='salmon')
    sc3 = ax[0].scatter(xs, ys, z_ecom, label = 'eCommerce', alpha=0.6, s=0.3, color='orangered')
    ax[0].view_init(10,25)
    ax[0].set_title('Step Functions View 1')
    ax[0].legend( loc='upper left')
    
    sc4 = ax[1].scatter(xs, ys, z_sur, label='Survey', s=0.1, color='pink')
    sc5 = ax[1].scatter(xs, ys, z_rec, label='Recreational', s=0.2, color='salmon')
    s6 = ax[1].scatter(xs, ys, z_ecom, label = 'eCommerce', s=0.3, color='orangered')
    ax[1].view_init(10,110)
    ax[1].set_title('Step Functions View 2')
    ax[1].legend( loc='upper left')


    '''
    #2D PLOTs
    fig2=figure()
    subplots(1,2) 
    suptitle('Side View Step Functions ')
    subplot(1,2,1)
    scatter(xs, z_rec)
    xlabel('Time Delayed (mins)')
    ylabel('Relative Percieved Penalty')

    subplot(1,2,2)
    scatter(ys, z_rec)
    xlabel('Extra Distance (meters)')
    ylabel('Relative Percieved Penalty')
    '''

'unhash below to see the step function shape (example is recreational users)'
viewStepRecGraph()

#------------------------------------------------------

def viewRegressions():
    #------------------------------------------------------
    # RAINBOW GRAPH IS BASED ON THE NUMBER OF USERS IN THE AIRSPACE
    #  Look at distribution of delay and additional distance 
    #+ linear regressions

    """
        The blue graph shows the incurred delay time and additional travel
        imposed on users and how this value changes with the number of users
        in the airspace. Its meaningless for now because the delay times 
        andextra distance travelled was generated randomally... BUT...    
        im putting this here because i expect delay time and extra distance
        travelled will get worse with more users in the airspace
        """

    #delay time vs user id
    subplots(1,2)  
    suptitle('Change in Delay and Route Length with Airspace Density for Recreational Users')
    delayTime_R,r_time = linearRegression(users_rec,delayTimes)
    subplot(1,2,1)
    scatter(users_rec,delayTimes, color='cyan', label= 'Delay Time')
    plot(users_rec,delayTime_R, color='blue', label= f'Linear Reg. R= {r_time}')
    legend( loc='upper left')
    xlabel('User ID #')
    ylabel('delay time (mins)')

    #extra distance travelled vs user id
    subplot(1,2,2)
    delayDistance_R,r_distance = linearRegression(users_rec,extraDistances)
    scatter(users_rec,extraDistances, color='cyan', label='Extra Distance')
    plot(users_rec,delayDistance_R, color='blue', label= f'Linear Reg. R= {r_time}')
    legend( loc='upper left')
    xlabel('User ID #')
    ylabel('additional travel (m)')
'unhash below to see regressions for recreational users'
#viewRegressions()


#------------------------------------------------------


def fairVSequal():
    # Look at normalised Penaltys of delay and extra travel  
    # + geometric and arithmetic mean of total Penalty function
    # normalised delay time and total means (geo and ari)
    # RED AND PINK GRAPH
    """
        The red and pink graph graph shows the incurred delay and 
        distance penalt score (using the step function method) 
        imposed on users. The top axis is meters and the bottom axis
        is mins. The graph also shows the arithmetic and geometric
        means... which are an indication of equality in this case.
        i.e it should indicate how the penalty scores and impacted by the
        2 metrics...
        red doesnt look right to me...
        """
    
    fig,ax = subplots()
    title('Recreational User Equity and Fairness')
    ax.set_xlabel('User Number')
    ax.set_ylabel('Penalty to User')
    ax.scatter(users_rec, Penalty_rec, color='purple', marker='o',label='Penalty to Recreational User')
    ax.plot(users_rec, [gme_rec]*len(users_rec), color='darkorchid', marker='*',label=' Geometric Equity Mean')
    ax.plot(users_rec, [ame_rec]*len(users_rec), color='orchid', marker='.',label=' Arithmetic Equity Mean')
    
    #normalised extra distance travelled and total means (geo and ari)
    ax2=ax.twinx()

    ax.set_ylabel('Normalised Penalty to User')
    ax2.scatter(users_rec, Prel_rec, color='orange', marker='o',label='Normalised Penalty to Recreational User')
    ax2.plot(users_rec, [gmf_rec]*len(users_rec), color='darkorange', marker='*',label='Geometric Fairness Mean')
    ax2.plot(users_rec, [amf_rec]*len(users_rec), color='tomato', marker='.',label='Arithmetic Fairness Mean')
    ax2.set_xlabel('Extra meters travelled (m)')
    ax.set_ylabel('Normalised percieved Penalty')

    #below combines the legends from both axes
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper center')
'unhash below to see the equality / fairness graph for recreational users'
#fairVSequal()
#-----------------------------------------------------
print('E_rec, E_ecom, E_sur,  Sat_rec, Sat_ecom, Sat_sur, Fair_rec, Fair_ecom, Fair_sur')
a = '  '
print(E_rec,a, E_ecom,a, E_sur, a, Sat_rec, a, Sat_ecom, a, Sat_sur,  a, Fair_rec,   a,Fair_ecom,   a, Fair_sur)
