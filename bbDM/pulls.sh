combine -M FitDiagnostics --saveShapes datacards_bbDM_2017/datacard_bbDM2017_2b_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_100.txt --saveWithUncertainties --saveNormalizations   --rMin 0 -t -1 --expectSignal 0 --X-rtd MINIMIZER_analytic
python diffNuisances.py fitDiagnostics.root --abs --all -g  pulls.root

combine -M AsymptoticLimits datacards_bbDM_2017/datacard_bbDM2017_2b_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_100.txt  -v 0 --rMin 1e-07 --rMax 30 --noFitAsimov
