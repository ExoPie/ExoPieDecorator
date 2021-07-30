#dirname=$1
#datacard=datacards_bbDM_2017/datacard_bbDM2017_2b_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_100.txt
dirname=checkscombo2017
#datacard=datacards_bbDM_run2/datacard_bbDMrun2_C_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_100.txt
datacard=datacards_bbDM_2017/datacard_bbDM2017_2b_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_100.txt
#datacards_bbDM_2017/datacard_bbDM2017_C_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_100.txt
year=2017
catg=C

mode=asimov_t_0

## create workspace 
text2workspace.py $datacard --channel-masks
datacardws=`echo $datacard | sed  's|.txt|.root|g'`
echo $datacardws

## run limits 
mkdir -p ${dirname}
combine -M AsymptoticLimits $datacard    -v 0 --rMin 1e-07 --rMax 30 > ${dirname}/limit.txt
combine -M AsymptoticLimits $datacard  -t -1  -v 0 --rMin 1e-07 --rMax 30 > ${dirname}/limit_blind.txt


## run pulls and impact asimov b-only 
#### pulls 
combine -M FitDiagnostics  $datacardws --saveShapes --saveWithUncertainties -t -1 --expectSignal 0 -n _${catg}_${year}_${mode}_${dirname}
python diffNuisances.py fitDiagnostics_${catg}_${year}_${mode}_${dirname}.root --abs --all -g pulls_${catg}_${year}_${mode}_${dirname}.root
root -l -b -q PlotPulls.C\(\"pulls_${catg}_${year}_${mode}_${dirname}.root\",\"${dirname}/\",\"_${catg}_${year}_${mode}_${dirname}\"\)



#### impacts
#--freezeParameters ratett --setParameters ratett=1.2
text2workspace.py $datacard --channel-masks
combineTool.py -M Impacts -d $datacardws --doInitialFit --robustFit 1 -m 125 -t -1 --expectSignal 0 --rMin -10
combineTool.py -M Impacts -d $datacardws --doFits  --robustFit 1 -m 125 --parallel 32 -t -1 --expectSignal 0 --rMin -10
combineTool.py -M Impacts -d  $datacardws -m 125 -o impacts_t0.json
plotImpacts.py -i  impacts_t0.json -o   ${dirname}/impacts_t0_${dirname}

## run pulls and impact asimov signal injected 
### pulls 

mode=asimov_t_m1

combine -M FitDiagnostics  $datacardws --saveShapes --saveWithUncertainties -t -1 --expectSignal 1 -n _${catg}_${year}_${mode}_${dirname}
python diffNuisances.py fitDiagnostics_${catg}_${year}_${mode}_${dirname}.root --abs --all -g pulls_${catg}_${year}_${mode}_${dirname}.root
root -l -b -q PlotPulls.C\(\"pulls_${catg}_${year}_${mode}_${dirname}.root\",\"${dirname}/\",\"_${catg}_${year}_${mode}_${dirname}\"\)


#### impacts
combineTool.py -M Impacts -d $datacardws --doInitialFit --robustFit 1 -m 125 -t -1 --expectSignal 1 --rMin -10
combineTool.py -M Impacts -d $datacardws --doFits  --robustFit 1 -m 125 --parallel 32 -t -1 --expectSignal 1 --rMin -10
combineTool.py -M Impacts -d  $datacardws -m 125 -o impacts_t1.json
plotImpacts.py -i  impacts_t1.json -o  ${dirname}/impacts_t1_${dirname}



mode=fit_CRonly_result

## CR only fit pulls 
combine -M FitDiagnostics -d $datacardws -n _${catg}_${year}_${mode}_${dirname}  --saveShapes --saveWithUncertainties --setParameters mask_SR=1,mask_cat_1b_SR=1,mask_cat_2b_SR=1 --X-rtd MINIMIZER_analytic --cminFallbackAlgo Minuit2,0:1.0
root -l -b -q plotPostNuisance_combine.C\(\"fitDiagnostics_${catg}_${year}_${mode}_${dirname}.root\",\"${dirname}/\",\"${catg}_${year}_${mode}_${dirname}\"\)


#combine -M FitDiagnostics -d $datacardws -n _${catg}_${year}_${mode}_${dirname}  --saveShapes --saveWithUncertainties --setParameters mask_SR=1,mask_d2016_cat_1b_SR=1,mask_d2016_cat_2b_SR=1,mask_d2017_cat_1b_SR=1,mask_d2017_cat_2b_SR=1,mask_d2018_cat_1b_SR=1,mask_d2018_cat_2b_SR=1, --X-rtd MINIMIZER_analytic --cminFallbackAlgo Minuit2,0:1.0


## CR only postfit summary plot  ## need to work on this one. 
#python stackhist.py  fitDiagnostics_$catg_$year_$mode.root $catg $mode $year

#python crSummary_postfit.py -i fitDiagnostics_${catg}_${year}_${mode}_${dirname}.root -d b -c 2b -t ${catg}_${year}_${mode}_${dirname} -y 2017



#combine -M FitDiagnostics -d $datacardws -n _${catg}_${year}_${mode}_${dirname}  --saveShapes --saveWithUncertainties --freezeParameters ratett --setParameters mask_SR=1,ratett=1.2 --X-rtd MINIMIZER_analytic --cminFallbackAlgo Minuit2,0:1.0

