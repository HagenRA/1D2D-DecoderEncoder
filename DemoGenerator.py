# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 11:22:48 2021
Generalising DotCodeGen to a more generic barcode scanning and prototyping script
Make sure is running within:
    C:\Users\Hagen Arhelger\Desktop\Current - Industrial\Industrial - Bulk Scanning Demo
How it differs from the regular type is that this is for a preset demo version without any product
packaging image and with preset dimensions and location

Specs:
    Printing onto the stickers on an A4 page:
        Sticker size L4677 (3.81cm x 6.35cm)
        Version 1 (1 DM code, 1 Bar code):
            GS1 Compliant DM Code (6mmx6mm)
            Expiry Date Information
            SKU (as well as in text form)
            *Barcode with SKU info*
        Version 2 (6 DM codes, all with same info):
            GS1 Compliant DM code
            Expiry Date Information
            Production Date Information
            SKU info
            Text: "SmartMore Demo Box"
@author: Hagen Arhelger
"""
#%% Loading dependencies, setting up environment
import random, string, os, shutil, time, cv2, biip
from pyzbar.pyzbar import decode as bar_decode
from pylibdmtx.pylibdmtx import decode as dm_decode #Found PyStrich, actual library with the relevant functions
import numpy as np
import pandas as pd
from pystrich.datamatrix import DataMatrixEncoder
# from pystrich.ean13 import EAN13Encoder
from pystrich.code128 import Code128Encoder
from PIL import Image, ImageDraw, ImageFont #, ImageOps
Image.MAX_IMAGE_PIXELS=1000000000
from fpdf import FPDF
from datetime import datetime

# Code generation
now = datetime.now()
dt_string = now.strftime("%Y.%m.%d")
src_dir = 'C:/Users/Hagen Arhelger/Desktop/Current - Industrial/Industrial - Bulk Scanning Demo/'

start_time = time.time()
Inventory = []

def GTIN_check_cal(i):
    multiplier = [1,3]
    times = ""
    total = 0
    for index, digit in enumerate(list(str(i))):
        total = total + int(digit)*multiplier[index%2]
        times = times+str(int(digit)*multiplier[index%2])+", "
        mof10 = total + (10 - total%10)
        checkdigit = mof10 - total
        if checkdigit ==10:
            checkdigit = 0
    return checkdigit

def random_date(seed):
    random.seed(seed)
    d = random.randint(1, int(time.time()))
    return datetime.fromtimestamp(d).strftime('%y%m%d')

for i in range(126):
    GTIN_13 = ''.join(random.choices(string.digits, k=12))
    random_date_pr = random_date(random.random())
    Inventory.append("010"+GTIN_13+''.join(str(GTIN_check_cal(GTIN_13)))+
                     "11"+''.join(random_date_pr)+
                     "10"+''.join(random.choices(string.ascii_uppercase + string.digits, k=6)))
print('Full Inventory List generated')
pagewidth = 196
pageheight = 266
#%
# PyStrich Encoder -> Code to DotMatrix (Unique Condition)
# encoder = DataMatrixEncoder(DotCode)
# encoder.save('DotCode.jpg')
# print(encoder.get_ascii())
j = 0
for i in Inventory:
    encoder = DataMatrixEncoder(i)
    name = str(j).zfill(3)
    encoder.save(f'{src_dir}{name}.jpg')
    j = j+1
    
#List generated files
files = [f for f in os.listdir(src_dir) if os.path.isfile(f) and f.endswith('.jpg')]

# PyStrich Encoder -> Code to DotMatrix (Repeated+Ratio Condition)

def constrained_sum_sample_pos(n, total):
    """Return a randomly chosen list of n positive integers summing to total.
    Each such list is equally likely to occur."""

    dividers = sorted(random.sample(range(1, total), n - 1))
    return [a - b for a, b in zip(dividers + [total], [0] + dividers)]

# rand_ratio = random.randint(2,10)
# test_case = constrained_sum_sample_pos(rand_ratio,126)

#Randomly select 2-10 barcodes for 
case = random.sample(files,21)

# Extract Code
case_code = list(np.array(Inventory)[[int(g) for g in list({s.replace('.jpg',"") for s in case})]])

#Gen Dataframe, pairing rand
case_ans = pd.DataFrame(data={'code': case_code, 'file':case, 'count': 1})

print('Repeat cases generated')

#Generate "Answer Key"

Inventory_df = pd.DataFrame(Inventory)
answer_key_list = {"Inventory": Inventory_df,
                   "case": case_ans}

writer = pd.ExcelWriter(f'{dt_string}_Answer_Key.xlsx', engine='xlsxwriter')

for k, v in answer_key_list.items():
    v.to_excel(writer, sheet_name=f'{k}')
    
writer.save()
print('Answer key generated')
#Output generation (Unique)

x_loc = 80
y_loc = 50
x_move = 80
y_move = 60

# Generate repeat cases
barcodebase = Image.open(src_dir + 'Base/L4677.jpg')
title_font = ImageFont.truetype(f"{src_dir}Roboto/Roboto-Black.ttf",size=18)
j=0
for i in case:
    barcode_add = Image.open(i).resize((50,50))
    barcode_out = barcodebase.copy()
    barcode_out.paste(barcode_add, (x_loc,y_loc))
    barcode_out.paste(barcode_add, (x_loc,y_loc+y_move))
    barcode_out.paste(barcode_add, (x_loc + x_move,y_loc))
    barcode_out.paste(barcode_add, (x_loc + x_move,y_loc+y_move))
    barcode_out.paste(barcode_add, (x_loc + 2*x_move,y_loc))
    barcode_out.paste(barcode_add, (x_loc + 2*x_move,y_loc+y_move))
    result = biip.parse(str(dm_decode(cv2.imread(f'{i}'))[0].data)[2:-1])
    GTIN = f'{result.gs1_message.element_strings[0].ai.data_title}: {result.gs1_message.element_strings[0].gtin.value}'
    prod = f'{result.gs1_message.element_strings[1].ai.data_title}: {result.gs1_message.element_strings[1].date}'
    batch = f'{result.gs1_message.element_strings[2].ai.data_title}: {result.gs1_message.element_strings[2].value}'
    title_text = f'SmartMore Demo Box\n{GTIN}\n{prod}\n{batch}'
    with barcode_out as im:
        draw = ImageDraw.Draw(im)
        draw.multiline_text((x_loc, y_loc+2*y_move-10), title_text, fill = (0,0,0),font=title_font, align='center')
        barcode_out.save(f'Repeat_{i}')
    j+=1

print('Matrix Codes all added onto sample image.')
print('Stitching of photos into columns started. (This could take a while)')
# Add layer where it is stitching onto each sticker before stitching into columns
#Photo stitching (Unique cases)
case = [f for f in os.listdir(src_dir) if os.path.isfile(f) and f.startswith('Repeat_')]
j = 0
while j < 21:
    col0 = np.array(case[j:j+7])
    imgs_col0 = [Image.open(k) for k in col0]
    imgs0 = Image.fromarray(np.vstack(imgs_col0))
    name = "RCol"+str(j)
    imgs0.save(f"{src_dir}Columns/{name}.jpg")
    j+=7

page_cols = (f"{src_dir}Columns/RCol0.jpg",f"{src_dir}Columns/RCol7.jpg",f"{src_dir}Columns/RCol14.jpg")
imgs_page = [Image.open(i) for i in np.array(page_cols)]
page = Image.fromarray(np.hstack(imgs_page))
page.save(f"{src_dir}Pages/Repeat_page.jpg")

# Export to pdf (Unique Cases)

pdf = FPDF(orientation = "P",unit='mm', format = 'A4')
Repeat_case = [f'{src_dir}Pages/Repeat_page.jpg']
for imageFile in Repeat_case:
    cover = Image.open(imageFile)
    pdf.add_page()
    pdf.image(imageFile, 7, 15, pagewidth, pageheight)
name = f'{dt_string}_Repeat_Codes.pdf'
pdf.output(name)
print(f'{name} created')

#Generate unique code pages
print('Cleaning up folders')
dest_dir = src_dir+'/Individual'
cleanup = [f for f in os.listdir(src_dir) if os.path.isfile(f) and f.endswith('.jpg')]
for file_name in cleanup:
    src_file = os.path.join(src_dir, file_name)
    dst_file = os.path.join(dest_dir, file_name)
    if os.path.exists(dst_file):
        if os.path.samefile(src_file, dst_file):
            continue
        os.remove(dst_file)
    shutil.move(src_file, dest_dir)

j = 0
for i in Inventory:
    encoder = DataMatrixEncoder(i)
    name = str(j).zfill(3)
    encoder.save(f'{src_dir}{name}.jpg')
    j = j+1
    
#List generated files
files = [f for f in os.listdir(src_dir) if os.path.isfile(f) and f.endswith('.jpg')]

i = 0
j = 0
for i in range(0,len(files),6):
    barcode_add = []
    for j in range(0,6):
        k=0
        k = i+j
        barcode_add.append(Image.open(files[k]).resize((50,50)))
    barcode_out = barcodebase.copy()
    barcode_out.paste(barcode_add[0], (x_loc,y_loc))
    barcode_out.paste(barcode_add[1], (x_loc,y_loc+y_move))
    barcode_out.paste(barcode_add[2], (x_loc + x_move,y_loc))
    barcode_out.paste(barcode_add[3], (x_loc + x_move,y_loc+y_move))
    barcode_out.paste(barcode_add[4], (x_loc + 2*x_move,y_loc))
    barcode_out.paste(barcode_add[5], (x_loc + 2*x_move,y_loc+y_move))
    title_text = 'SmartMore Demo Box'
    with barcode_out as im:
        draw = ImageDraw.Draw(im)
        draw.text((x_loc+10, y_loc+2*y_move), title_text, fill = (0,0,0),font=title_font, align='center')
        barcode_out.save(f'unique{i}.jpg')
    j+=1

case = [f for f in os.listdir(src_dir) if os.path.isfile(f) and f.startswith('unique')]
j = 0
k = 0
while j < 21:
    col0 = np.array(case[j:j+7])
    imgs_col0 = [Image.open(k) for k in col0]
    imgs0 = Image.fromarray(np.vstack(imgs_col0))
    name = "UCol"+str(j)
    imgs0.save(f"{src_dir}Columns/{name}.jpg")
    j+=7

page_cols = (f"{src_dir}Columns/UCol0.jpg",f"{src_dir}Columns/UCol7.jpg",f"{src_dir}Columns/UCol14.jpg")
imgs_page = [Image.open(i) for i in np.array(page_cols)]
page = Image.fromarray(np.hstack(imgs_page))
page.save(f"{src_dir}Pages/Unique_page.jpg")

# Export to pdf (Unique Cases)

pdf = FPDF(orientation = "P",unit='mm', format = 'A4')
Unique_case = [f'{src_dir}Pages/Unique_page.jpg']
for imageFile in Unique_case:
    cover = Image.open(imageFile)
    pdf.add_page()
    pdf.image(imageFile, 7, 15, pagewidth, pageheight)
name = f'{dt_string}_Unique_Codes.pdf'
pdf.output(name)
print(f'{name} created')
   
print('All conditions created.')
print('Cleaning up folders')
dest_dir = src_dir+'/Individual'
cleanup = [f for f in os.listdir(src_dir) if os.path.isfile(f) and f.endswith('.jpg')]
for file_name in cleanup:
    src_file = os.path.join(src_dir, file_name)
    dst_file = os.path.join(dest_dir, file_name)
    if os.path.exists(dst_file):
        if os.path.samefile(src_file, dst_file):
            continue
        os.remove(dst_file)
    shutil.move(src_file, dest_dir)

#%
# Mixed Code generation
now = datetime.now()
dt_string = now.strftime("%Y.%m.%d")
src_dir = 'C:/Users/Hagen Arhelger/Desktop/Current - Industrial/Industrial - Bulk Scanning Demo/'

Inventory = []

for i in range(21):
    GTIN_13 = ''.join(random.choices(string.digits, k=12))
    Inventory.append(GTIN_13+''.join(str(GTIN_check_cal(GTIN_13))))

j = 0
for i in Inventory:
    name = str(j).zfill(3)
    bar_encoder = Code128Encoder(i)
    bar_encoder.save(f'{src_dir}/{name}_bar.jpg')
    j = j+1
    
for index, item in enumerate(Inventory):
    random_date_pr = random_date(random.random())
    Inventory[index] = "010"+item+"11"+''.join(random_date_pr)+"10"+''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

j = 0
for i in Inventory:
    name = str(j).zfill(3)
    dm_encoder = DataMatrixEncoder(i)
    dm_encoder.save(f'{src_dir}/{name}_dm.jpg')
    j = j+1

#List generated files
extension = '.jpg'
files = [f for f in os.listdir(src_dir) if os.path.isfile(f) and f.endswith(extension)]

x_loc = 50
y_loc = 70
x_move = 70
y_move = 70

# Generate repeat cases
barcodebase = Image.open(src_dir + 'Base/L4677.jpg')
title_font = ImageFont.truetype(f"{src_dir}Roboto/Roboto-Black.ttf",size=18)

i=0
l=0
k=0
for i in range(0, len(files), 2):
    barcode_add = []
    for j in range(0,2):
        k=0
        k = i+j
    # check if barcode or dm
        if '_dm.jpg' in files[k]:
            barcode_add.append(Image.open(files[k]).resize((50,50)))
        else:
            barcode_add.append(Image.open(files[k]).resize((340,65)))
    # Pair up the files based on names and paste them sequentially on the page, bar code on the top, dm code underneath
    barcode_out = barcodebase.copy()
    barcode_out.paste(barcode_add[0], (x_loc-30,y_loc)) #bar code
    barcode_out.paste(barcode_add[1], (x_loc,y_loc+y_move)) #dmr code
    title_text = 'SmartMore Mixed Demo Box'
    result = biip.parse(Inventory[l])
    GTIN = f'{result.gs1_message.element_strings[0].ai.data_title}: {result.gs1_message.element_strings[0].gtin.value}'
    prod = f'{result.gs1_message.element_strings[1].ai.data_title}: {result.gs1_message.element_strings[1].date}'
    batch = f'{result.gs1_message.element_strings[2].ai.data_title}: {result.gs1_message.element_strings[2].value}'
    title_text = f'SmartMore Demo Box\n{GTIN}\n{prod}\n{batch}'
    with barcode_out as im:
        draw = ImageDraw.Draw(im)
        draw.multiline_text((x_loc+x_move, y_loc+y_move), title_text, fill = (0,0,0),font=title_font, align='center')
        barcode_out.save(f'{src_dir}Mixed_{l}.jpg')
    l+=1

# Stitch and generate pages for printing onto stickers and boxes
case = [f for f in os.listdir(src_dir) if os.path.isfile(f) and f.startswith('Mixed')]
j = 0
while j < 21:
    col0 = np.array(case[j:j+7])
    imgs_col0 = [Image.open(k) for k in col0]
    imgs0 = Image.fromarray(np.vstack(imgs_col0))
    name = "Mixed"+str(j)
    imgs0.save(f"{src_dir}Columns/{name}.jpg")
    j+=7

page_cols = (f"{src_dir}Columns/Mixed0.jpg",f"{src_dir}Columns/Mixed7.jpg",f"{src_dir}Columns/Mixed14.jpg")
imgs_page = [Image.open(i) for i in np.array(page_cols)]
page = Image.fromarray(np.hstack(imgs_page))
page.save(f"{src_dir}Pages/Mixed_page.jpg")

# Export to pdf (Unique Cases)

pdf = FPDF(orientation = "P",unit='mm', format = 'A4')
Unique_case = [f'{src_dir}Pages/Mixed_page.jpg']
for imageFile in Unique_case:
    cover = Image.open(imageFile)
    pdf.add_page()
    pdf.image(imageFile, 7, 15, pagewidth, pageheight)
name = f'{dt_string}_Mixed_Codes.pdf'
pdf.output(name)
print(f'{name} created')
#
print('All conditions created.')
print('Cleaning up folders')
dest_dir = src_dir+'/Individual'
cleanup = [f for f in os.listdir(src_dir) if os.path.isfile(f) and f.endswith('.jpg')]
for file_name in cleanup:
    src_file = os.path.join(src_dir, file_name)
    dst_file = os.path.join(dest_dir, file_name)
    if os.path.exists(dst_file):
        if os.path.samefile(src_file, dst_file):
            continue
        os.remove(dst_file)
    shutil.move(src_file, dest_dir)
    
print("Code generating process completed in ~%s seconds" % int(time.time() - start_time))

#%%
for i in Inventory:
    result = biip.parse(i)
    print(result.gs1_message)
    
