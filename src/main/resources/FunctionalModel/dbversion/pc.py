#!/Users/wanghaogang/Public/anaconda2/bin
# -*- coding: utf-8 -*-  
import os
import sys
from AR_Predictions import ar_predict
from pr import pr

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
status_path = os.path.join(BASE_DIR, 'uploads/status.txt')
status = open(status_path,'w')
status.write('wait')
status.close()
print("ar")
ar_predict()
print("pr")
pr()
print("end")
status = open(status_path,'w')
status.write('go')
print('go')
status.close()