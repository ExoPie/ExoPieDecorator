import os
import yaml
import numpy as np
from collections import OrderedDict
import pandas as pd
import sys, optparse,argparse

## ----- command line argument
usage = "python -y 2017 -c R -reg ['SR']"
parser = argparse.ArgumentParser(description=usage)
parser.add_argument("-y", "--year", dest="year", default="2017")
parser.add_argument("-m", "--model", dest="model", default="THDMa")
parser.add_argument("-c", "--category",  dest="category",default="B")
# parser.add_argument("-r", "--region", dest="region", default=['SR'])
parser.add_argument("-reg", nargs="+", default=["a", "b"])
args = parser.parse_args()

year     = args.year
category = args.category
regions  = args.reg
modelName = args.model


print (year, category, regions)
if category=='R':
    f = open('datacard_tempalate_Resolved.ymal')
else:
    f = open('datacard_tempalate_boosted.ymal')
doc = yaml.safe_load(f)

signalFile = open('datacard_tempalate_signal.ymal','r')
signalDoc  = yaml.safe_load(signalFile)


outdir = 'datacards_monoHbb_'+year
os.system('mkdir '+ outdir)
top_ = '''
imax *  number of channels
jmax *  number of backgrounds

kmax *  number of nuisance parameters (sources of systematical uncertainties)
'''

def getEndPart(reg):
    end_=''
    if reg=='SR':
        end_='''
CMSYEAR_EleRECO param  0.0 1
CMSYEAR_EleID param  0.0 1
CMSYEAR_MuID param  0.0 1
CMSYEAR_trig_ele param 0.0 1
CMSYEAR_MuISO param  0.0 1
CMSYEAR_eff_b param 0.0 1
CMSYEAR_prefire param 0.0 1
rrv_CMSYEAR_stats_err_TOPE_tt_'''+category+'''_bin1 param 0.0 1
rrv_CMSYEAR_stats_err_TOPE_tt_'''+category+'''_bin2 param 0.0 1
rrv_CMSYEAR_stats_err_TOPE_tt_'''+category+'''_bin3 param 0.0 1
rrv_CMSYEAR_stats_err_TOPE_tt_'''+category+'''_bin4 param 0.0 1
rrv_CMSYEAR_stats_err_TOPMU_tt_'''+category+'''_bin1 param 0.0 1
rrv_CMSYEAR_stats_err_TOPMU_tt_'''+category+'''_bin2 param 0.0 1
rrv_CMSYEAR_stats_err_TOPMU_tt_'''+category+'''_bin3 param 0.0 1
rrv_CMSYEAR_stats_err_TOPMU_tt_'''+category+'''_bin4 param 0.0 1
rrv_CMSYEAR_stats_err_ZEE_dyjets_'''+category+'''_bin1 param 0.0 1
rrv_CMSYEAR_stats_err_ZEE_dyjets_'''+category+'''_bin2 param 0.0 1
rrv_CMSYEAR_stats_err_ZEE_dyjets_'''+category+'''_bin3 param 0.0 1
rrv_CMSYEAR_stats_err_ZEE_dyjets_'''+category+'''_bin4 param 0.0 1
rrv_CMSYEAR_stats_err_ZMUMU_dyjets_'''+category+'''_bin1 param 0.0 1
rrv_CMSYEAR_stats_err_ZMUMU_dyjets_'''+category+'''_bin2 param 0.0 1
rrv_CMSYEAR_stats_err_ZMUMU_dyjets_'''+category+'''_bin3 param 0.0 1
rrv_CMSYEAR_stats_err_ZMUMU_dyjets_'''+category+'''_bin4 param 0.0 1
'''

    if reg =='ZMUMU':
        end_='''
rrvbc_SR_zjets_'''+category+'''1_YEAR flatParam
rrvbc_SR_zjets_'''+category+'''2_YEAR flatParam
rrvbc_SR_zjets_'''+category+'''3_YEAR flatParam
rrvbc_SR_zjets_'''+category+'''4_YEAR flatParam
tf1_ZMUMU_dyjets_'''+category+'''_YEAR flatParam
tf2_ZMUMU_dyjets_'''+category+'''_YEAR flatParam
tf3_ZMUMU_dyjets_'''+category+'''_YEAR flatParam
tf4_ZMUMU_dyjets_'''+category+'''_YEAR flatParam
'''
    if reg =='ZEE':
        end_='''
rrvbc_SR_zjets_'''+category+'''1_YEAR flatParam
rrvbc_SR_zjets_'''+category+'''2_YEAR flatParam
rrvbc_SR_zjets_'''+category+'''3_YEAR flatParam
rrvbc_SR_zjets_'''+category+'''4_YEAR flatParam
tf1_ZEE_dyjets_'''+category+'''_YEAR flatParam
tf2_ZEE_dyjets_'''+category+'''_YEAR flatParam
tf3_ZEE_dyjets_'''+category+'''_YEAR flatParam
tf4_ZEE_dyjets_'''+category+'''_YEAR flatParam
'''
    if reg =='TOPMU':
        end_='''  
rrvbc_SR_tt_'''+category+'''1_YEAR flatParam
rrvbc_SR_tt_'''+category+'''2_YEAR flatParam
rrvbc_SR_tt_'''+category+'''3_YEAR flatParam
rrvbc_SR_tt_'''+category+'''4_YEAR flatParam
'''
    if reg =='TOPE':
        end_='''  
tf1_TOPE_tt_'''+category+'''_YEAR flatParam
tf2_TOPE_tt_'''+category+'''_YEAR flatParam
tf3_TOPE_tt_'''+category+'''_YEAR flatParam
tf4_TOPE_tt_'''+category+'''_YEAR flatParam
rrvbc_SR_tt_'''+category+'''1_YEAR flatParam
rrvbc_SR_tt_'''+category+'''2_YEAR flatParam
rrvbc_SR_tt_'''+category+'''3_YEAR flatParam
rrvbc_SR_tt_'''+category+'''4_YEAR flatParam
'''
    if end_ =='' :
        print("Inside getEndPart fix end_")
        exit
    return end_



def getUpperPart2(reg,cat):
	top_= 'shapes * '+reg+' monoHbb_'+year+'_WS.root ws_monoHbb_'+cat+'_'+year+':monoHbb2017_'+cat+'_'+reg+'_$PROCESS ws_monoHbb_'+cat+'_'+year+':monoHbb2017_'+cat+'_'+reg+'_$PROCESS_$SYSTEMATIC'+'\n'
        addst_ =''
        if reg =='SR':
            addst_ ='shapes  tt '+reg+' monoHbb_'+year+'_WS.root ws_monoHbb_'+cat+'_'+year+':rph_SR_tt_'+cat+'_'+year+ '\n' +'shapes zjets  '+reg+' monoHbb_'+year+'_WS.root ws_monoHbb_'+cat+'_'+year+':rph_SR_zjets_'+cat+'_'+year+ '\n'
        if reg == 'ZEE' :
            addst_ ='shapes  dyjets '+reg+' monoHbb_'+year+'_WS.root ws_monoHbb_'+cat+'_'+year+':rph_ZEE_dyjets_'+cat+'_'+year+ '\n'
        if reg == 'ZMUMU':    
            addst_ ='shapes  dyjets '+reg+' monoHbb_'+year+'_WS.root ws_monoHbb_'+cat+'_'+year+':rph_ZMUMU_dyjets_'+cat+'_'+year+ '\n'
        if reg =='TOPE' :
            addst_ = 'shapes  tt '+reg+' monoHbb_'+year+'_WS.root ws_monoHbb_'+cat+'_'+year+':rph_TOPE_tt_'+cat+'_'+year+ '\n'
        if reg =='TOPMU' :
            addst_ = 'shapes  tt '+reg+' monoHbb_'+year+'_WS.root ws_monoHbb_'+cat+'_'+year+':rph_TOPMU_tt_'+cat+'_'+year+ '\n'
        if addst_ =='':
            print("Inside getUpperPart2 fix addstr_")
            exit
        return top_+addst_


# def getUpperPart2(reg,cat):
# 	top_= 'shapes * '+reg+' AllMETHistos.root  monoHbb2017_'+cat+'_'+reg+'_bdtscore'+'_$PROCESS monoHbb2017_'+cat+'_'+reg+'_bdtscore'+'_$PROCESS_$SYSTEMATIC'
# 	return top_

def getUpperPart3(reg):
	top_ = 'bin '+reg
	# observation -1
	return top_

def getDic(dics,name):
	values=''
	itm=dics[name]
	# print name ,itm[0].split()
	values = itm[0].split()
	# for key, value in dics:
	# 	if key==name:
	# 		itm=np.array(value[0].split())
	return values

def getSyst(lists):
	syst=OrderedDict()
	# print getDic(lists,'bin')
	reg     = getDic(lists,'bin')[0].split(':')[0]
	length  = int(getDic(lists,'bin')[0].split(':')[1])
	nuis    = getDic(lists,'Nuisances')
	unc     = getDic(lists,'SystUnclnN')
	for n, u in zip(nuis,unc):
		# print 'testing ', n , u
		syst[str(n)]=[u] * length

	return syst




def getProcSyst(lists):
	nuisancesForCard=OrderedDict()
	# print 'testing ', lists
	NuisForProc = lists['NuisForProc']
	uncertainties  = lists['UnclnN']
	procs   = getDic(lists,'Process')

	# print 'NuisForProc',NuisForProc
	for ij, istring in enumerate(uncertainties):
		nuis = istring.split()[0]
		syst = istring.split()[1]
		# print 'nuis, syst',nuis, syst
		values=[]
		if syst=='shape':values.append('shape')
		else:values.append('lnN')
		
		for proc in procs:
			# print nuis,NuisForProc[ij]

			if proc in  (NuisForProc[ij])[nuis]:
				if syst=='shape':
					values.append(1)
				else:
					values.append(syst)
			else:values.append('-')
		nuisancesForCard[nuis]=values

	# print ('nuisancesForCard', nuisancesForCard)
	return nuisancesForCard





def getbinProcRate(lists):
	binProcRate = OrderedDict()
	reg     = getDic(lists,'bin')[0].split(':')[0]
	length  = int(getDic(lists,'bin')[0].split(':')[1])
	procs   = getDic(lists,'Process')
	procs1  = getDic(lists,'process1')
        rates =  getDic(lists,'rate')
#	rates   = [getDic(lists,'rate')[0].split(':')[0]] * length

	binProcRate['bin']      =  [reg] * length
	binProcRate['process']  =  procs
	binProcRate['process1'] =  procs1
	binProcRate['rate']     = rates
	# print 'binProcRate', binProcRate

	# print (lists['rateTest'])

	return binProcRate

def getProcRate(lists):
	binProcRate = OrderedDict()
	reg     = getDic(lists,'bin')[0].split(':')[0]
	length  = int(getDic(lists,'bin')[0].split(':')[1])
	procs   = getDic(lists,'Process')
	procs1  = getDic(lists,'process1')
        rates =  getDic(lists,'rate')
	#rates   = [getDic(lists,'rate')[0].split(':')[0]] * length

	# binProcRate['bin']      =  [reg] * length
	# binProcRate['process']  =  procs
	binProcRate['process'] =  procs1
	binProcRate['rate']     = rates
	# print 'binProcRate', binProcRate

	# print (lists['rateTest'])

	return binProcRate


def getSignalHists(doc,model):
	parameters = doc[model]
	print ("parameters   :  %s"%parameters)
	samples  = []
	if model=="THDMa":
		tb_list  = parameters[0]['tb']
		st_list  = parameters[1]['st']
		ma_list  = parameters[2]['ma']
		mA_list  = parameters[3]['mA']

		# for tb in tb_list:
		# 	for st in st_list:
		# 		for ma in ma_list:
		# 			for mA in mA_list:
		# 				# print ('tb',tb,'st',st,'ma',ma,'mA',mA)
		# 				samp = 'ggF_sp_'+st+'_tb_'+tb+'_mXd_10_mA_'+str(mA)+'_ma_'+str(ma)
		# 				samples.append(samp)

		for ma in ma_list:
			for tb in tb_list:
				if int(ma)==350 or int(ma)==200:continue
				mA='600'
				st='0p35'
				samp = 'ggF_sp_'+st+'_tb_'+tb+'_mXd_10_mA_'+str(mA)+'_ma_'+str(ma)
				samples.append(samp)
			for st in st_list:
				if int(ma)!=200:continue
				mA='600'
				tb='1p0'
				samp = 'ggF_sp_'+st+'_tb_'+tb+'_mXd_10_mA_'+str(mA)+'_ma_'+str(ma)
				samples.append(samp)
			for mA in mA_list:
				if int(ma)==200:continue
				st='0p35'
				tb='1p0'
				samp = 'ggF_sp_'+st+'_tb_'+tb+'_mXd_10_mA_'+str(mA)+'_ma_'+str(ma)
				samples.append(samp)





	elif model=="ZpB":
		mchi_list = parameters[0]['mchi']
		mzp_list  = parameters[1]['mzp']
		for mzp in mzp_list:
			for mchi in mchi_list:
				isfill = False
				if  (int(mzp)==100 and (int(mchi)==1 or int(mchi)==50)):isfill=True
				if  (int(mzp)==200 and (int(mchi)==1 or int(mchi)==50 or int(mchi)==100 or int(mchi)==150)):isfill=True
				if  (int(mzp)==300 and int(mchi)==150):isfill=True
				if  (int(mzp)==350 and int(mchi)==50):isfill=True
				if  (int(mzp)==500 and (int(mchi)==1 or int(mchi)==100 or int(mchi)==200 or int(mchi)==400)):isfill=True
				if  (int(mzp)==650 and int(mchi)==50):isfill=True
				if  (int(mzp)==800 and int(mchi)==50):isfill=True
				if  (int(mzp)==1000 and (int(mchi)==1 or int(mchi)==100 or int(mchi)==200 or int(mchi)==400 or int(mchi)==600 or int(mchi)==800)):isfill=True
				if  (int(mzp)==1500 and (int(mchi)==1 or int(mchi)==100 or int(mchi)==200 or int(mchi)==400 or int(mchi)==600 or int(mchi)==800)):isfill=True
				if  (int(mzp)==2000 and (int(mchi)==1 or int(mchi)==100 or int(mchi)==200 or int(mchi)==400 or int(mchi)==600 or int(mchi)==800)):isfill=True
				if  (int(mzp)==2500 and (int(mchi)==1 or int(mchi)==100 or int(mchi)==200 or int(mchi)==400 or int(mchi)==600 or int(mchi)==800)):isfill=True
				if  (int(mzp)==3000 and (int(mchi)==1 or int(mchi)==100 or int(mchi)==200 )):isfill=True
				if  (int(mzp)==3500 and (int(mchi)==1 or int(mchi)==100)):isfill=True

				if isfill:
					samp = 'MZp_'+str(mzp)+'_Mchi_'+str(mchi)
					samples.append(samp)

	elif model=="ZpTHDM":
		mA_list = parameters[0]['mA']
		mzp_list  = parameters[1]['mzp']
		for mzp in mzp_list:
			for mA in mA_list:
				# print (mA,mzp)
				isfill=False
				if  (int(mzp)==1000 and (int(mA)==300 or int(mA)==800)):isfill=True
				if (int(mzp)==1200 and (int(mA)==300 or int(mA)==500 or int(mA)==900 or int(mA)==1000)):isfill=True
				if (int(mzp)==1400 and (int(mA)==300 or int(mA)==400 or int(mA)==500 or int(mA)==600 or int(mA)==800 or int(mA)==900 or int(mA)==1000 or int(mA)==1200)) :isfill=True
				if (int(mzp)==1700 and (int(mA)==300 or int(mA)==400 or int(mA)==500 or int(mA)==600 or int(mA)==700 or int(mA)==800 or int(mA)==900 or int(mA)==1000 or int(mA)==1200 or int(mA)==1400)) :isfill=True
				if (int(mzp)==2000 and (int(mA)==300 or int(mA)==700 or int(mA)==1000 or int(mA)==1200 or int(mA)==1400 or int(mA)==1600)):isfill=True
				if (int(mzp)==2500 and (int(mA)==300 or int(mA)==400 or int(mA)==500 or int(mA)==600 or int(mA)==700 or int(mA)==1000 or int(mA)==1200 or int(mA)==1600)):isfill=True
				if isfill:
					samp = 'MZp'+str(mzp)+'_MA0'+str(mA)
					samples.append(samp)
	print ("samples  ",samples)
	print ("total samples   ",len(samples))


	return samples




'''
=======================
START WRITING DATACARDS
=======================
'''


for reg in regions:

	# print getSyst(doc.items())
	# print (doc[reg])
	if reg=='SR':
		
		for sigHist in getSignalHists(signalDoc,modelName):

			outputfile = 'monoHbb_datacard_'+year+'_'+reg+'_'+category+'_'+sigHist+'.txt'
			df0 = pd.DataFrame(getbinProcRate(doc[reg]))
			# df1 = pd.DataFrame(getProcRate(doc[reg]))
			df0['process'] = df0['process'].replace(['signal'],sigHist)



			# df =  pd.DataFrame(getSyst(doc))
			df =  pd.DataFrame(getProcSyst(doc[reg]))
			# df = pd.merge(df0,df1)

			fout = open(outdir+'/'+outputfile,'w')
			p0 = df0.T.to_string(justify='right',index=True, header=False)
			# p1 = df1.T.to_string(justify='right',index=True, header=False)
			p = df.T.to_string(justify='right',index=True,header=False)

			part1 = top_
			part2 = getUpperPart2(reg,category)
			part3 = getUpperPart3(reg)
                        part4 = getEndPart(reg)
			fout.write(part1+'\n')
			fout.write('------------'+'\n')
			fout.write(part2+'\n')
			fout.write('------------'+'\n')
			fout.write(part3+'\n')
			fout.write('observation -1'+'\n')
			fout.write('------------'+'\n')
			fout.write(p0+'\n')
			# fout.write(p1+'\n')
			fout.write('------------'+'\n')
			fout.write(p+'\n')
                        fout.write(part4+'\n')
			fout.close()

	else:
		outputfile = 'monoHbb_datacard_'+year+'_'+reg+'_'+category+'.txt'
		df0 = pd.DataFrame(getbinProcRate(doc[reg]))
		# df1 = pd.DataFrame(getProcRate(doc[reg]))
		df0['process'] = df0['process'].replace(['signal'],sigHist)



		# df =  pd.DataFrame(getSyst(doc))
		df =  pd.DataFrame(getProcSyst(doc[reg]))
		# df = pd.merge(df0,df1)

		fout = open(outdir+'/'+outputfile,'w')
		p0 = df0.T.to_string(justify='right',index=True, header=False)
		# p1 = df1.T.to_string(justify='right',index=True, header=False)
		p = df.T.to_string(justify='right',index=True,header=False)

		part1 = top_
		part2 = getUpperPart2(reg,category)
		part3 = getUpperPart3(reg)
                part4 = getEndPart(reg)
		fout.write(part1+'\n')
		fout.write('------------'+'\n')
		fout.write(part2+'\n')
		fout.write('------------'+'\n')
		fout.write(part3+'\n')
		fout.write('observation -1'+'\n')
		fout.write('------------'+'\n')
		fout.write(p0+'\n')
		# fout.write(p1+'\n')
		fout.write('------------'+'\n')
		fout.write(p+'\n')
                fout.write(part4+'\n')
		fout.close()

'''
============================
replace process1 with process
============================
'''


os.system("sed -i'.bak' 's/process1/process /g' "+outdir+"/*")
os.system("sed -i'.bak' 's/YEAR/"+year+"/g' "+outdir+"/*")
os.system("rm -rf "+outdir+"/*bak")



#combine datacards now


iregion=[]

#allregions.append(rl.TextFileToList(iregion))		 

modelRename =''

if modelName == 'THDMa' :
    modelRename = '2hdma'


monohbb_file='monohbb'+year+'_datacardslist_'+category+'_'+'allregion_'+modelRename+'_all.txt'
monohbb_file_SR='monohbb'+year+'_datacardslist_'+category+'_'+'SR_'+modelRename+'_all.txt'
#monohbb_file='monohbb'+year+'_datacardslist_'+category+'_'+modelName+'_all.txt'

#monoHbb2017_R_SR_ggF_sp_0p8_tb_1p0_mXd_10_mA_600_ma_200



ftxt = open(monohbb_file,'w')
ftxt_SR= open(monohbb_file_SR,'w')
for sigHist in getSignalHists(signalDoc,modelName):
    outfile_SR = 'monoHbb'+year+'_'+category+'_SR_'+sigHist
    srfile = 'monoHbb_datacard_'+year+'_SR_'+category+'_'+sigHist+'.txt'
    outfile= 'monoHbb_datacard_'+year+'_'+modelRename+'_'+category+'_allregion_'+sigHist+'.txt'
    # os.system('combineCards.py sr='+outdir+'/'+srfile+' zee='+outdir+'/monoHbb_datacard_2017_ZEE_R.txt  zmumu='+outdir+'/monoHbb_datacard_2017_ZMUMU_R.txt wmu='+outdir+'/monoHbb_datacard_2017_WMU_R.txt we='+outdir+'/monoHbb_datacard_2017_WE_R.txt topmu='+outdir+'/monoHbb_datacard_2017_TOPMU_R.txt tope='+outdir+'/monoHbb_datacard_2017_TOPE_R.txt >'+outdir+'/'+outfile)
    os.system('combineCards.py sr='+outdir+'/'+srfile+' zee='+outdir+'/monoHbb_datacard_2017_ZEE_'+category+'.txt  zmumu='+outdir+'/monoHbb_datacard_2017_ZMUMU_'+category+'.txt topmu='+outdir+'/monoHbb_datacard_2017_TOPMU_'+category+'.txt tope='+outdir+'/monoHbb_datacard_2017_TOPE_'+category+'.txt >'+outdir+'/'+outfile)
    ftxt.write(outdir+'/'+outfile+' \n')
    ftxt_SR.write(outfile_SR+'\n')
    
ftxt.close()
ftxt_SR.close()
    
#print(iregion)


    
