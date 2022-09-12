# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 10:54:22 2022

@author: Hagen Arhelger

Just a general DM + barcode scanning tool
"""
#% Loading dependencies, setting up environment
import os, time, cv2, biip
from pyzbar.pyzbar import decode as bar_decode
from pylibdmtx.pylibdmtx import decode as dm_decode #Found PyStrich, actual library with the relevant functions
#%%
start_time = time.time()
print('Start identification process of image, please bear with us.')
files = [f for f in os.listdir(os.curdir) if os.path.isfile(f) and f.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')) ]
files.sort()
index_files = {i: files[i] for i in range(0, len(files))}
target_ID = ''
for i in index_files:
        print(i, index_files[i])
while target_ID == '':
    target_ID = input('Using the index number, which image to decode?: ')
    if target_ID.isalpha() or int(target_ID) > len(files):
        print('Please enter valid ID for import target.')
        target_ID = ''
target = index_files[int(target_ID)]
start_time = time.time()
print('Starting decoding process, please bear with the computer/code.')
image = cv2.imread(f'{target}')
result = dm_decode(image, timeout=6000) # Try decode by dm and then bar
if len(result) != 0:
    code_type = 'datamatrix'
else:
    result = bar_decode(image)
    code_type = 'bar'
print(f'{result}')
print(f'\nDecoding process identified {len(result)} code(s)')
print("Decoding completed in ~%s seconds" % int(time.time() - start_time))

# loop over the detected barcodes
for barcode in result:
 	# extract the bounding box location of the barcode and draw the
 	# bounding box surrounding the barcode on the image
 	(x, y, w, h) = barcode.rect
 	cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
 	# the barcode data is a bytes object so if we want to draw it on
 	# our output image we need to convert it to a string first
 	barcodeData = barcode.data.decode("utf-8")
 	barcodeType = barcode.type
 	# draw the barcode data and barcode type on the image
 	text = "{} ({})".format(barcodeData, barcodeType)
 	cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.5, (0, 0, 255), 2)
 	# print the barcode type and data to the terminal
 	print("\n[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
# show the output image
# cv2.imshow("Image", image)

for i in result:
    try:
        GS1_result = biip.parse(i.data.decode('utf-8'))
        print("")
        print(GS1_result.gs1_message)
    except:
        print("")
        print(f'Unable to parse {i.data.decode("utf-8")}, not a GS1 Code')

#%%

individual_input = input('Input GS1 code here: ')

individual_result = biip.parse(individual_input)
print(individual_result)


#%% Output
# Input GS1 code here:0190027182008283320100071811210901210261878668
# ParseResult(value='0190027182008283320100071811210901210261878668',
#             symbology_identifier=None,
#             gtin=Gtin(value='90027182008283',
#                       format=GtinFormat.GTIN_14,
#                       prefix=GS1Prefix(value='002', usage='GS1 US'),
#                       payload='9002718200828',
#                       check_digit=3,
#                       packaging_level=9),
#             gtin_error=None,
#             upc=None,
#             upc_error="Failed to parse '0190027182008283320100071811210901210261878668' as UPC: Expected 6, 7, 8, or 12 digits, got 46.",
#             sscc=None,
#             sscc_error="Failed to parse '0190027182008283320100071811210901210261878668' as SSCC: Expected 18 digits, got 46.",
#             gs1_message=GS1Message(value='0190027182008283320100071811210901210261878668',
#                                    element_strings=[GS1ElementString(ai=GS1ApplicationIdentifier(ai='01',
#                                                                                                  description='Global Trade Item Number (GTIN)',
#                                                                                                  data_title='GTIN',
#                                                                                                  fnc1_required=False,
#                                                                                                  format='N2+N14'),
#                                                                      value='90027182008283', pattern_groups=['90027182008283'],
#                                                                      gtin=Gtin(value='90027182008283',
#                                                                                format=GtinFormat.GTIN_14,
#                                                                                prefix=GS1Prefix(value='002',
#                                                                                                 usage='GS1 US'),
#                                                                                payload='9002718200828',
#                                                                                check_digit=3,
#                                                                                packaging_level=9),
#                                                                      sscc=None,
#                                                                      date=None,
#                                                                      decimal=None,
#                                                                      money=None),
#                                                     GS1ElementString(ai=GS1ApplicationIdentifier(ai='3201',
#                                                                                                  description='Net weight, pounds (variable measure trade item)',
#                                                                                                  data_title='NET WEIGHT (lb)',
#                                                                                                  fnc1_required=False,
#                                                                                                  format='N4+N6'),
#                                                                      value='000718',
#                                                                      pattern_groups=['000718'],
#                                                                      gtin=None,
#                                                                      sscc=None,
#                                                                      date=None,
#                                                                      decimal=Decimal('71.8'),
#                                                                      money=None),
#                                                     GS1ElementString(ai=GS1ApplicationIdentifier(ai='11',
#                                                                                                  description='Production date (YYMMDD)',
#                                                                                                  data_title='PROD DATE',
#                                                                                                  fnc1_required=False,
#                                                                                                  format='N2+N6'),
#                                                                      value='210901',
#                                                                      pattern_groups=['210901'],
#                                                                      gtin=None,
#                                                                      sscc=None,
#                                                                      date=datetime.date(2021, 9, 1),
#                                                                      decimal=None,
#                                                                      money=None),
#                                                     GS1ElementString(ai=GS1ApplicationIdentifier(ai='21',
#                                                                                                  description='Serial number',
#                                                                                                  data_title='SERIAL',
#                                                                                                  fnc1_required=True,
#                                                                                                  format='N2+X..20'),
#                                                                      value='0261878668',
#                                                                      pattern_groups=['0261878668'],
#                                                                      gtin=None,
#                                                                      sscc=None,
#                                                                      date=None,
#                                                                      decimal=None,
#                                                                      money=None)]),
#             gs1_message_error=None)
