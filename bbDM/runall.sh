rootfile=$1
year=$2
postfix=$3
nbins=$4
model=$5

echo $nbins


root -l -b -q PrepareWS_withnuisanceInvertTF_noW_nBins.C"(\"bbDM\", \"1b\", \"RECREATE\", \"AllMETHistos\", \"$rootfile\", \"${year}\", $nbins)"
root -l -b -q PrepareWS_withnuisanceInvertTF_noW_nBins.C"(\"bbDM\", \"2b\", \"UPDATE\", \"AllMETHistos\", \"$rootfile\", \"${year}\", $nbins)"

#root -l -b -q PrepareWS_withnuisanceInvertTF_noW_nBins.C"(\"bbDM\", \"2b_ML\", \"RECREATE\", \"AllMETHistos\", \"$rootfile\", \"${year}\", $nbins)"
#python RunLimits.py -c --model 2hdma_all --region "SR TOPE TOPMU ZEE ZMUMU" --category=sr2 --year ${year}
#cp bbDM_${year}_WS.root datacards_bbDM_${year}/bbDM_${year}_WS.root
#python RunLimits.py -A -L -v 0 -i bbDM${year}_datacardslist_2b_ML_2hdma_all.txt --category=sr2 --postfix $postfix --savepdf --outlog="running limits for 2b"  --year ${year}


cp bbDM_${year}_WS.root datacards_bbDM_${year}/bbDM_${year}_WS.root




if [[ $model == "2hdma" ]]
then 
    echo "preparing datacards for :", $model
    sleep 2
    
    # create cards
    #python RunLimits.py -c --model 2hdma_all --region "SR WE WMU ZEE ZMUMU" --category=sr1 --year ${year}
    #python RunLimits.py -c --model 2hdma_all --region "SR TOPE TOPMU ZEE ZMUMU" --category=sr2 --year ${year}
    #python RunLimits.py -c --model 2hdma_all --region "bbDM${year}_datacardslist_1b_2hdma_all.txt bbDM${year}_datacardslist_2b_2hdma_all.txt" --category=srall --year ${year}
    
    # run limits #
    #python RunLimits.py -A -L -v 0 -i bbDM${year}_datacardslist_1b_2hdma_all.txt --category=sr1 --postfix $postfix --savepdf --outlog="running limits for 1b"  --year ${year}
    python RunLimits.py -A -L -v 0 -i bbDM${year}_datacardslist_2b_2hdma_all.txt --category=sr2 --postfix $postfix --savepdf --outlog="running limits for 2b"  --year ${year}
    #python RunLimits.py -A -L -v 0 -i bbDM${year}_datacardslist_C_2hdma_all.txt --category=srall --postfix $postfix --savepdf --outlog="running limits for 1b+2b"  --year ${year}

    #python RunLimits.py --savepdf --limitTextFile bin/$postfix/limits_bbDM_${model}_1b_${year}.txt --outlog "saving pdf for 1b" --category=sr1  --year ${year} 
    #python RunLimits.py --savepdf --limitTextFile bin/$postfix/limits_bbDM_${model}_2b_${year}.txt --outlog "saving pdf for 2b" --category=sr2  --year ${year} 
    #python RunLimits.py --savepdf --limitTextFile bin/$postfix/limits_bbDM_${model}_combined_${year}.txt --outlog "saving pdf for 1b+2b" --category=srall  --year ${year} 

fi 



if  [[ $model == "dmsimp" ]] 
then
    echo "preparing datacards for :", $model
    sleep 2
    
    # create cards
    #python RunLimits.py -c --model dmsimp_all --region "SR WE WMU ZEE ZMUMU" --category=sr1 --year ${year}
    python RunLimits.py -c --model dmsimp_all --region "SR TOPE TOPMU ZEE ZMUMU" --category=sr2 --year ${year}
    #python RunLimits.py -c --model dmsimp_all --region "bbDM${year}_datacardslist_1b_dmsimp_all.txt bbDM${year}_datacardslist_2b_dmsimp_all.txt" --category=srall --year ${year}

    # run limits
 #   python RunLimits.py -A -L -v 0 -i bbDM${year}_datacardslist_1b_dmsimp_all.txt --category=sr1 --postfix $postfix --savepdf --outlog="running limits for 1b"  --year ${year} --model dmsimp_all
    python RunLimits.py -A -L -v 0 -i bbDM${year}_datacardslist_2b_dmsimp_all.txt --category=sr2 --postfix $postfix --savepdf --outlog="running limits for 2b"  --year ${year} --model dmsimp_all
 #   python RunLimits.py -A -L -v 0 -i bbDM${year}_datacardslist_C_dmsimp_all.txt --category=srall --postfix $postfix --savepdf --outlog="running limits for 1b+2b"  --year ${year} --model dmsimp_all

    #python RunLimits.py --savepdf --limitTextFile bin/$postfix/limits_bbDM_${model}_all_1b_${year}.txt --outlog "saving pdf for 1b" --category=sr1  --year ${year} --model dmsimp
 #   python RunLimits.py --savepdf --limitTextFile bin/$postfix/limits_bbDM_${model}_all_2b_${year}.txt --outlog "saving pdf for 2b" --category=sr2  --year ${year} --model dmsimp
    #python RunLimits.py --savepdf --limitTextFile bin/$postfix/limits_bbDM_${model}_all_combined_${year}.txt --outlog "saving pdf for 1b+2b" --category=srall  --year ${year} --model dmsimp

fi



cp index.php plots_limit/$postfix
cp -r plots_limit/$postfix /afs/cern.ch/work/k/khurana/public/AnalysisStuff/bbDM/LimitStuff






#python RunLimits.py --savepdf --limitTextFile bin/$postfix/limits_bbDM_2b_${year}.txt --outlog "saving pdf for 2b" --category=sr2  --year ${year}
#python RunLimits.py --savepdf --limitTextFile bin/limits_bbDM_combined_${year}.txt --outlog "saving pdf for 1b+2b" --category=srall  --year ${year}



## for pull etc 
#root -l -b -q PrepareWS_withnuisance.C"(\"bbDM\", \"1b\", \"RECREATE\", \"AllMETHistos\", \"$rootfile\", \"${year}\")"
#root -l -b -q PrepareWS_withnuisance.C"(\"bbDM\", \"2b\", \"UPDATE\", \"AllMETHistos\", \"$rootfile\", \"${year}\")"
#python RunLimits.py -c --model 2hdma --region "SR TOPE TOPMU WE WMU ZEE ZMUMU" --category=sr1  --year ${year}
#python RunLimits.py -c --model 2hdma --region "SR TOPE TOPMU WE WMU ZEE ZMUMU" --category=sr2 --year ${year}
#python RunLimits.py -c --model 2hdma --region "bbDM${year}_datacardslist_1b_2hdma_all.txt bbDM${year}_datacardslist_2b_2hdma_all.txt" --category=srall  --year ${year}
#python RunLimits.py --pulls --runmode asimov -i bbDM2017_datacardslist_C_2hdma.txt  --outlog "testing the pulls for asimov" --category srall --year ${year}
#python PlotPreFitPostFit.py fitDiagnostics_combined_2017_asimov.root plots_limit/postfitOverlay/ _combined_2017_

#python RunLimits.py --pulls --runmode data -i bbDM2016_datacardslist_C_2hdma.txt  --outlog "testing the pulls for data" --category srall                                                               

#python RunLimits.py --pulls --runmode cronly -i bbDM2016_datacardslist_C_2hdma.txt  --outlog "testing the pulls for data" --category srall --year ${year}                                                              
#python RunLimits.py --pulls --runmode cronly -i bbDM2017_datacardslist_C_2hdma.txt  --outlog "testing the pulls for data" --category srall --year ${year}                                                              
#python RunLimits.py --pulls --runmode cronly -i bbDM2018_datacardslist_C_2hdma.txt  --outlog "testing the pulls for data" --category srall --year ${year}                                                              
#																	    
#python RunLimits.py --pulls --runmode cronly -i bbDM2017_datacardslist_1b_2hdma.txt  --outlog "testing the pulls for data" --category sr1b --year ${year}
#python RunLimits.py --pulls --runmode cronly -i bbDM2017_datacardslist_2b_2hdma.txt  --outlog "testing the pulls for data" --category sr2b --year ${year}
#python RunLimits.py --pulls --runmode cronly -i bbDM2017_datacardslist_C_2hdma.txt  --outlog "testing the pulls for data" --category srall --year ${year}

#text2workspace.py datacards_bbDM_2017/datacard_bbDM2017_2b_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_100.txt --channel-masks
#combine -M FitDiagnostics  datacards_bbDM_2017/datacard_bbDM2017_2b_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_100.root --saveShapes --saveWithUncertainties --setParameters mask_SR=1
#combine -M FitDiagnostics datacards_bbDM_2017/datacard_bbDM2017_C_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_100.root  --saveShapes --saveWithUncertainties --setParameters mask_cat_1b_SR=1,mask_cat_2b_SR=1
#root -l -b -q plotPostNuisance_combine.C\(\"fitDiagnostics.root\",\"plots_limit/pulls/\",\"_2b_2017_\"\)

#plotPostNuisance_combine.C("fitDiagnostics_2b_2017_cronly.root","plots_limit/pulls/","_2b_2017_")

#python  stackhist.py


## combine -M AsymptoticLimits datacards_bbDM_2017/datacard_bbDM2017_C_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_10.txt  --noFitAsimov  -v 0 --rMin 1e-07 --rMax 30


## impact: asimov 
#combineTool.py -M Impacts -d  datacards_bbDM_2017/datacard_bbDM2017_C_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_100.root -m 200 --rMin -1 --rMax 2 --robustFit 1 --doInitialFit  -t -1 --expectSignal 0
#combineTool.py -M Impacts -d datacards_bbDM_2017/datacard_bbDM2017_C_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_100.root -m 200 --rMin -1 --rMax 2 --robustFit 1 --doFits  -t -1 --expectSignal 0
#combineTool.py -M Impacts -d datacards_bbDM_2017/datacard_bbDM2017_C_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_100.root -m 200 --rMin -1 --rMax 2 --robustFit 1 --output impacts.json
# plotImpacts.py -i impacts.json -o impacts
#[khurana@lxplus774 bbDM]$ combine -M FitDiagnostics  datacards_bbDM_2017/datacard_bbDM2017_2b_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_100.root --saveShapes --saveWithUncertainties --setParameters mask_SR=1,mask_cat_1b_SR=1,mask_cat_2b_SR=1   -v 3 --cminDefaultMinimizerType Minuit2 --cminDefaultMinimizerStrategy 1 --cminFallbackAlgo Minuit2,0:1.0



#combine -M AsymptoticLimits datacards_bbDM_2017/datacard_bbDM2017_C_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_250.txt  --noFitAsimov  -v 0 --rMin 1e-07 --rMax 30 


# datacards_bbDM_2017_b/datacard_bbDM2017_1b_SR_sp_0p7_tb_35_mXd_1_mA_600_ma_200.txt : 1.9375
# datacards_bbDM_2017_b/datacard_bbDM2017_2b_SR_sp_0p7_tb_35_mXd_1_mA_600_ma_200.txt : 0.6621
