##https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/HiggsPAGPreapprovalChecks

datacard=datacards_bbDM_2017/datacard_bbDM2017_2b_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_100.txt
year=2017
catg=2b
mode=asimov


##combine -M AsymptoticLimits $datacard  --noFitAsimov  -v 0 --rMin 1e-07 --rMax 30
##
##rm fitDiagnostics.root
##combine -M FitDiagnostics --saveShapes $datacard --saveWithUncertainties --saveNormalizations --X-rtd MINIMIZER_analytic  --rMin -100 -t -1 --expectSignal 0
##
##rm fitDiagnostics_$catg_$year_$mode.root
##mv fitDiagnostics.root fitDiagnostics_$catg_$year_$mode.root
##
##rm pulls_$catg_$year_$mode.root
##python diffNuisances.py fitDiagnostics_$catg_$year_$mode.root --abs --all -g pulls_$catg_$year_$mode.root
##
##root -l -b -q PlotPulls.C\(\"pulls_$catg_$year_$mode.root\",\"plots_limit/pulls/\",\"_$catg_$year_\"\)
##
##python yieldratio.py fitDiagnostics_$catg_$year_$mode.root plots_limit/YieldRatio/ _$catg_$year_
##
##python stackhist.py  fitDiagnostics_$catg_$year_$mode.root $catg $mode $year


## move everything to a web page and spit the link to page 

mode=cronly

rm fitDiagnostics.root

## convert to workspace 
text2workspace.py $datacard --channel-masks
datacardws=`echo $datacard | sed  's|.txt|.root|g'`
echo $datacardws

## perform fit 
combine -M FitDiagnostics  $datacardws --saveShapes --saveWithUncertainties --setParameters mask_SR=1,mask_cat_1b_SR=1,mask_cat_2b_SR=1 --X-rtd MINIMIZER_analytic --cminFallbackAlgo Minuit2,0:1.0

## clean area 
rm fitDiagnostics_${catg}_${year}_${mode}.root
mv fitDiagnostics.root fitDiagnostics_${catg}_${year}_${mode}.root

rm pulls_${catg}_${year}_${mode}.root

## create pulls 
python diffNuisances.py fitDiagnostics_${catg}_${year}_${mode}.root --abs --all -g pulls_${catg}_${year}_${mode}.root


## save pulls 
root -l -b -q PlotPulls.C\(\"pulls_${catg}_${year}_${mode}.root\",\"plots_limit/pulls/\",\"_${catg}_${year}_\"\)

## save yield ratio 
python yieldratio.py fitDiagnostics_${catg}_${year}_${mode}.root plots_limit/YieldRatio/ _${catg}_${year}_

## save stack plots 
python stackhist.py  fitDiagnostics_${catg}_${year}_${mode}.root ${catg} ${mode} ${year}




## run impact b-only
combineTool.py -M Impacts -d $datacardws --doInitialFit --robustFit 1 -m 125 -t -1 --expectSignal 0 --rMin -10
combineTool.py -M Impacts -d $datacardws --doFits  --robustFit 1 -m 125 --parallel 32 -t -1 --expectSignal 0 --rMin -10
combineTool.py -M Impacts -d  $datacardws -m 125 -o impacts_t0.json
plotImpacts.py -i  impacts_t0.json -o  impacts_t0



## run impact signal injected 
combineTool.py -M Impacts -d $datacardws --doInitialFit --robustFit 1 -m 125 -t -1 --expectSignal 1 --rMin -10
combineTool.py -M Impacts -d $datacardws --doFits  --robustFit 1 -m 125 --parallel 32 -t -1 --expectSignal 1 --rMin -10
combineTool.py -M Impacts -d  $datacardws -m 125 -o impacts_t1.json
plotImpacts.py -i  impacts_t1.json -o  impacts_t1




## limit 
combine -M AsymptoticLimits $datacardws --noFitAsimov  -v 0 --rMin 1e-07 --rMax 3 


## Pulls b only 
combine -M FitDiagnostics  $datacardws --saveShapes --saveWithUncertainties -t -1 --expectSignal 0
python diffNuisances.py fitDiagnostics.root -a  --abs -g plots_t0.root

## Pulls signal injected 
combine -M FitDiagnostics  $datacardws --saveShapes --saveWithUncertainties -t -1 --expectSignal 1
python diffNuisances.py fitDiagnostics.root -a  --abs -g plots_t1.root
