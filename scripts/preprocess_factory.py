#!/bin/env python
# This script removed ASM(4-bytes), VCDU Header(17-bytes) at front of each
# VCDU packet(1028-bytes) and CRC(2-bytes) at the end of VCDU packet.
# Keep 1005-bytes after VCDU Header and before CRC. 

import os
import os.path
import sys
import struct
import re
import datetime
import argparse
import glob

was_truncated = []

CRC_TABLE = [0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5,
             0x60c6, 0x70e7, 0x8108, 0x9129, 0xa14a, 0xb16b,
             0xc18c, 0xd1ad, 0xe1ce, 0xf1ef, 0x1231, 0x0210,
             0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
             0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c,
             0xf3ff, 0xe3de, 0x2462, 0x3443, 0x0420, 0x1401,
             0x64e6, 0x74c7, 0x44a4, 0x5485, 0xa56a, 0xb54b,
             0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
             0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6,
             0x5695, 0x46b4, 0xb75b, 0xa77a, 0x9719, 0x8738,
             0xf7df, 0xe7fe, 0xd79d, 0xc7bc, 0x48c4, 0x58e5,
             0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
             0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969,
             0xa90a, 0xb92b, 0x5af5, 0x4ad4, 0x7ab7, 0x6a96,
             0x1a71, 0x0a50, 0x3a33, 0x2a12, 0xdbfd, 0xcbdc,
             0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
             0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03,
             0x0c60, 0x1c41, 0xedae, 0xfd8f, 0xcdec, 0xddcd,
             0xad2a, 0xbd0b, 0x8d68, 0x9d49, 0x7e97, 0x6eb6,
             0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
             0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a,
             0x9f59, 0x8f78, 0x9188, 0x81a9, 0xb1ca, 0xa1eb,
             0xd10c, 0xc12d, 0xf14e, 0xe16f, 0x1080, 0x00a1,
             0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
             0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c,
             0xe37f, 0xf35e, 0x02b1, 0x1290, 0x22f3, 0x32d2,
             0x4235, 0x5214, 0x6277, 0x7256, 0xb5ea, 0xa5cb,
             0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
             0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447,
             0x5424, 0x4405, 0xa7db, 0xb7fa, 0x8799, 0x97b8,
             0xe75f, 0xf77e, 0xc71d, 0xd73c, 0x26d3, 0x36f2,
             0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
             0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9,
             0xb98a, 0xa9ab, 0x5844, 0x4865, 0x7806, 0x6827,
             0x18c0, 0x08e1, 0x3882, 0x28a3, 0xcb7d, 0xdb5c,
             0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
             0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0,
             0x2ab3, 0x3a92, 0xfd2e, 0xed0f, 0xdd6c, 0xcd4d,
             0xbdaa, 0xad8b, 0x9de8, 0x8dc9, 0x7c26, 0x6c07,
             0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
             0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba,
             0x8fd9, 0x9ff8, 0x6e17, 0x7e36, 0x4e55, 0x5e74,
             0x2e93, 0x3eb2, 0x0ed1, 0x1ef0]



def convert_year_doy2_date(year, doy):
      return datetime.datetime(year, 1, 1) + datetime.timedelta(doy - 1)


def remove_vcdu_hdr(fileName, outfile):

    sage_offset = 0
    file_size = (os.stat(fileName)).st_size
    last_left_size = 1006   
    data_size = 1005
    data_and_crc_size = 1007
    vcdu_header = 21 
    
    f = open(fileName, "rb")
    num = list(f.read())
    
    new_num =[]
    f.close()
    
    i = 0
    while i < file_size - last_left_size:
         if ((num[i+sage_offset]=='\x1a') and (num[i+1+sage_offset]=='\xcf')):

              i = i + vcdu_header
              new_num.extend(num[i:i+data_size])
              i = i + data_and_crc_size
         else:
             print " Something wrong!"
             return
             
    fw = open(outfile, 'w+b')
    binary_fmt = bytearray(new_num)
    fw.write(binary_fmt)
    fw.close()



####################################################################
####################################################################
####################################################################
####################################################################
# The input file is a removed vcdu headers binary file.
# Use remove_vcdu_headers.py at first for vcdu_rfoe021_0926.bin
# Find 1st event packet, then if it is a sequence packets, remove 
# SpaceWirePreamble, Primary Header, Secondary Header, rfs_event_header and
# CRC. Only keey time series packets for the following sequence packets.


def crc_16_ccitt(vals):
    """
    Reference:
      http://automationwiki.com/index.php/CRC-16-CCITT
    """
    import ctypes

  
    data = bytearray(vals)

    seed  = 0xffff
    final = 0x0000

    crc = seed

    for x in data:
        temp = ( x ^ (crc >> 8) ) & 0xff
        crc  = CRC_TABLE[temp] ^ (crc << 8)

        crc = ctypes.c_ushort(crc).value

    return ctypes.c_ushort(crc ^ final).value

# -- ENDs crc_16_ccitt()


def parse_event(i, num, new_num, pkt_len_idx_arr, pkt_len_arr, sys, sub_sys, pkt_len_dict):
    # i is the index of preamble_byte1 = \xe0
    binary_fmt = bytearray( num[i+4:i+5])
    sequence_flag = binary_fmt[0]>>6
    count = 0
    for_truncated_use = len(new_num)

    if sequence_flag == 1:
         count = 1

         n = num[i+6] + num[i+7]
         pkt_len = int(n.encode('hex'),16)

         pkt_idx = len(new_num) + 6
         total_pkt_len = pkt_len

         while not (num[i+2]=='\xe0' and num[i+3]=='\xf0'):
             new_num.extend(num[i])
             i = i+1
         # i is the index of crc bytes  when out of loop
         i = i+2       # i is next preamble_byte1

         binary_fmt = bytearray( num[i+4:i+5])
         sequence_flag = binary_fmt[0]>>6         #sequence_flag should be 0
         while (sequence_flag == 0 ):
            count = count +1

            if (num[i]=='\xe0' and num[i+1]=='\xf0'):
                frame_start = i

                n = num[i+6] + num[i+7]
                pkt_len = int(n.encode('hex'),16)
                total_pkt_len = total_pkt_len + (pkt_len -2-6-13-2)

                i = i + 21  # skip preamble(2-bytes), primaryHdr(6-bytes), 2ndHdr(13-bytes). time_sample starts here

                while (not ((num[i+2]=='\xe0' and num[i+3]=='\xf0')and (num[i+9+2]==sys and num[i+10+2]==sub_sys))) :
                    new_num.extend(num[i])
                    i = i+1
                    j = i+12
                    if j >len(num):

                       return i, new_num, pkt_len_idx_arr, pkt_len_arr

                # i is at crc_byte1

                #check frame checksum vs pre-checksum (crc bytes)
                crc_byte_stream = num[i]+num[i+1]
                crc = int(crc_byte_stream.encode('hex'),16)
                frame_stream = num[frame_start+2:i]
                frame_val = crc_16_ccitt(frame_stream)
                if frame_val != crc:
                    print "------Wrong CRC, shouldn't get here----"

                i = i+2    # next preamble_byte1
                binary_fmt = bytearray( num[i+4:i+5])
                sequence_flag = binary_fmt[0]>>6

         if sequence_flag == 2:
               count = count +1
               
               last_frame_start  = i    # last sequnece frame preamble_byte1

               n = num[i+6] + num[i+7]
               pkt_len = int(n.encode('hex'),16)

               i = i + 21  # skip preamble(2-bytes), primaryHdr(6-bytes), 2ndHdr(13-bytes). time_sample starts here
      
               last_seq_frame_len = 0
               #while (not ((num[i+2]=='\xe0' and num[i+3]=='\xf0')) and (not(num[i+2] =='0' and num[i+3] =='\xf0'))) :
               while (not ((num[i+2]=='\xe0' and num[i+3]=='\xf0') and (num[i+4] == '\x08' and num[i+5]=='\x60')) and \
                      not ((num[i+2]=='\xe0' and num[i+3]=='\xf0') and (num[i+4] == '\x08' and num[i+5]=='\x40')) and \
                      not ((num[i+2]=='\xe0' and num[i+3]=='\xf0') and (num[i+4] == '\x08' and num[i+5]=='\x20')) and \
                      (not(num[i+2] =='0' and num[i+3] =='\xf0'))) :

                    new_num.extend(num[i])
                    i = i+1
                    last_seq_frame_len =  last_seq_frame_len + 1

               # now, i = indx of CRC_byte1
               crc_byte_stream = num[i]+num[i+1]
               crc = int(crc_byte_stream.encode('hex'),16)
   
               last_seq_byte_stream = num[last_frame_start+2:i]
               # covers bytes from 1st byte after preamble_byte2 to the one before CRC_byte1
               frame_val = crc_16_ccitt(last_seq_byte_stream)


               if crc != frame_val:
		    was_truncated.append( for_truncated_use)
      
               i = i+2
               if last_seq_frame_len < pkt_len:
                     total_pkt_len = total_pkt_len + last_seq_frame_len
               else:
                     total_pkt_len = total_pkt_len + pkt_len

               
         pkt_len_idx_arr.append(pkt_idx)
         pkt_len_arr.append(total_pkt_len)
         pkt_len_dict.update({pkt_idx:total_pkt_len})
     
    else:
         new_num.extend(num[i])
         i = i+1
         while(not (num[i]=='\xe0' and num[i+1]=='\xf0')):
                 new_num.extend(num[i])
                 i = i+1

    return i, new_num, pkt_len_idx_arr, pkt_len_arr
     

 
def combine_frames(fileName, outfile):

    f = open(fileName, "rb")
    num = list(f.read())
    f.close()
    
    i = 0
    new_num =[]
    pkt_len_idx_arr=[]
    pkt_len_arr = []
    pkt_len_dict={}
    h_count = 0
    l_count = 0
    
    while i < (len(num)):
        if ((num[i] =='\xe0') and (num[i+1]=='\xf0')):
            if (num[i+21] == '\xeb') and (num[i+22] == '\x90'):
                if ( num[i+9]=='\xc6' and num[i+10]=='\x01'):    
           
                    h_count = h_count + 1
    
                    i, new_num, pkt_len_idx_arr, pkt_len_arr =  parse_event(i, num, new_num, pkt_len_idx_arr, pkt_len_arr,'\xc6','\x01', pkt_len_dict)
                elif ( num[i+9]=='\xc6' and num[i+10]=='\x02') and ( num[i+24]=='\x1a') :    
                     # EMP_DIAG and LOW_Event almost have all the same hdr information.
                     # Use frame_id == \x1a is Low_event, frame_id ==\x17 is EMP_DIAG
                     l_count = l_count + 1
    
                     i, new_num, pkt_len_idx_arr, pkt_len_arr =  parse_event(i, num, new_num, pkt_len_idx_arr, pkt_len_arr,'\xc6','\x02', pkt_len_dict)
    
                else:
                     new_num.extend(num[i])
                     i = i+1
            else:
                new_num.extend(num[i])
                i = i+1
        else:
            new_num.extend(num[i])
            i = i+1
    
    
    #insert two-bytes for pkt_length field
    del num
    num = new_num
    new_num = []
    
    max_pkt_len = 0 
    if len(pkt_len_dict.values()):
          max_pkt_len= max(pkt_len_dict.values())
    
    i = 0
    
    while i < len(num):
         truncated_flag = 0
         for_truncated = i
         #print "------ 275---", i, len(num)
    
         if ((num[i]=='\xe0' and num[i+1]=='\xf0') and num[i+9]=='\xc6' and ((num[i+10]=='\x01') or num[i+10]=='\x02'))  or \
            (num[i]=='\xe0' and num[i+1]=='\xf0' and num[i+9]=='\xc4' and num[i+10]=='\x03')  or \
            (num[i]=='0' and num[i+1]=='\xf0' and num[i+9]=='\xc4' and num[i+10]=='\x01'):
          
             n = num[i+6] + num[i+7]
             pkt_len = int(n.encode('hex'),16)
             # pkt_len is number of bytes from 1st byte after pkt_len(or after primary_header)
             # to the byte before 1st crc byte.
    
             new_num.extend(num[i:i+6])
             i = i+6
    
             if pkt_len <= max_pkt_len:                   
                 #new_num.extend(num[i:i+6])
                 #i = i+6
                 if i in pkt_len_dict.keys():
                        pkt_len = pkt_len_dict[i]
                        del pkt_len_dict[i]
    
                 if for_truncated in was_truncated:              # for HIGHBAND_EVENT and lOWBAND_EVENT
                        truncated_flag = 1                       # was_truncated was checked in parse_event
    
             if (num[i+15]=='\xeb' and num[i+16]=='\x90') and (num[i+19]=='\x0e' or num[i+19]== '\x0f'):
                            # for EMP_SOH and RPP_SOH, check was_truncated
                            # use sync bytes and frame_id to check if packet is EMP_SOH or APP_SOH
                            frame_stream = num[i-6+2 : i+pkt_len+1]    # i is the 1st idx of pkt_len
                            frame_val = crc_16_ccitt(frame_stream)
                            if (i+pkt_len+1 >len(num)) or (i+pkt_len +2 >len(num)):
                               crc_byte_stream = num[-2] + num[-1]
                            else:
                               crc_byte_stream = num[i+pkt_len+1] + num[i+pkt_len+2]
    
                            crc = int(crc_byte_stream.encode('hex'),16)
                            if frame_val != crc:
                              truncated_flag = 1                      
    
             pnum = tuple(struct.pack('I', int(pkt_len)))
             new_num.extend(pnum[3])
             new_num.extend(pnum[2])
             new_num.extend(pnum[1])
             new_num.extend(pnum[0])
                 
             pnum = tuple(struct.pack('I', int(truncated_flag)))
             new_num.extend(pnum[0])          # insert one-byte was_truncated flag
    
             i = i+2
         else:
             new_num.extend(num[i])
             i = i + 1
    
         
    
    fw = open(outfile, 'w+b')
    binary_fmt = bytearray(new_num)
    fw.write(binary_fmt)
    fw.close()



#======================= Main ===========================================
input_path = "/projects/senser/data/rfs/ptm/"
sage_flists = os.listdir(input_path)
#scratch_path = "/projects/sdn/scratch/"
scratch_path = "/projects/sdnprod/scratch/rfs/ptm/"
# vcdu_rfoe0x21_2020-09-01_15_27_00.bin
parser = argparse.ArgumentParser(description='SAGE Preprocesser')
parser.add_argument('--outpath', help='output directory')
parser.add_argument('--log', help='path for logs')
parser.add_argument('files', nargs='*', help='input file/output file')
args = parser.parse_args()
input_file = args.files[0].split(' ')
input_path = os.path.dirname(input_file[0])
input_files = sorted(glob.glob(os.path.join(input_path, os.path.basename(input_file[0])[:4]+"*")))

     
for each_sage in input_files:

    if not os.path.isfile(each_sage):    # skip a directory
        continue
    m = re.match(r'.*(\d{4})-(\d{2})-(\d{2})_(\d{2})_(\d{2})_(\d{2}).*', os.path.basename(each_sage))
    year = m.group(1)
    month = m.group(2)
    day = m.group(3)
    hour  = m.group(4)
    minute = m.group(5)
    sec = m.group(6)
    hms = hour+minute+sec

    ubet_mon = month
    if ubet_mon < 10 :
        ubet_mon = '0' + str(ubet_mon)

    ubet_day = day
    if ubet_day < 10 :
        ubet_day = '0' + str(ubet_day)

    removed_vcdu_file = scratch_path + 'senser_xxxx_' + str(year) + str(ubet_mon) + str(ubet_day) + '_' + hms + '_SERN_VC33.1.0.0.ptm'
    ubet_fileName = args.outpath + '/' + os.path.basename(removed_vcdu_file)
     
    if os.path.isfile(ubet_fileName):
       print ubet_fileName, " exists already, skip it."
       continue
#       sys.exit(0)
    print "Preprocessing: ", each_sage
    remove_vcdu_hdr(each_sage, removed_vcdu_file)                 
    if not os.path.isfile(removed_vcdu_file):
        continue
    combine_frames(removed_vcdu_file, ubet_fileName)
    os.remove(removed_vcdu_file)
     
