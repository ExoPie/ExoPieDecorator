## to do in the limit model 

1. test the code with 12 bins 
2. why muon id and muon scale are so shifted in run 2 combo plot (cr only fit): check the shape of all the needd nuisances, and smooth them if needed,  
3. 



## Only for Raman 
I don't have setup of correct version of combine, so i source this script in my area, you might want to install the combine correctly. 
source envsetter.sh

## 
root -l -b -q PrepareWS_withnuisance.C"(\"bbDM\", \"1b\", \"RECREATE\", \"AllMETHistos\", \"AllMETHistos_v16_06_04_04.root\", \"2016\")" 
root -l -b -q PrepareWS_withnuisance.C"(\"bbDM\", \"2b\", \"UPDATE\", \"AllMETHistos\", \"AllMETHistos_v16_06_04_04.root\", \"2016\")"

root -l -b -q PrepareWS_withnuisance.C"(\"bbDM\", \"1b\", \"RECREATE\", \"AllMETHistos\", \"AllMETHistos_v17_07_04_00.root\", \"2017\")"
root -l -b -q PrepareWS_withnuisance.C"(\"bbDM\", \"2b\", \"UPDATE\", \"AllMETHistos\", \"AllMETHistos_v17_07_04_00.root\", \"2017\")"


## change the year string in describe.py 
python RunLimits.py -c --model 2hdma --region "SR TOPE TOPMU WE WMU ZEE ZMUMU" --category=sr1
python RunLimits.py -c --model 2hdma --region "SR TOPE TOPMU WE WMU ZEE ZMUMU" --category=sr2


##  combine 1b and 2b category 
python RunLimits.py -c --model 2hdma --region "bbDM2016_datacardslist_1b_2hdma.txt bbDM2016_datacardslist_2b_2hdma.txt" --category=srall



for all mass points just replace 2hdma by 2hdma_all in all three commands above, 
python RunLimits.py -c --model 2hdma_all --region "SR TOPE TOPMU WE WMU ZEE ZMUMU" --category=sr1
python RunLimits.py -c --model 2hdma_all --region "SR TOPE TOPMU WE WMU ZEE ZMUMU" --category=sr2
python RunLimits.py -c --model 2hdma_all --region "bbDM2016_datacardslist_1b_2hdma_all.txt bbDM2016_datacardslist_2b_2hdma_all.txt" --category=srall


## copy the .root file with workspace in the datacards directory, otherwise the old file will be used. something like following is needs to be done manually. 
cp bbDM_2016_WS.root datacards_bbDM_2016/bbDM_2016_WS.root 


## To run the limits for all mass points use the above produced text files as an input to the tool 

python RunLimits.py -A -L -v 0 -i bbDM2016_datacardslist_1b_2hdma_all.txt --category=sr1 --savepdf --outlog="running limits for 1b"
python RunLimits.py -A -L -v 0 -i bbDM2016_datacardslist_2b_2hdma_all.txt --category=sr2 --savepdf --outlog="running limits for 2b"


## save the pdf 
python RunLimits.py --savepdf --limitTextFile bin/limits_bbDM_2b_2016.txt --outlog "saving pdf for 1b" --category=sr2

combine -M AsymptoticLimits datacards_bbDM_2016/datacard_bbDM2016_1b_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_150.txt








## To do 

#### move datacardtemplatename_ to describe.py 
#### move fparam to describe.py 


# Workflow for Limit Calculation
## Installation
Use the Higgs [Combine](http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/) page to install combine tool and for documentation

## Usage
* Make the ```AllMETHistos.root``` file using bbDM_combinedroot.py file
* Make the ```bbDM_WS.root``` file using PrepareWS_withSyst.C file
```
root -l -b -q PrepareWS_withSyst.C
```
* Run the dataCard_makeNrun.py file with create command for making the datacards
```
python dataCard_makeNrun.py create
```
* Run the dataCard_makeNrun.py file with run command for calculating the limit
```
python dataCard_makeNrun.py run
```
* Run limit_scanner.py file for getting the limit in text file
```
python limit_scanner.py
```
* Run limit_textTOgraph.py file to get the limit in root file
```
python limit_textTOgraph.py
```
* Run limit_plotter.py to get the plots:
```
python limit_plotter.py
```

### For getting prefit and postfit plots
```
combine -M FitDiagnostics --saveShapes --abs --all --plots datacard.txt
```


