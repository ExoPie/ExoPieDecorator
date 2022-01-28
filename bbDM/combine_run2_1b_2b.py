import os 
import sys 
from LimitHelper import RunLimits

dmsimp=False



#########################################################
## This will take the merged datacards for each year and tgen combine them all together. 
## possible values for category=["1b","2b","C"]
#########################################################

'''
Usage: simply execute using 
python combine_run2.py 

Explanation: This macro uses the datacards listed in .txt files and make combination datacards and then execute the AsymptoticLimits. The outcome is generally one pdf/png plot for the combination. 

What to change: There are few parameters which needs to be changed: 
1.  maList: only those points can enter for which exist for all years. 
2. category: possible values are "1b", "2b", "C" or depending on how datacards are made 
3. dmsimp: the boolean can be used to switch the model to scan 
4. 

'''

if dmsimp==False:
    maList=[10,50,100,200,250,300,350,400,500]
    category="2b"
    datacard="datacards_bbDM_{}/datacard_bbDM{}_{}_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_{}.txt"
    model="2hdma"

## We decided to not use the DMSimp due to very poor sensitivity for this model. 
if dmsimp==True:
    maList=[50,100,200,300,400,500]
    category="C"
    datacard="datacards_bbDM_{}/datacard_bbDM{}_{}_Merged_mphi_{}_mchi_1.txt"
    model="dmsimp"
datacardCounter=0


## create and object of class RunLimits
limithelp=RunLimits(datacard,"161718","bbDM",category,"Run2Combo_"+category,model )
for ma in maList:
    #ma=50
    datacard_2016=datacard.format("2016","2016",category,str(ma))
    datacard_2017=datacard.format("2017","2017",category,str(ma))
    datacard_2018=datacard.format("2018","2018",category,str(ma))
    
    datacard_run2=datacard.format("run2","run2",category,str(ma))
    
    log_run2 = datacard_run2.replace(".txt",".log")
    combodatacard=""
    #if dmsimp==True:
    #combodatacard  = "combineCards.py d2017="+datacard_2017+" d2018="+datacard_2018+" > "+datacard_run2
    #if dmsimp==False:
    combodatacard  = "combineCards.py d2016="+datacard_2016+" d2017="+datacard_2017+" d2018="+datacard_2018+" > "+datacard_run2
    print (combodatacard)
    os.system(combodatacard)
    
    fout=open("tmp.txt","w")
    for iline in open(datacard_run2):
        iline=iline.replace("datacards_bbDM_2016/datacards_bbDM_2016", "datacards_bbDM_2016")
        iline=iline.replace("datacards_bbDM_2017/datacards_bbDM_2017", "datacards_bbDM_2017")
        iline=iline.replace("datacards_bbDM_2018/datacards_bbDM_2018", "datacards_bbDM_2018")
        fout.write(iline)
    fout.close()
    
    os.system("mv tmp.txt "+ datacard_run2)
    os.system('combine -M AsymptoticLimits '+datacard_run2+' --noFitAsimov -t -1 > '+log_run2)
    
    
    if datacardCounter ==0: mode = "w"
    if datacardCounter > 0: mode = "a"
    datacardCounter=datacardCounter+1
        
    limit_textfilename=limithelp.LogToLimitList(log_run2,category,mode)

limit_rootfilename = limithelp.TextFileToRootGraphs(limit_textfilename)

limithelp.SaveLimitPdf1D(limit_rootfilename)
    



