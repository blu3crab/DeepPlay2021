###############################################################################
#   ReportReader
#       scan report files in REPORT_DIR (sorted most recent to least)
#       for each report
#           capture report date range
#           skip to LEAD_COLUMN_LABEL
#           for each line in report
#               tally issue code
#               for each issue code
#                   tally percentage of total issues
#           write issue tally as json
#
#TODO: tally cumulative issues
#TODO: write csv
#TODO: plot trend
#TODO: build dictionary (phone name, count)
###############################################################################
import csv
import os
import sys
import xlrd

import json

import unicodedata

# Helper libraries
import numpy as np
import matplotlib.pyplot as plt

NADA = "nada"
COMMAND_LINE_OPTIONS = "REPORT_DIR LEAD_COLUMN_LABEL GETPHONE_CODE1 GETPHONE_CODE2"
COMMAND_LINE_ARG_REPORT_DIR = 1
COMMAND_LINE_ARG_LEAD_COLUMN_LABEL = 2
COMMAND_LINE_ARG_GETPHONE_CODE1 = 3
COMMAND_LINE_ARG_GETPHONE_CODE2 = 4

###############################################################################
def main():
    # issue dictionaries: tally, description, percentage
    issue_tally = {
        "A12": 0,
        "A22": 0,
        "S4": 0,
        "A8": 0,
        "A16": 0,
        "T1": 0,
        "C3": 0
    }
    issue_description = {
        "A12": "Frequent No Transmitter Connected notifications.",
        "A22": "Transmitter Disconnected, No Transmitter Connected notification.",
        "S4": "Sensor readings seem inaccurate and/or different from BGM test results...",
        "A8": "Sensor Replacement Alert <4, 90, 180 days post insertion...",
        "A16": "Sensor Check alert; no glucose values displayed",
        "T1": "Pairing incomplete, Transmitter Connected does not appear in status bar",
        "C3": "Calibration rejected; entry not used for calibration"
    }
    issue_percentage = {
        "A12": 0,
        "A22": 0,
        "S4": 0,
        "A8": 0,
        "A16": 0,
        "T1": 0,
        "C3": 0
    }
    phone_tally = {
        "iPhone 7": 0,
        "Samsung S7": 0
    }

    print("Hola! Command line parameters->")
    print(sys.argv, len(sys.argv))
    if not len(sys.argv) > 4:
        print("Oops!  ReportReader ", COMMAND_LINE_OPTIONS)
        return NADA
    print("issue description->", issue_description)

    # get report path from args
    report_dir, report_list = get_report_path()

    # get lead header column text from args
    lead_column_label = get_leadcolumn_label()
    # get phone codes to tally phones associated with these issue codes
    get_phone_for_code1, get_phone_for_code2 = get_phone_for_code_list()

    # define arrays of issue counts for later plotting
    issue_count1, issue_count2, issue_count3, issue_count4, issue_count5, issue_count6, issue_count7 = [], [], [], [], [], [], []

    for report in report_list:
        report_path = report_dir + report
        print("\nreport_path ", report_path, " loading...")

        # load workbook & extract 1st sheet
        workbook = xlrd.open_workbook(report_path)
        sheet = workbook.sheet_by_index(0)

        # # grab row of cells & print each cell
        # cells = sheet.row_slice(rowx=7, start_colx=0, end_colx=17)
        # for cell in cells:
        #     print(cell.value)

        # zero issue tally & percent dictionary, reset issue count, clear labels found flag
        issue_tally_by_week = issue_tally.copy()
        issue_percent_by_week = issue_percentage.copy()
        issue_count = -1;
        labels_found = False
        # for each row in sheet
        for row_inx in range(sheet.nrows):
            #cols = sheet.row_values(row_inx)
            #print(cols)
            #print("cols len->", len(cols))
            #print(sheet.cell(row_inx,0), ", ", sheet.cell(row_inx,15), ", ", sheet.cell(row_inx,16))

            first_cell_as_string = sheet.cell(row_inx,0).value
            # if lead column label found, mark labels found
            if not labels_found and lead_column_label == first_cell_as_string:
                labels_found = True
                #print("labels_found at ", row_inx, " with ", first_cell_as_string)
            elif not labels_found and row_inx == 2:
                file_date_range = first_cell_as_string
                print(file_date_range)

            # if labels have been found, start issue tally
            if labels_found and issue_count > -1:
                issue_count += 1
                cells_case = sheet.row_slice(rowx=row_inx, start_colx=0, end_colx=1)
                cell_phone = sheet.row_slice(rowx=row_inx, start_colx=12, end_colx=13)
                cells_issue = sheet.row_slice(rowx=row_inx, start_colx=15, end_colx=17)
                # print("cells_case len->", len(cells_case))
                # print("cells_issue len->", len(cells_issue))
                # print(issue_count, ": ", cells_case[0].value, ", ", cells_issue[0].value, ", " + cells_issue[1].value)
                for i in range(0, 2):
                    # if issue column not blank
                    if cells_issue[i].value != "":
                        try:
                            if cells_issue[i].value in issue_tally_by_week:
                                tally = issue_tally_by_week[cells_issue[i].value]
                                tally += 1
                                issue_tally_by_week[cells_issue[i].value] = tally
                                # print(cells_issue[i].value, " issue_tally ", issue_tally[cells_issue[i].value])
                        except Exception as inst:
                            print(type(inst))  # the exception instance
                            print(inst.args)  # arguments stored in .args
                            print(inst)  # __str__ allows args to be printed directly,
                    # if phone column not blank
                    if cell_phone[0].value != "" or not cell_phone:
                        # if cell issue code matches "get phone for code" issue code
                        if cells_issue[i].value == get_phone_for_code1 or cells_issue[i].value == get_phone_for_code2:
                            try:
                                # if phone in dictionary
                                phonelist = phone_tally.keys()
                                if cell_phone[0].value in phone_tally.keys():
                                    #print("existing phone (", cells_issue[i].value, ") -> ", cell_phone[0])
                                    # increment tally
                                    tally = phone_tally[cell_phone[0].value]
                                    tally += 1
                                    phone_tally[cell_phone[0].value] = tally
                                else:
                                    # add phone to dictionary
                                    #phone_tally.update({cell_phone: 1})
                                    #print("new phone (", cells_issue[i].value, ") -> ", cell_phone[0].value)
                                    phone_tally[cell_phone[0].value] = 1
                            except Exception as inst:
                                print(type(inst))  # the exception instance
                                print(inst.args)  # arguments stored in .args
                                print(inst)  # __str__ allows args to be printed directly,

            elif labels_found:
                issue_count = 0;

    #    for tally in issue_tally:
        keys = issue_tally_by_week.keys();
        # print("keys","[",len(keys),"]->", keys)
        for key in keys:
            issue_percent_by_week[key] = issue_tally_by_week[key]/issue_count

        # save as json
        filename = "issue_tally-" + file_date_range + ".json"
        with open(filename, 'w') as fp:
            json.dump(issue_tally_by_week, fp)

        # restore json
        with open(filename, 'r') as fp:
            issue_tally_by_week = json.load(fp)

        print(filename)
        for key in sorted(issue_tally_by_week, key=issue_tally_by_week.get, reverse=True):
            print(get_percent_rounded(issue_percent_by_week[key]), " (", issue_tally_by_week[key], " of ", issue_count, ")   ...", key, " -> ", issue_description[key])

        # tally issue counts for plotting
        i = 0
        for key in keys:
            if (i == 0):
                issue_count1.append(issue_tally_by_week[key])
            elif (i==1):
                issue_count2.append(issue_tally_by_week[key])
            elif (i==2):
                issue_count3.append(issue_tally_by_week[key])
            elif (i==3):
                issue_count4.append(issue_tally_by_week[key])
            elif (i==4):
                issue_count5.append(issue_tally_by_week[key])
            elif (i==5):
                issue_count6.append(issue_tally_by_week[key])
            elif (i==6):
                issue_count7.append(issue_tally_by_week[key])
            i = i + 1

    # after all files captured
    #print("issue_count for plot:" + issue_count1)
    print("##################################################")
    print("issue_count for plot:")
    print("#1 " + str(issue_count1))
    print("#2 " + str(issue_count2))

    #plt.plot

    week_range = range(len(issue_count1))
    plt.plot(week_range, issue_count1, 'r',
             week_range, issue_count2, 'r--',
             week_range, issue_count3, 'b',
             week_range, issue_count4, 'b--',
             week_range, issue_count5, 'g',
             week_range, issue_count6, 'y',
             week_range, issue_count7, 'm')
#    plt.legend(['A12', 'A22'])
    plt.legend(keys)
    plt.show()


    print("\n\n##########phone for codes: ", get_phone_for_code1, ", ", get_phone_for_code2, "############")
    for phone in sorted(phone_tally.keys()):
    #for phone in sorted(phone_tally, key=phone_tally.get, reverse=True):
        print(phone, " -> ", phone_tally[phone])
    # sorted_issue_tally = sorted(issue_tally.values())
    # print(sorted_issue_tally)
    # for key, value in sorted(released.items()):
    #     print key, value

    print("arrivederci!")
###############################################################################
def get_percent_rounded(raw):
    return '{:.0f}%'.format(raw * 100)
def get_percent_two(raw):
    return '{:.2f}%'.format(raw * 100)
def get_percent_raw(raw):
    return '{}%'.format(raw * 100)
###############################################################################
# get report path from args
#       returns path or NADA
def get_report_path():

    # path of executing python file
    print("\nget_report_path entry entered->\n")
    full_path = os.path.realpath(__file__)
    print("realpath->", full_path)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    print("dirname->", dir_path)

    cwd = os.getcwd()
    print("getcwd->", cwd)

    dir_path = sys.argv[COMMAND_LINE_ARG_REPORT_DIR]
    print("dirname->", dir_path)

    report_list = os.listdir(dir_path)
    for file in report_list:
        if file.endswith(".xlsx"):
            print("report->", file)
        else:
            print("unk->", file)

    report_list.sort(reverse=True)
    for file in report_list:
        print("sorted report->", file)

    # fname = sys.argv[2]
    # print("fname->", fname)
    # report_path = dir_path + fname
    # if not os.path.isfile(report_path):
    #     print("Oops! file ", report_path, " does NOT exist!")
    #     return NADA
    # print("file ", report_path, " exists!")
    print("get_report_path entry->", full_path)
    return dir_path, report_list

###############################################################################
# get report lead column from args
#       returns lead column
def get_leadcolumn_label():
    lead_column_label = sys.argv[COMMAND_LINE_ARG_LEAD_COLUMN_LABEL]
    print("lead_column_label->", lead_column_label)
    return lead_column_label


###############################################################################
# get phone codes of interest from args
#       returns path or NADA
def get_phone_for_code_list():
    get_phone_for_code1 = sys.argv[COMMAND_LINE_ARG_GETPHONE_CODE1]
    get_phone_for_code2 = sys.argv[COMMAND_LINE_ARG_GETPHONE_CODE2]
    print("get_phone_code_list->", get_phone_for_code1, get_phone_for_code2)
    return get_phone_for_code1, get_phone_for_code2


###############################################################################
# launch main
if __name__ == "__main__":
    main()

###############################################################################
