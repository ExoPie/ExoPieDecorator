import os
flist_ = open('bbDM_RUN2_datacardslist_C_2hdma_all.txt','w')

for i in [10,50, 100, 150, 200, 250, 300, 350, 400,450, 500 ]:
    massa = str(i)
    outcard='combination_2b_2bML/datacard_bbDM2_2b2ML_sp_0p7_tb_35_mXd_1_mA_600_ma_'+massa+'.txt'
    outcard_=outcard.replace('2b2ML', '2b2bML_Merged')
    fout = open(outcard_,'w')
    card_2b_    = 'datacards_bbDM_2017/datacard_bbDM2017_2b_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_'+massa+'.txt'
    card_2b_ML_ = 'datacards_bbDM_2017/datacard_bbDM2017_2b_ML_Merged_sp_0p7_tb_35_mXd_1_mA_600_ma_'+massa+'.txt'
    
    
    os.system( 'combineCards.py card_2b='+card_2b_+' card_2b_ML='+card_2b_ML_+' > '+outcard )
    for iline in open(outcard):
        iline=iline.replace("datacards_bbDM_2017/datacards_bbDM_2017", "datacards_bbDM_2017")
        fout.write(iline)

    #os.system('combine -M AsymptoticLimits '+outcard_+' --noFitAsimov')                                                                                                                                    
    flist_.write(outcard_+"\n")
flist_.close()
