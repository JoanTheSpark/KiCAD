'''
features
- change info in step file
- import step, export vrml with scale applied
- add license&info to vrml file
- keep track of changes to step files to avoid redoing already done ones
'''

import sys, os, shutil
import hashlib, pyparsing
import datetime
from datetime import datetime

PATH_FREECADBIN = "C:\Program Files\FreeCAD 0.16\bin"
sys.path.append(PATH_FREECADBIN)

import FreeCAD
import Import
import FreeCADGui
import ImportGui
import Draft

PATH_toStepFiles = "."
PATH_toVrmlFiles = "."
FNME_hashfile = "StepFileHashes.txt"

STR_licAuthor = ""
STR_licEmail = ""
STR_licOrgSys = ""
STR_licPreProc = ""

LIST_license = ["Copyright (C) "+datetime.now().strftime("%Y")+", " + STR_licAuthor,
                "",
                "This program is free software: you can redistribute it and/or modify",
                "it under the terms of the GNU General Public License as published by",
                "the Free Software Foundation, either version 3 of the License, or",
                "any later version.",
                "",
                "This program is distributed in the hope that it will be useful,",
                "but WITHOUT ANY WARRANTY; without even the implied warranty of",
                "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the",
                "GNU General Public License for more details.",
                "",
                "You should have received a copy of the GNU General Public License",
                "along with this program.  If not, see http://www.gnu.org/licenses/.",
                ]


def FNCT_modify_step(PMBL_stepfile,
                     DICT_positions,
                     LIST_license,
                     FNME_stepfile,
                     STR_licAuthor,
                     STR_licEmail,
                     STR_licOrgSys,
                     STR_licPreProc,
                     ):
    """
    - add license right after HEADER
    - modification of DESCR
    - total replace of NAME
    - copy of SCHEMA
    - space after ENDSEC

    DICT_positions:
    H .. HEADER
    D .. DESCRIPTION
    N .. NAME
    S .. SCHEMA
    E .. ENDSEC
    """
    PMBL_modstepfile = []
    FLAG_addlicense = True
    STR_description = ""
    STR_schema = ""
    for line in range(DICT_positions["E"]):
        if line < DICT_positions["H"]: # leave ISO/HEADER alone
            PMBL_modstepfile.append(PMBL_stepfile[line].strip())
        if line == DICT_positions["H"] and FLAG_addlicense: # add license
            PMBL_modstepfile.append("/* " + str(FNME_stepfile) + " 3D STEP model for use in ECAD systems")
            for licline in LIST_license:
                PMBL_modstepfile.append(" * " + licline)
            PMBL_modstepfile.append(" */")
            PMBL_modstepfile.append("")
            FLAG_addLicense = False
        if line >= DICT_positions["D"] and line < (DICT_positions["N"] - 1): # get DESCR part
            STR_description += PMBL_stepfile[line].strip()
        if line == (DICT_positions["S"] - 1): # add modded DESCR and NAME
            # DESCRIPTION
            PMBL_modstepfile.append("FILE_DESCRIPTION(")
            PMBL_modstepfile.append("/* description */ ('model of " + str(FNME_stepfile) + "'),")
            STR_description = pyparsing.nestedExpr("/*", "*/").suppress().transformString(STR_description)
            PMBL_modstepfile.append("/* implementation_level */ " + STR_description[-len("'2;1');"):])
            PMBL_modstepfile.append("")
            #NAME
            PMBL_modstepfile.append("FILE_NAME(")
            PMBL_modstepfile.append("/* name */ '" + str(FNME_stepfile) + ".stp',")
            STR_TS = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            PMBL_modstepfile.append("/* time_stamp */ '" + STR_TS + "',")
            PMBL_modstepfile.append("/* author */ ('" + STR_licAuthor + "','" + STR_licEmail + "'),"),
            PMBL_modstepfile.append("/* organization */ (''),")
            PMBL_modstepfile.append("/* preprocessor_version */ '" + STR_licPreProc + "',")
            PMBL_modstepfile.append("/* originating_system */ '" + STR_licOrgSys + "',")
            PMBL_modstepfile.append("/* authorisation */ '');")
            PMBL_modstepfile.append("")
        if line >= (DICT_positions["S"] - 1) and line <= (DICT_positions["E"] - 1): # get DESCR part
            STR_schema += PMBL_stepfile[line].strip()
        if line == (DICT_positions["E"] - 1): # add cleaned SCHEMA/ENDSEC
            STR_schema = pyparsing.nestedExpr("/*", "*/").suppress().transformString(STR_schema)
            for item in STR_schema.split(";")[:-1]:
                PMBL_modstepfile.append(item + ";")
    PMBL_modstepfile.append("")
    return(PMBL_modstepfile)


def FNCT_modify_vrml(PMBL_vrmlfile,
                     DICT_positions,
                     LIST_license,
                     FNME_vrmlfile,
                     STR_licAuthor,
                     STR_licEmail,
                     STR_licOrgSys,
                     STR_licPreProc,
                     ):
    """
    DICT_positions:
    V .. VRML line
    G .. Group start
    """
    PMBL_modvrmlfile = []
    STR_description = ""
    STR_schema = ""
    for line in range(DICT_positions["G"]):
        if line < DICT_positions["V"]: # leave ISO/HEADER alone
            PMBL_modvrmlfile.append(PMBL_vrmlfile[line].strip())
        if line == DICT_positions["V"]: # add license
            PMBL_modvrmlfile.append("")
            PMBL_modvrmlfile.append("# LICENSE")
            PMBL_modvrmlfile.append("# " + str(FNME_vrmlfile) + " 3D VRML model for use in ECAD systems")
            for licline in LIST_license:
                PMBL_modvrmlfile.append("# " + licline)
            PMBL_modvrmlfile.append("#")
            # DESCRIPTION
            PMBL_modvrmlfile.append("# METADATA")
            PMBL_modvrmlfile.append("# description 'model of " + str(FNME_vrmlfile) + "'")
            PMBL_modvrmlfile.append("# filename '" + str(FNME_vrmlfile) + ".wrl'")
            STR_TS = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            PMBL_modvrmlfile.append("# time_stamp '" + STR_TS + "'")
            PMBL_modvrmlfile.append("# author ('" + STR_licAuthor + "','" + STR_licEmail + "')"),
            PMBL_modvrmlfile.append("# organization ('')")
            PMBL_modvrmlfile.append("# preprocessor_version '" + STR_licPreProc + "'")
            PMBL_modvrmlfile.append("# originating_system '" + STR_licOrgSys + "'")
            PMBL_modvrmlfile.append("# authorisation ''")
    PMBL_modvrmlfile.append("")
    return(PMBL_modvrmlfile)
    

def FNCT_md5_for_file(FNME_file, NMBR_block_size=8192):
    md5 = hashlib.md5()
    while True:
        data = FNME_file.read(NMBR_block_size)
        if not data:
            break
        md5.update(data)
    return md5.hexdigest()



if __name__=='__main__':

    # if exist, read old md5 hash file in list for comparison
    # so we don't work on already good files
    try:
        HDLR_hashfile = open(PATH_toStepFiles + FNME_hashfile, 'r') # open
        HDLR_hashfile.seek(0)
        LIST_md5Hashes = HDLR_hashfile.readlines()
        HDLR_hashfile.close()
    except:
        # no file there, start from scratch
        LIST_md5Hashes = []
        print "broken_1"
    DICT_md5Hashes = {}
    for item in LIST_md5Hashes:
        DICT_md5Hashes[item.split(";")[0]] = item.split(";")[1].strip()

    # modify STEP files if needed
    LIST_stepfiles = os.listdir(PATH_toStepFiles)
    LIST_stepfiles_clean = []
    for FNME_stepfile in LIST_stepfiles:
        if os.path.isfile(PATH_toStepFiles + FNME_stepfile) == 1: # test if folder or file..
            if FNME_stepfile[-3:] == "stp": # test if step file
                FLAG_makeTransparent = False
                if FNME_stepfile[-6:-4] != "_T": # test if transparency manipulation is needed
                    FLAG_makeTransparent = True
                LIST_stepfiles_clean.append(FNME_stepfile[:-4])
                try:
                    HDLR_stepfile = open(PATH_toStepFiles + FNME_stepfile, 'r') # open
                except:
                    print "broken_2"
                STR_md5Hash = str(FNCT_md5_for_file(HDLR_stepfile))

                #search for stepfile in old md5 hash list, compare hashes
                FLAG_workFile = False
                if FNME_stepfile[:-4] in DICT_md5Hashes.keys():
                    if DICT_md5Hashes.get(FNME_stepfile[:-4]) != STR_md5Hash:
                        FLAG_workFile = True #got changed step file here
                else:
                    FLAG_workFile = True #new step file here

                if FLAG_workFile == True:
                    print "working on",FNME_stepfile
                    HDLR_stepfile.seek(0)
                    PMBL_stepfile = HDLR_stepfile.readlines()
                    HDLR_stepfile.close()
                    CNT_cutoff = 0
                    DICT_positions = {}
                    for line in PMBL_stepfile:
                        CNT_cutoff += 1
                        if line[:6] == "HEADER":
                            DICT_positions["H"] = CNT_cutoff
                        elif line[:6] == "ENDSEC":
                            DICT_positions["E"] = CNT_cutoff
                        elif line[:4] == "DATA":
                            DICT_positions["A"] = CNT_cutoff
                            break
                        if line[:5] == "FILE_":
                            if line[5:9] == "DESC":
                                DICT_positions["D"] = CNT_cutoff
                            elif line[5:9] == "NAME":
                                DICT_positions["N"] = CNT_cutoff
                            elif line[5:9] == "SCHE":
                                DICT_positions["S"] = CNT_cutoff

                    LIST_PMBL = FNCT_modify_step(PMBL_stepfile[:DICT_positions["E"]],
                                                 DICT_positions,
                                                 LIST_license,
                                                 FNME_stepfile[:-4],
                                                 STR_licAuthor,
                                                 STR_licEmail,
                                                 STR_licOrgSys,
                                                 STR_licPreProc,
                                                 )

                    # overwrite step file
                    try:
                        HDLR_stepfile_w = open(PATH_toStepFiles + FNME_stepfile, 'w') # open
                    except:
                        print "broken_3"
                    else:
                        # overwrite with new preamble
                        for line in LIST_PMBL:
                            HDLR_stepfile_w.write(line + "\n")
                        # add old data section
                        for line in PMBL_stepfile[(DICT_positions["A"]-1):]:
                            HDLR_stepfile_w.write(line.strip() + "\n")
                        HDLR_stepfile_w.close()

                    # load STEP model, manipulate and save as VRML
                    FreeCAD.newDocument("Unnamed")
                    FreeCAD.setActiveDocument("Unnamed")
                    ImportGui.insert(PATH_toStepFiles + FNME_stepfile,"Unnamed")
                    FNME_vrmlfile = FNME_stepfile[:-4] + ".wrl"
                    # change display mode and scale down
                    for part in FreeCAD.ActiveDocument.Objects:
                        part.ViewObject.DisplayMode = 1 #Shaded
                        Draft.scale(part,delta=App.Vector(0.3937,0.3937,0.3937),center=App.Vector(0,0,0),legacy=True)
                    if FLAG_makeTransparent: # if transparency is needed
                        
#                        from PySide import QtGui
#                        QtGui.QInputDialog.getText(None, "Get text", "Input:")[0]
                        pass
                    __objs__=[] # select all parts (again)
                    for part in FreeCAD.ActiveDocument.Objects:                    
                        __objs__.append(part)
                    FreeCADGui.export(__objs__,(PATH_toVrmlFiles + FNME_vrmlfile))
                    del __objs__
                    FreeCAD.closeDocument("Unnamed")

                    
                    # add license stuff to fresh VRML file
                    print "working on",FNME_vrmlfile
                    try:
                        HDLR_vrmlfile = open(PATH_toVrmlFiles + FNME_vrmlfile, 'r') # open
                    except:
                        print "broken_4"
                    else:
                        HDLR_vrmlfile.seek(0)
                        PMBL_vrmlfile = HDLR_vrmlfile.readlines()
                        HDLR_vrmlfile.close()
                        CNT_cutoff = 0
                        DICT_positions = {}
                        for line in PMBL_vrmlfile:
                            CNT_cutoff += 1
                            if line[:15] == "#VRML V2.0 utf8":
                                DICT_positions["V"] = CNT_cutoff
                            elif line[:7] == "Group {":
                                DICT_positions["G"] = CNT_cutoff
                                break

                        LIST_PMBL = FNCT_modify_vrml(PMBL_vrmlfile[:DICT_positions["G"]],
                                                     DICT_positions,
                                                     LIST_license,
                                                     FNME_vrmlfile[:-4],
                                                     STR_licAuthor,
                                                     STR_licEmail,
                                                     STR_licOrgSys,
                                                     STR_licPreProc,
                                                     )

                        # overwrite vrml file
                        try:
                            HDLR_vrmlfile_w = open(PATH_toVrmlFiles + FNME_vrmlfile, 'w') # open
                        except:
                            print "broken_5"
                        else:
                            # overwrite with new preamble
                            for line in LIST_PMBL:
                                HDLR_vrmlfile_w.write(line + "\n")
                            # add old data section
                            for line in PMBL_vrmlfile[(DICT_positions["G"]-1):]:
                                HDLR_vrmlfile_w.write(line)
                            HDLR_vrmlfile_w.close()

                else:
                    HDLR_stepfile.close()

    # rewrite hash file when done
    if LIST_stepfiles_clean:
        LIST_stepfiles_clean.sort()
        try:
            HDLR_hashfile_w = open(PATH_toStepFiles + FNME_hashfile, 'w') # open
        except:
            print "broken_6"
        else:
            print "writing new hashfile"
            for FNME_stepfile_clean in LIST_stepfiles_clean:
                try:
                    HDLR_stepfile_r = open(PATH_toStepFiles + FNME_stepfile_clean + ".stp", 'r') # open
                except:
                    print "broken_7"
                else:
                    HDLR_hashfile_w.write(FNME_stepfile_clean + ";" + str(FNCT_md5_for_file(HDLR_stepfile_r)) + "\n")
                    HDLR_stepfile_r.close()
            HDLR_hashfile_w.close()

