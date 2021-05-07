```
python tools/conv_cmap.py -c B5=cp950 -c UniCNS-UTF8=utf-8 pdfminer/cmap Adobe-CNS1 cmaprsrc/cmap-resources/Adobe-CNS1-7/cid2code.txt
python tools/conv_cmap.py -c GBK-EUC=cp936 -c UniGB-UTF8=utf-8 pdfminer/cmap Adobe-GB1 cmaprsrc/cmap-resources/Adobe-GB1-5/cid2code.txt
python tools/conv_cmap.py -c RKSJ=cp932 -c EUC=euc-jp -c UniJIS-UTF8=utf-8 pdfminer/cmap Adobe-Japan1 cmaprsrc/cmap-resources/Adobe-Japan1-7/cid2code.txt
python tools/conv_cmap.py -c KSC-EUC=euc-kr -c KSC-Johab=johab -c KSCms-UHC=cp949 -c UniKS-UTF8=utf-8 pdfminer/cmap cmaprsrc/cmap-resources/Adobe-Korea1-2/cid2code.txt
```