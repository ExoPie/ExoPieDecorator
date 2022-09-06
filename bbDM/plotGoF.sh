year=2017
catg=2b

rm higgsCombine*Merged*.root

# _result_bonly_CRonly

hadd higgsCombine_result_bonly_CRonly_toy.GoodnessOfFit.mH120.Merged.root higgsCombine_result_bonly_CRonly_toy.GoodnessOfFit.mH120.1243*.root

## plotting
combineTool.py -M CollectGoodnessOfFit --input higgsCombine_result_bonly_CRonly.GoodnessOfFit.mH120.root higgsCombine_result_bonly_CRonly_toy.GoodnessOfFit.mH120.Merged.root -m 120.0 -o gof_result_bonly_CRonly_${catg}_${year}.json
plotGof.py gof_result_bonly_CRonly_${catg}_${year}.json --statistic saturated --mass 120.0 -o gof_result_bonly_CRonly_${catg}_${year} --title-right="B-only hypothesis"

# _result_sb

hadd higgsCombine_result_sb.GoodnessOfFit.mH120.Merged.root higgsCombine_result_sb.GoodnessOfFit.mH120.1253*.root

## plotting
combineTool.py -M CollectGoodnessOfFit --input higgsCombine_result_sb.GoodnessOfFit.mH120.root higgsCombine_result_sb.GoodnessOfFit.mH120.Merged.root -m 120.0 -o gof_result_sb_${catg}_${year}.json
plotGof.py gof_result_sb_${catg}_${year}.json --statistic saturated --mass 120.0 -o gof_result_sb_${catg}_${year} --title-right="S+B hypothesis"

## on real Data

hadd higgsCombineTest.GoodnessOfFit.mH120.Merged.root higgsCombineTest.GoodnessOfFit.mH120.1263*.root

## plotting
combineTool.py -M CollectGoodnessOfFit --input higgsCombineTest.GoodnessOfFit.mH120.root higgsCombineTest.GoodnessOfFit.mH120.Merged.root -m 120.0 -o gof_on_data_${catg}_${year}.json
plotGof.py gof_on_data_${catg}_${year}.json --statistic saturated --mass 120.0 -o gof_on_data_${catg}_${year} --title-right="on DATA"
