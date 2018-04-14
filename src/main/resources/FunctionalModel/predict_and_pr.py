#!/Users/wanghaogang/Applications/anaconda3/bin
# -*- coding: utf-8 -*-  
import os
import sys
from ar_predictions import ar_predict
from pr_and_save import pr

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
status_path = os.path.join(BASE_DIR, 'uploads/status.txt')
status = open(status_path,'w')
status.write('wait')
status.close()
print("ar")
ar_predict()
download_path = os.path.join(BASE_DIR, 'uploads/file.txt')
download_status = open(download_path, 'w')
download_status.write('download')
download_status.close()
print("pr")
pr()
print("end")
status = open(status_path,'w')
status.write('go')
print('go')
status.close()