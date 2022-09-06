datacard=datacards_bbDM_2017/datacard_bbDM2017_2b_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_200.txt
year=2017
catg=2b

text2workspace.py $datacard --channel-masks
datacardws=`echo $datacard | sed  's|.txt|.root|g'`

echo $datacardws

# _result_bonly_CRonly
## for data
combine -M GoodnessOfFit -d $datacardws --algo=saturated -n _result_bonly_CRonly --setParametersForFit mask_SR=1 --setParametersForEval mask_SR=0 --freezeParameters r --setParameters r=0

## for toys
combine -M GoodnessOfFit -d $datacardws --algo=saturated -n _result_bonly_CRonly_toy --setParametersForFit mask_SR=1 --setParametersForEval mask_SR=0 --freezeParameters r --setParameters r=0,mask_SR=1 -t 100 --toysFrequentist -s 12431 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_bonly_CRonly_toy --setParametersForFit mask_SR=1 --setParametersForEval mask_SR=0 --freezeParameters r --setParameters r=0,mask_SR=1 -t 100 --toysFrequentist -s 12432 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_bonly_CRonly_toy --setParametersForFit mask_SR=1 --setParametersForEval mask_SR=0 --freezeParameters r --setParameters r=0,mask_SR=1 -t 100 --toysFrequentist -s 12433 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_bonly_CRonly_toy --setParametersForFit mask_SR=1 --setParametersForEval mask_SR=0 --freezeParameters r --setParameters r=0,mask_SR=1 -t 100 --toysFrequentist -s 12434 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_bonly_CRonly_toy --setParametersForFit mask_SR=1 --setParametersForEval mask_SR=0 --freezeParameters r --setParameters r=0,mask_SR=1 -t 100 --toysFrequentist -s 12435 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_bonly_CRonly_toy --setParametersForFit mask_SR=1 --setParametersForEval mask_SR=0 --freezeParameters r --setParameters r=0,mask_SR=1 -t 100 --toysFrequentist -s 12436 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_bonly_CRonly_toy --setParametersForFit mask_SR=1 --setParametersForEval mask_SR=0 --freezeParameters r --setParameters r=0,mask_SR=1 -t 100 --toysFrequentist -s 12437 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_bonly_CRonly_toy --setParametersForFit mask_SR=1 --setParametersForEval mask_SR=0 --freezeParameters r --setParameters r=0,mask_SR=1 -t 100 --toysFrequentist -s 12438 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_bonly_CRonly_toy --setParametersForFit mask_SR=1 --setParametersForEval mask_SR=0 --freezeParameters r --setParameters r=0,mask_SR=1 -t 100 --toysFrequentist -s 12439 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_bonly_CRonly_toy --setParametersForFit mask_SR=1 --setParametersForEval mask_SR=0 --freezeParameters r --setParameters r=0,mask_SR=1 -t 100 --toysFrequentist -s 12430 &



# _result_sb
## for data
combine -M GoodnessOfFit -d $datacardws --algo=saturated -n _result_sb
## for toys
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_sb  -t 100 --toysFrequentist -s 12531 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_sb  -t 100 --toysFrequentist -s 12532 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_sb  -t 100 --toysFrequentist -s 12533 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_sb  -t 100 --toysFrequentist -s 12534 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_sb  -t 100 --toysFrequentist -s 12535 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_sb  -t 100 --toysFrequentist -s 12536 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_sb  -t 100 --toysFrequentist -s 12537 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_sb  -t 100 --toysFrequentist -s 12538 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_sb  -t 100 --toysFrequentist -s 12539 &
combine -M GoodnessOfFit -d  $datacardws --algo=saturated -n _result_sb  -t 100 --toysFrequentist -s 12530 &


## on real Data

combine -M GoodnessOfFit $datacardws --algo=saturated

combine -M GoodnessOfFit $datacardws --algo=saturated -t 100 --toysFreq -s 12431 & ## It is recomended to use the frequentist toys (--toysFreq) when running the saturated model
combine -M GoodnessOfFit $datacardws --algo=saturated -t 100 --toysFreq -s 12432 &
combine -M GoodnessOfFit $datacardws --algo=saturated -t 100 --toysFreq -s 12433 &
combine -M GoodnessOfFit $datacardws --algo=saturated -t 100 --toysFreq -s 12434 &
combine -M GoodnessOfFit $datacardws --algo=saturated -t 100 --toysFreq -s 12435 &
combine -M GoodnessOfFit $datacardws --algo=saturated -t 100 --toysFreq -s 12436 &
combine -M GoodnessOfFit $datacardws --algo=saturated -t 100 --toysFreq -s 12437 &
combine -M GoodnessOfFit $datacardws --algo=saturated -t 100 --toysFreq -s 12438 &
combine -M GoodnessOfFit $datacardws --algo=saturated -t 100 --toysFreq -s 12439 &
combine -M GoodnessOfFit $datacardws --algo=saturated -t 100 --toysFreq -s 12430 &



