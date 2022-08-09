rootfile=$1
year=$2
postfix=$3
nbins=$4
model=$5

python RunLimits.py --savepdf --limitTextFile bin/$postfix/limits_bbDM_2b_${year}.txt --outlog "saving pdf for 2b" --category=sr2  --year ${year} --model $model
