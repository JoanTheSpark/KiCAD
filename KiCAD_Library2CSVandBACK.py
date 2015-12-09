# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- KiCAD local library export to csv and back
#--
#-- reads local library and pulls out symbols
#-- and their field values, then writes them into
#-- a csv file.
#-- If a flag in the code is changed it also
#-- is able to write field value data from that csv
#-- back into the local libs. Do not change lib, name
#-- or reference fields for the import to work!
#--
#-- BACKUP YOUR LIBRARIES BEFORE RUNNING THIS!
#--
#-- Joan The Spark 2015
#--
#-- GNU General Public License 3+ (GPL3+)
#-------------------------------------------------

import os, sys, shutil, fileinput

FLDR_toLibs = "." #i.e. "E:/Data_KiCAD/KiCAD_Symbols/"
FLDR_toCSV = "."
FNME_csv = "symbollist.csv"

def FNC_get_libs(FLDR_toLibs):
    LIST_libs = os.listdir(FLDR_toLibs)
    LIST_libs_clean = []
    for FNME_lib in LIST_libs:
        if os.path.isfile(FLDR_toLibs + FNME_lib) == 1: # test if folder or file..
            if FNME_lib[-3:] == "lib": # test if lib file
                LIST_libs_clean.append(FNME_lib)
    return LIST_libs_clean

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

def FNC_write_csv(LIST_ofLines, PATH_toCSV):
    try:
        HDLR_csvfile = open(PATH_toCSV, 'w') # open
    except:
        print "broken_2"
    else:
        for line in LIST_ofLines:
            STR_line = ';'.join(line)
            HDLR_csvfile.write(STR_line + "\n")
        HDLR_csvfile.close()
    return()


if __name__=='__main__':

    FLAG_doImport = True # True = make CSV, False = modify Libraries
    FLAG_dryRun = True # True = do not change libs, just print changes to commandline output
                       # False = do modify the libs

    if FLAG_doImport:
        # this list is setup so it adds a 'manf#' field automatically into the csv
        LIST_symbols = [["lib","ref","name","footprint","pdf","manf#"]]
        LIST_libs = FNC_get_libs(FLDR_toLibs)
        for FNME_lib in LIST_libs: # go through libs
            BLOB_libfile = FNC_read_file(FLDR_toLibs+FNME_lib) # get lib content
            CNT_line = -1
            for line in BLOB_libfile: # go through single lib
                CNT_line += 1
                if line[:4] == "DEF ": # find symbol start
                    LIST_thisSymbol = [FNME_lib[:-4]]
                    for j in range(1,len(LIST_symbols[0])): # get symbol details
                        if BLOB_libfile[CNT_line+j][:3] == ("F"+str(j-1)+" "):
                            LIST_thisSymbol.append(BLOB_libfile[CNT_line+j].split(" ")[1].strip("\""))
                        else:
                            LIST_thisSymbol.append("")
                    LIST_symbols.append(LIST_thisSymbol)
        FNC_write_csv(LIST_symbols, FLDR_toCSV + FNME_csv)
    else:
        #now read csv file and add stuff to libs
        BLOB_csvfile = FNC_read_file(FLDR_toCSV+FNME_csv) # get csv content
        LIST_symbols = []
        for line in BLOB_csvfile: # convert blob to list..
            LIST_symbols.append(line.strip().split(";"))
        #kicad optimizes stuff? and deletes fields completely in lib if there is nothing in ""
        # >> replace empty fields with "_", as we can't have that, can we?
        for i in range(len(LIST_symbols)):
            for j in range(len(LIST_symbols[i])):
                if LIST_symbols[i][j] == "":
                    LIST_symbols[i][j] = "_"
        # got symbol with fieldvalues in list-variable, let's go..
        for symbol in LIST_symbols[1:]:
            try:
                CNT_Fx = 0
                FLAG_foundSymbol = False
                # open lib file and replace/add when symbol has been found
                for line in fileinput.input(FLDR_toLibs+symbol[0]+".lib", inplace=FLAG_dryRun):
                    CNT_Fx += 1
                    # check that we got the correct symbol
                    if line.startswith("DEF "+symbol[2]+" "+symbol[1]):
                        print line,
                        CNT_Fx = 0
                        FLAG_foundSymbol = True
                    # now fill in the values into the fields (F0 to Fx)
                    elif FLAG_foundSymbol:
                        if line.startswith("F"+str(CNT_Fx-1)+" "): # put in new field values
                            line = line.strip().split(" ")
                            fieldname = ""
                            if CNT_Fx < 3: # F0-F2 keep settings for textsize, etc..
                                print line[0]+" \""+symbol[CNT_Fx]+"\" "+(" ").join(line[2:])
                            elif CNT_Fx > 4: # add/mod fieldnames above F4
                                fieldname = " \""+LIST_symbols[0][CNT_Fx]+"\""
                                print line[0]+" \""+symbol[CNT_Fx]+"\" 0 0 5 H I C CNN"+fieldname
                            else: # '0 0 5 H I C CNN' makes datasheet, etc. info tiny small and invisible..
                                print line[0]+" \""+symbol[CNT_Fx]+"\" 0 0 5 H I C CNN"
                        else: # we ran out of available fields to fill in, make more
                            for i in range(len(symbol) - CNT_Fx): # add missing fields
                                fieldname = ""
                                if CNT_Fx > 3: # add fieldname if needed
                                    fieldname = " \""+LIST_symbols[0][CNT_Fx+i]+"\""
                                print "F"+str(CNT_Fx+i-1)+" \""+symbol[CNT_Fx+i]+"\" 0 0 5 H I C CNN"+fieldname
                            print line, # don't forget to re-print the line that came here
                            FLAG_foundSymbol = False # we only do this ONCE per symbol
                    else:
                        print line, # print lines we don't care for
                fileinput.close() # done
            except:
                print "broken_3" # upsi

    print "done"
