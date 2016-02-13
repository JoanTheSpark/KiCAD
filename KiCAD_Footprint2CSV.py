# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- KiCAD local footprint repository parser
#--
#-- destructive, values it doesn't know will be
#-- lost when the footprint is written back 
#--
#-- Joan The Spark 2016
#--
#-- GNU General Public License 3+ (GPL3+)
#-------------------------------------------------

import os, sys, shutil, fileinput, re, copy

FLDR_toRepos = "E:/Data_KiCAD/_KiCAD_Footprints/" # local footprint repo root directory
FLDR_toCSV = "E:/Data_KiCAD/_KiCAD_Footprints/" # folder to save csv overview to
FNME_csv = "footprints_2016-02-11.csv" # csv overview file name

def FNC_get_repos(FLDR_toRepos):
    LST_repos = os.listdir(FLDR_toRepos)
    LST_repos_clean = []
    for FNME_repo in LST_repos:
        if os.path.isdir(FLDR_toRepos + FNME_repo) == 1: # test if folder or file..
            try:
                FNME_ext = FNME_repo.rsplit(".",1)[1]
            except:
                FNME_ext = ""
            if FNME_ext == "pretty": # test if repo
                LST_repos_clean.append(FNME_repo)
    return LST_repos_clean

def FNC_get_ftprts(FLDR_toFtPrts):
    LST_ftprts = os.listdir(FLDR_toFtPrts)
    LST_ftprts_clean = []
    for FNME_ftprt in LST_ftprts:
        if os.path.isfile(FLDR_toFtPrts + FNME_ftprt) == 1: # test if folder or file..
            try:
                FNME_ext = FNME_ftprt.rsplit(".",1)[1]
            except:
                FNME_ext = ""
            if FNME_ext == "kicad_mod": # test if footprint
                LST_ftprts_clean.append(FNME_ftprt)
    return LST_ftprts_clean
    
def FNC_read_file(PATH_tofile):
    try:
        HDLR_file = open(PATH_tofile, 'r') # open
    except:
        print "broken_1"
    else:
        HDLR_file.seek(0)
        BLOB_file = HDLR_file.readlines()
        HDLR_file.close()
    return BLOB_file

def FNC_convert_file(BLOB_file):
    STR_file = ""
    if len(BLOB_file):
        for line in BLOB_file:
            line = line.strip()
            if len(line) == 1: # no space before closing braket
                STR_file += line
            else: # all other cases
                STR_file += " "+line
    return STR_file

def FNC_get_next_level(STR_withBrakets):
    """Generate parenthesized contents in string as pairs (level, contents)."""
    LST_stack = []
    for i, c in enumerate(STR_withBrakets):
        if c == '(':
            LST_stack.append(i)
        elif c == ')' and LST_stack:
            start = LST_stack.pop()
            if len(LST_stack) == 1:
                yield (STR_withBrakets[start + 1: i])

def FNC_get_this_level(STR_withBrakets):
    """Generate parenthesized contents in string as pairs (level, contents)."""
    LST_stack = []
    LST_pos = []
    for i, c in enumerate(STR_withBrakets):
        if c == '(':
            LST_stack.append(i)
            if len(LST_stack) in [1,2]:
                LST_pos.append(i)
        elif c == ')' and LST_stack:
            if len(LST_stack) in [1,2]:
                LST_pos.append(i)
            start = LST_stack.pop()
        if len(LST_pos) == 2:
            end = LST_pos.pop()
            start = LST_pos.pop()
            STR_out = STR_withBrakets[start + 1 : end].strip()
            if len(STR_out):
                yield (STR_out)
    
def FNC_write_csv(LST_ofLines, PATH_toCSV):
    try:
        HDLR_csvfile = open(PATH_toCSV, 'w') # open
    except:
        print "broken_2"
    else:
        for line in LST_ofLines:
            STR_line = '\t'.join(line)
            HDLR_csvfile.write(STR_line + "\n")
        HDLR_csvfile.close()
    return()
    
if __name__=='__main__':
   
#          <id>,<searchstr>,<#-splits>,<pos>,<depth>,<extra>
    check = [[('MOD',r'^\bmodule\b',-1,1,0),
              ('STS',r'\blocked\b$',-1,2,0),
             ],
             [('FOB',r'^\blayer\b',1,1,0,()),
              ('DOC',r'^\bdescr\b',1,1,0,()),
              ('KEY',r'^\btags\b',1,1,0,()),
              ('A09',r'^\bautoplace_cost90\b',1,1,0,()),
              ('A18',r'^\bautoplace_cost180\b',1,1,0,()),
              ('MSK',r'^\bsolder_mask_margin\b',1,1,0,()),
              ('PMG',r'^\bsolder_paste_margin\b',1,1,0,()),
              ('PRT',r'^\bsolder_paste_ratio\b',1,1,0,()),
              ('CLR',r'^\bclearance\b',1,1,0,()),
              ('ATR',r'^\battr\b',1,1,0,()),
              ('REF',r'^\bfp_text reference\b',-1,2,1,('VIS',r'\bhide\b$')),
              ('VAL',r'^\bfp_text value\b',-1,2,1,('VIS',r'\bhide\b$')),
              ('3DM',r'^\bmodel\b',1,1,1,()),
             ],
             [('EFT',r'^\beffects\b',-1,0,1,0),
              ('POS',r'^\bat\b',     -1,1,0,'XYA'),
              ('LYR',r'^\blayer\b',   1,1,0,1),
              ('POS',r'^\bat\b',     -1,0,1,0),
              ('SCL',r'^\bscale\b',  -1,0,1,0),
              ('ROT',r'^\brotate\b', -1,0,1,0),
             ],
             [('FNT',r'^\bfont\b',-1,1,1,r'\bitalic\b$'),
              ('XYZ',r'^\bxyz\b',-1,1,0,'XYZ'),
             ],
             [('SIZ',r'^\bsize\b',-1,1,0,'HW'),
              ('THK',r'^\bthickness\b',-1,1,0,''),
             ],
            ]
                 
    LST_repos = FNC_get_repos(FLDR_toRepos)
    LST_tmp_repo = []
    for FLDR_repo in LST_repos: # go through repos
        LST_ftprts = FNC_get_ftprts(FLDR_toRepos + FLDR_repo + "/")
        for FNME_ftprt in LST_ftprts: # go through footprints
            LST_tmp_fprt = [('s_','RPO',FLDR_repo)]
            LST_tmp_fprt.append(('s_','FIL',FNME_ftprt))
            BLOB_file = FNC_read_file(FLDR_toRepos + FLDR_repo + "/" + FNME_ftprt) # get module content
            STR_file = FNC_convert_file(BLOB_file) # convert module file to string
            
            n = 0
            lvl0 = ' '.join(list(FNC_get_this_level(STR_file)))
            #print n,n*"  ",lvl0
            for s0 in check[n]:
                if re.search(s0[1],lvl0):
                    try:
                        LST_tmp_fprt.append(('s0',s0[0],lvl0.split(" ",s0[2])[s0[3]]))
                    except:
                        LST_tmp_fprt.append(('s0',s0[0],""))
            
            for STR_1stlvl in list(FNC_get_next_level(STR_file)):
                n = 1
                lvl1 = ' '.join(list(FNC_get_this_level("("+STR_1stlvl+")")))
                #print n,n*"  ",lvl1
                for s1 in check[n]:
                    if re.search(s1[1],lvl1):
                        try:
                            LST_tmp_fprt.append(('s1',s1[0],lvl1.split(" ",s1[2])[s1[3]]))
                        except:
                            LST_tmp_fprt.append(('s1',s1[0],""))
                        
                        if s1[5] and re.search(s1[5][1],lvl1): # special treatment for hide of text fields comes here
                            LST_tmp_fprt.append(('s1',s1[0]+"_"+s1[5][0],lvl1.split(" ",s1[2])[-1]))
                        if s1[4]:
                        
                            for STR_2ndlvl in list(FNC_get_next_level("("+STR_1stlvl+")")):
                                n = 2
                                lvl2 = ' '.join(list(FNC_get_this_level("("+STR_2ndlvl+")")))
                                #print n,s1[0],lvl2
                                
                                for s2 in check[n]:
                                    if re.search(s2[1],lvl2):
                                        if s2[5] and s1[0] != '3DM':
                                            if s2[0] == 'POS':
                                                for i, val in enumerate(lvl2.split(" ",s2[2])[1:]):
                                                    LST_tmp_fprt.append(('s2',s1[0]+"_"+s2[0]+"_"+s2[5][i],val))
                                            else:
                                                LST_tmp_fprt.append(('s2',s1[0]+"_"+s2[0],lvl2.split(" ",s2[2])[s2[3]]))
                                        else:
                                
                                            for STR_3rdlvl in list(FNC_get_next_level("("+STR_2ndlvl+")")):
                                                n = 3
                                                lvl3 = ' '.join(list(FNC_get_this_level("("+STR_3rdlvl+")")))
                                                #print n,s2[0],"  ",lvl3
                                                
                                                for s3 in check[n]:
                                                    if re.search(s3[1],lvl3):
                                                        if s3[0] == "FNT":
                                                            if re.search(s3[5],lvl3):
                                                                LST_tmp_fprt.append(('s3',s1[0]+"_"+s3[0],lvl3.split(" ",s3[2])[s3[3]]))
                                                        elif s3[0] == "XYZ":
                                                            for i, val in enumerate(lvl3.split(" ",s3[2])[1:]):
                                                                LST_tmp_fprt.append(('s3',s1[0]+"_"+s2[0]+"_"+s3[5][i],val))
                                                        if s3[4]:
                                                                
                                                            for STR_4thlvl in list(FNC_get_next_level("("+STR_3rdlvl+")")):
                                                                n = 4
                                                                lvl4 = ' '.join(list(FNC_get_this_level("("+STR_4thlvl+")")))
                                                                #print n,s2[0],"    ",lvl4
                                                                
                                                                for s4 in check[n]:
                                                                    if re.search(s4[1],lvl4):
                                                                        if len(s4[5]) == 2:
                                                                            for i, val in enumerate(lvl4.split(" ",s4[2])[1:3]):
                                                                                LST_tmp_fprt.append(('s4',s1[0]+"_"+s4[0]+"_"+s4[5][i],val))
                                                                        else:
                                                                            LST_tmp_fprt.append(('s4',s1[0]+"_"+s4[0],lvl4.split(" ",s4[2])[s4[3]]))

            #break                    
            LST_tmp_repo.append(LST_tmp_fprt)
        #break

    # make list of lines
    # get header
    LST_hdr = ['RPO','FIL','MOD','STS']
    for hdr in check[1]:
        LST_hdr.append(hdr[0])
    sortstart = len(LST_hdr) - 3
    for fpt in LST_tmp_repo:
        for hdr in fpt:
            if hdr[1] not in LST_hdr:
                LST_hdr.append(hdr[1])
    
    LST_part = LST_hdr[sortstart:]
    LST_hdr = LST_hdr[:sortstart]
    LST_part.sort()
    LST_hdr.extend(LST_part)
    TPL_hdr = tuple(LST_hdr)
    # for item in LST_hdr:
        # print item
    # get values for the 'columns'
    LST_oflines = [TPL_hdr]
    for fpt in LST_tmp_repo:
        DCT_fpt = {}
        LST_fpt = []
        for h,i,j in fpt:
            DCT_fpt[i] = j
        for hdr in TPL_hdr:
            try:
                LST_fpt.append(DCT_fpt[hdr])
            except:
                LST_fpt.append("")
        TPL_fpt = tuple(LST_fpt)
        LST_oflines.append(TPL_fpt)
    #break
    
    FNC_write_csv(LST_oflines, FLDR_toCSV+FNME_csv)