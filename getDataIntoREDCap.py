#!/usr/bin/env python
#
# import timeline followback
#
# needed to run:
#    apt-get install libcurl4-openssl-dev
# to get pycurl installed by pip
#

import pycurl, cStringIO, json, sys, re, os
from dateutil.parser import parse
from array import array
from StringIO import StringIO
from time import sleep

# TODO: test if we can find the tokens files

with open('../../code/php/tokens.json') as data_file:
    tokens = json.load(data_file)

# default
site = "UCSD"
# do not add to REDCap
force = ""

if len(sys.argv) < 2:
    print("Usage: <site name> [-f]")
    sys.exit(0)

site = sys.argv[1]
if len(sys.argv) == 3:
    force = sys.argv[2]
#print("Query for site: "+ site + "\n")

# get list of events from REDCap
buf = cStringIO.StringIO()
# variables we need from REDCap include all the CBCL variables from the instrument P_Child Behavior Check List (cbcl_qXX_p)
# and P_Adult Self Report (asr_qXX_p)
data = {
    'token': tokens[site],
    'content': 'event',
    'format': 'json',
    'returnFormat': 'json'
}
ch = pycurl.Curl()
ch.setopt(ch.URL, 'https://abcd-rc.ucsd.edu/redcap/api/')
ch.setopt(ch.HTTPPOST, data.items())
ch.setopt(ch.WRITEFUNCTION, buf.write)
ch.perform()
ch.close()
eventList = json.load(StringIO(buf.getvalue()))
buf.close()

# get list of existing participants for this site
buf = cStringIO.StringIO()
# variables we need from REDCap include all the CBCL variables from the instrument P_Child Behavior Check List (cbcl_qXX_p)
# and P_Adult Self Report (asr_qXX_p)
data = {
    'token': tokens[site],
    'content': 'record',
    'format': 'json',
    'type': 'flat',
    'fields[0]': 'id_redcap',
    'events[0]': 'baseline_year_1_arm_1',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'false',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json'
}
ch = pycurl.Curl()
ch.setopt(ch.URL, 'https://abcd-rc.ucsd.edu/redcap/api/')
ch.setopt(ch.HTTPPOST, data.items())
ch.setopt(ch.WRITEFUNCTION, buf.write)
ch.perform()
ch.close()
v = json.load(StringIO(buf.getvalue()))
buf.close()

participants = {}
for p in v:
    participants[p['id_redcap']] = 1


# find events done on the same day with the same substance and merge them into single events
def mergeDays( scores ):
    # find day for each score
    days = []
    realEvents = []
    for score in scores:
        if ('substance' not in score) or (score['substance'] == 'undefined'):
            continue
        realEvents.append(score)
        d = parse(score['start'])
        days.append(d.strftime('%Y-%m-%d'))
    unique_days    = [x for n, x in enumerate(days) if x not in days[:n]]
    duplicate_days = [x for n, x in enumerate(days) if x in days[:n]]
    if len(duplicate_days) == 0:
        return realEvents
    output = []
    dayBySubstance = {}
    i = 0
    for d in realEvents:
        if days[i] in duplicate_days:
            # do something
            # lets get the list of all scores for these days by substance
            subst = d['substance']
            day = days[i]
            if subst not in dayBySubstance:
                dayBySubstance[subst] = {}
            if day not in dayBySubstance[subst]:
                dayBySubstance[subst][day] = []
            dayBySubstance[subst][day].append(d)
        else:
            # just append, the score is from a day that is not duplicated
            output.append(d)
        i = i + 1 
    # now we have all events in either output (events without any other event on the same day)
    # or we have them in dayBySubstance (scoreByDayBySubstance)
    # s = 0
    for s,data in dayBySubstance.iteritems():
        for d,data2 in data.iteritems():
            # data2 is now a list of all duplicate events
            if len(data2) == 1:
                output.append(data2[0])
            else:
                # calculate the sum and append it instead
                sum = 0
                for dat in data2:
                    sum = sum + float(dat['amount'])
                data2[0]['amount'] = sum
                output.append(data2[0])
    return output

# scores is an array, substance a string and weekdays an array of numbers (0-Mon)
def getSumWeekdays( scores, substance, weekdays ):
    # return how many events (days) for substance on the weekend
    sumWeekdays = 0
    for score in scores:
        d = parse(score['start'])
        if score['substance'] != substance:
            continue
        if d.weekday() in weekdays:
            sumWeekdays = sumWeekdays + 1
    return sumWeekdays


def getDaysOverX( scores, substance, threshold ):
    daysOverX = 0
    for score in scores:
        if score['substance'] != substance:
            continue
        if score['amount'] > threshold:
            daysOverX = daysOverX + 1
    return daysOverX


def coUse( scores, substance1, substance2 ):
    # scores should have gone through mergedDays already!
    coUseN = 0
    coUseS1 = 0
    coUseS2 = 0
    days = []
    for score in scores:
        d = parse(score['start'])
        days.append(d.strftime('%Y-%m-%d'))

    i = 0
    substanceByDay = {}
    for score in scores:
        d = days[i]
        subst = score['substance']
        if d not in substanceByDay:
            substanceByDay[d] = []
        substanceByDay[d].append(score)
        i = i + 1

    for i,scr in substanceByDay.iteritems():
        foundS1 = False
        foundS2 = False
        if len(scr) == 1:
            continue
        for score in scr:
            if score['substance'] == substance1:
                foundS1 = True
            if score['substance'] == substance2:
                foundS2 = True
        if foundS1 and foundS2:
            coUseS1tmp = 0
            coUseS2tmp = 0
            coUseN = coUseN + 1
            try:
                coUseS1tmp = coUseS1 + float(score['amount'])
            except ValueError:
                coninue
            try:
                coUseS2tmp = coUseS2 + float(score['amount'])
            except ValueError:
                continue
            coUseS1 = coUseS1tmp
            coUseS2 = coUseS2tmp

    coUseS1 = coUseS1/coUseN if coUseN > 0 else ''
    coUseS2 = coUseS2/coUseN if coUseN > 0 else ''
    coUseN = coUseN if coUseN > 0 else ''
    return [ coUseN, coUseS1, coUseS2 ]

# look for files to import from the data folder
ROOT   = 'data/' + site
output = []
for path, subdirs, files in os.walk(ROOT):
    for name in files:
        if not name.endswith('.json'):
            continue
        # extract the different fields from the filename
        pGUID = ''
        event_name = ''
        for event in eventList:
            # find out if we have a specific event here
            if event['unique_event_name'] not in name:
                continue
            nameparts = re.match('events_(.*)_' + event['unique_event_name'] + ".json", name)
            pGUID      = nameparts.groups()[0]
            event_name = event['unique_event_name']

        if (pGUID == '') or (event_name == ''):
            print("Warning: could not detect the pGUID or event name in %s, ignore this file" % (name))
            continue

        if pGUID not in participants:
            print("Warning: Could not find this participant in REDCap: %s, skip data" % pGUID)
            continue

        filename = os.path.join(path, name)
        print("Look at this file: %s for %s [%s]" % (filename, pGUID, event_name))

        with open(filename) as data_file:
            scores = json.load(data_file)

        tlfb_cal_scr_assess_date = ''
        if ('status' in scores) and (len(scores['status']) > 0):
            tlfb_cal_scr_assess_date = scores['status'][-1]['date']

        tlfb_cal_scr_mj_avg = ''
        tlfb_cal_scr_sd_avg = ''
        tlfb_cal_scr_bl_avg = ''
        tlfb_cal_scr_nr_avg = ''
        tlfb_cal_scr_bm_avg = ''
        tlfb_cal_scr_ca_avg = ''
        tlfb_cal_scr_cg_avg = ''
        tlfb_cal_scr_co_avg = ''
        tlfb_cal_scr_cc_avg = ''
        tlfb_cal_scr_ec_avg = ''
        tlfb_cal_scr_ex_avg = ''
        tlfb_cal_scr_ha_avg = ''
        tlfb_cal_scr_he_avg = ''
        tlfb_cal_scr_ho_avg = ''
        tlfb_cal_scr_in_avg = ''
        tlfb_cal_scr_me_avg = ''
        tlfb_cal_scr_ot_avg = ''
        tlfb_cal_scr_smj_avg = ''
        tlfb_cal_scr_emj_avg = ''
        tlfb_cal_scr_fmj_avg = ''
        tlfb_cal_scr_mjc_avg = ''
        tlfb_cal_scr_mji_avg = ''
        tlfb_cal_scr_mjt_avg = ''
        tlfb_cal_scr_ke_avg = ''
        tlfb_cal_scr_sm_avg = ''
        tlfb_cal_scr_st_avg = ''
        tlfb_cal_scr_tc_avg = ''
        tlfb_cal_scr_ts_avg = ''
        tlfb_cal_scr_tr_avg = ''
        tlfb_cal_scr_pr_avg = ''
        tlfb_cal_scr_pt_avg = ''
        tlfb_cal_scr_mm_avg = ''
        tlfb_cal_scr_sa_avg = ''
        tlfb_cal_scr_gbh_avg = ''
        tlfb_cal_scr_num_events = ''
        tlfb_cal_scr_co_mjsd_drinks = ''
        tlfb_cal_scr_co_mjsd_mj = ''
        tlfb_cal_scr_co_mjsd_num = ''
        tlfb_cal_scr_num_bde = ''
        
        tlfb_cal_scr_mj_wu = ''
        tlfb_cal_scr_sd_wu = ''
        tlfb_cal_scr_bl_wu = ''
        tlfb_cal_scr_nr_wu = ''
        tlfb_cal_scr_bm_wu = ''
        tlfb_cal_scr_ca_wu = ''
        tlfb_cal_scr_cg_wu = ''
        tlfb_cal_scr_co_wu = ''
        tlfb_cal_scr_cc_wu = ''
        tlfb_cal_scr_ec_wu = ''
        tlfb_cal_scr_ex_wu = ''
        tlfb_cal_scr_ha_wu = ''
        tlfb_cal_scr_in_wu = ''
        tlfb_cal_scr_he_wu = ''
        tlfb_cal_scr_ke_wu = ''
        tlfb_cal_scr_ho_wu = ''
        tlfb_cal_scr_me_wu = ''
        tlfb_cal_scr_ot_wu = ''
        tlfb_cal_scr_smj_wu = ''
        tlfb_cal_scr_emj_wu = ''
        tlfb_cal_scr_fmj_wu = ''
        tlfb_cal_scr_mjc_wu = ''
        tlfb_cal_scr_mji_wu = ''
        tlfb_cal_scr_mjt_wu = ''
        tlfb_cal_scr_sm_wu = ''
        tlfb_cal_scr_st_wu = ''
        tlfb_cal_scr_tc_wu = ''
        tlfb_cal_scr_ts_wu = ''
        tlfb_cal_scr_tr_wu = ''
        tlfb_cal_scr_pr_wu = ''
        tlfb_cal_scr_pt_wu = ''
        tlfb_cal_scr_mm_wu = ''
        tlfb_cal_scr_sa_wu = ''
        tlfb_cal_scr_gbh_wu = ''

        mj_s = 0
        sd_s = 0
        bl_s = 0
        nr_s = 0
        bm_s = 0
        ca_s = 0
        cg_s = 0
        co_s = 0
        cc_s = 0
        ec_s = 0
        ex_s = 0
        ke_s = 0
        ha_s = 0
        he_s = 0
        ho_s = 0
        in_s = 0
        me_s = 0
        ot_s = 0
        smj_s = 0
        emj_s = 0
        fmj_s = 0
        mjc_s = 0
        mji_s = 0
        mjt_s = 0
        sm_s = 0
        st_s = 0
        tc_s = 0
        ts_s = 0
        tr_s = 0
        pr_s = 0
        pt_s = 0
        mm_s = 0
        sa_s = 0
        gbh_s = 0

        mj_avg = 0
        sd_avg = 0
        bl_avg = 0
        nr_avg = 0
        bm_avg = 0
        ca_avg = 0
        cg_avg = 0
        co_avg = 0
        cc_avg = 0
        ec_avg = 0
        ex_avg = 0
        ha_avg = 0
        he_avg = 0
        ho_avg = 0
        in_avg = 0
        ke_avg = 0
        me_avg = 0
        ot_avg = 0
        smj_avg = 0
        emj_avg = 0
        fmj_avg = 0
        mjc_avg = 0
        mji_avg = 0
        mjt_avg = 0
        sm_avg = 0
        st_avg = 0
        tc_avg = 0
        ts_avg = 0
        tr_avg = 0
        pr_avg = 0
        pt_avg = 0
        mm_avg = 0
        sa_avg = 0
        gbh_avg = 0

        numMJ = 0
        numAL = 0
        numBL = 0
        numNR = 0
        numBM = 0
        numCA = 0
        numCG = 0
        numCO = 0
        numCC = 0
        numEC = 0
        numEX = 0
        numKE = 0
        numHA = 0
        numHE = 0
        numHO = 0
        numIN = 0
        numME = 0
        numOT = 0
        numSMJ = 0
        numEMJ = 0
        numFMJ = 0
        numMJC = 0
        numMJI = 0
        numMJT = 0
        numSM = 0
        numST = 0
        numTC = 0
        numTS = 0
        numTR = 0
        numPR = 0
        numPT = 0
        numMM = 0
        numSA = 0
        numGBH = 0
        if ('data' in scores) and (len(scores['data']) > 0):
            # the average is computed per day, even if there are several events on a single day
            # group scores by day
            mergedScores = mergeDays( scores['data'] )
            tlfb_cal_scr_num_events = len(mergedScores)
            tlfb_cal_scr_co_mjsd_mj = ''
            tlfb_cal_scr_co_mjsd_drinks = ''
            [tlfb_cal_scr_co_mjsd_num, tlfb_cal_scr_co_mjsd_mj, tlfb_cal_scr_co_mjsd_drinks] = coUse( mergedScores, 'Marijuana', 'Alcohol' )
            tlfb_cal_scr_num_bde = getDaysOverX( mergedScores, 'Alcohol', 3)
            tlfb_cal_scr_mj_wu  = getSumWeekdays( mergedScores, 'Marijuana', [5,6] )
            tlfb_cal_scr_sd_wu  = getSumWeekdays( mergedScores, 'Alcohol', [5,6] )
            tlfb_cal_scr_bl_wu  = getSumWeekdays( mergedScores, 'Blunts', [5,6] )
            tlfb_cal_scr_nr_wu  = getSumWeekdays( mergedScores, 'Nicotine replacement', [5,6] )
            tlfb_cal_scr_bm_wu  = getSumWeekdays( mergedScores, 'Bittamugen', [5,6] )
            tlfb_cal_scr_ca_wu  = getSumWeekdays( mergedScores, 'Cathinones', [5,6] )
            tlfb_cal_scr_cg_wu  = getSumWeekdays( mergedScores, 'Cigars', [5,6] )
            tlfb_cal_scr_co_wu  = getSumWeekdays( mergedScores, 'Cocaine', [5,6] )
            tlfb_cal_scr_mm_wu  = getSumWeekdays( mergedScores, 'Magic mushrooms', [5,6] )
            tlfb_cal_scr_sa_wu  = getSumWeekdays( mergedScores, 'Saliva', [5,6] )
            tlfb_cal_scr_cc_wu  = getSumWeekdays( mergedScores, 'Cough or cold medicine', [5,6] )
            tlfb_cal_scr_ec_wu  = getSumWeekdays( mergedScores, 'E-cigarettes', [5,6] )
            tlfb_cal_scr_ex_wu  = getSumWeekdays( mergedScores, 'Ecstasy', [5,6] )
            tlfb_cal_scr_ke_wu  = getSumWeekdays( mergedScores, 'Ketamine', [5,6] )
            tlfb_cal_scr_ha_wu  = getSumWeekdays( mergedScores, 'Hallucinogens', [5,6] )
            tlfb_cal_scr_he_wu  = getSumWeekdays( mergedScores, 'Heroin', [5,6] )
            tlfb_cal_scr_ho_wu  = getSumWeekdays( mergedScores, 'Hookah', [5,6] )
            tlfb_cal_scr_in_wu  = getSumWeekdays( mergedScores, 'Inhalants', [5,6] )
            tlfb_cal_scr_me_wu  = getSumWeekdays( mergedScores, 'Methamphetamine', [5,6] )
            tlfb_cal_scr_ot_wu  = getSumWeekdays( mergedScores, 'Other', [5,6] )
            tlfb_cal_scr_smj_wu = getSumWeekdays( mergedScores, 'Smoked MJ', [5,6] )
            tlfb_cal_scr_emj_wu = getSumWeekdays( mergedScores, 'Edible MJ', [5,6] )
            tlfb_cal_scr_fmj_wu = getSumWeekdays( mergedScores, 'Fake MJ', [5,6] )
            tlfb_cal_scr_mjc_wu = getSumWeekdays( mergedScores, 'MJ concentrates', [5,6] )
            tlfb_cal_scr_mji_wu = getSumWeekdays( mergedScores, 'MJ infused alcohol drinks', [5,6] )
            tlfb_cal_scr_mjt_wu = getSumWeekdays( mergedScores, 'MJ tincture', [5,6] )
            tlfb_cal_scr_sm_wu  = getSumWeekdays( mergedScores, 'Stimulant medication', [5,6] )
            tlfb_cal_scr_st_wu  = getSumWeekdays( mergedScores, 'Steroids', [5,6] )
            tlfb_cal_scr_tc_wu  = getSumWeekdays( mergedScores, 'Tobacco chew', [5,6] )
            tlfb_cal_scr_ts_wu  = getSumWeekdays( mergedScores, 'Tobacco smoked', [5,6] )
            tlfb_cal_scr_tr_wu  = getSumWeekdays( mergedScores, 'Tranquilizers or sedatives', [5,6] )
            tlfb_cal_scr_pr_wu  = getSumWeekdays( mergedScores, 'Pain relievers', [5,6] )
            tlfb_cal_scr_pt_wu  = getSumWeekdays( mergedScores, 'Pipe Tabacco', [5,6] )
            tlfb_cal_scr_gbh_wu  = getSumWeekdays( mergedScores, 'GBH', [5,6] )
            
            for event in mergedScores:
                if ('substance' not in event) or (event['substance'] == "undefined"):
                    print("Ignore one event because no substance is defined : %s" % json.dumps(event))
                    continue
                if event['substance'] == "Marijuana":
                    try:
                        mj_s = mj_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numMJ = numMJ + 1
                if event['substance'] == "Alcohol":
                    try:
                        sd_s = sd_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numAL = numAL + 1
                if event['substance'] == "Blunts":
                    try:
                        bl_s = bl_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numBL = numBL + 1
                if event['substance'] == "Nicotine replacement":
                    try:
                        nr_s = nr_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numNR = numNR + 1
                if event['substance'] == "Bittamugen":
                    try:
                        bm_s = bm_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numBM = numBM + 1
                if event['substance'] == "Cathinones":
                    try:
                        ca_s = ca_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numCA = numCA + 1
                if event['substance'] == "Methamphetamine":
                    try:
                        me_s = me_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numME = numME + 1
                if event['substance'] == "Cigars":
                    try:
                        cg_s = cg_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numCG = numCG + 1
                if event['substance'] == "Cocaine":
                    try:
                        co_s = co_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numCO = numCO + 1
                if event['substance'] == "Cough or cold medicine":
                    try:
                        cc_s = cc_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numCC = numCC + 1
                if event['substance'] == "Ketamine":
                    try:
                        ke_s = ke_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numKE = numKE + 1
                if event['substance'] == "E-cigarettes":
                    try:
                        ec_s = ec_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numEC = numEC + 1
                if event['substance'] == "Ecstasy":
                    try:
                        ex_s = ex_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numEX = numEX + 1
                if event['substance'] == "Hallucinogens":
                    try:
                        ha_s = ha_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numHA = numHA + 1
                if event['substance'] == "Heroin":
                    try:
                        he_s = he_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numHE = numHE + 1
                if event['substance'] == "Hookah":
                    try:
                        ho_s = ho_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numHO = numHO + 1
                if event['substance'] == "Inhalants":
                    try:
                        in_s = in_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numIN = numIN + 1
                if event['substance'] == "Other":
                    try:
                        ot_s = ot_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numOT = numOT + 1
                if event['substance'] == "Smoked MJ":
                    try:
                        smj_s = smj_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numSMJ = numSMJ + 1
                if event['substance'] == "Edible MJ":
                    try:
                        emj_s = emj_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numEMJ = numEMJ + 1
                if event['substance'] == "Fake MJ":
                    try:
                        fmj_s = fmj_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numFMJ = numFMJ + 1
                if event['substance'] == "MJ concentrates":
                    try:
                        mjc_s = mjc_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numMJC = numMJC + 1
                if event['substance'] == "MJ infused alcohol drinks":
                    try:
                        mji_s = mji_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numMJI = numMJI + 1
                if event['substance'] == "MJ tincture":
                    try:
                        mjt_s = mjt_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numMJT = numMJT + 1
                if event['substance'] == "Stimulant medication":
                    try:
                        sm_s = sm_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numSM = numSM + 1
                if event['substance'] == "Steroids":
                    try:
                        st_s = st_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numST = numST + 1
                if event['substance'] == "Tobacco chew":
                    try:
                        tc_s = tc_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numTC = numTC + 1
                if event['substance'] == "Tobacco smoked":
                    try:
                        ts_s = ts_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numTS = numTS + 1
                if event['substance'] == "Tranquilizers or sedatives":
                    try:
                        tr_s = tr_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numTR = numTR + 1
                if event['substance'] == "Pain relievers":
                    try:
                        pr_s = pr_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numPR = numPR + 1
                if event['substance'] == "Pipe Tabacco":
                    try:
                        pt_s = pt_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numPT = numPT + 1
                if event['substance'] == "Magic mushrooms":
                    try:
                        mm_s = mm_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numMM = numMM + 1
                if event['substance'] == "Saliva":
                    try:
                        sa_s = sa_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numSA = numSA + 1
                if event['substance'] == "GBH":
                    try:
                        gbh_s = gbh_s + float(event['amount'])
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numGBH = numGBH + 1
            if numMJ > 0:
                mj_avg = "{0:.2f}".format(mj_s / numMJ)
            if numAL > 0:
                sd_avg = "{0:.2f}".format(sd_s / numAL)
            if numBL > 0:
                bl_avg = "{0:.2f}".format(bl_s / numBL)
            if numNR > 0:
                nr_avg = "{0:.2f}".format(nr_s / numNR)
            if numBM > 0:
                bm_avg = "{0:.2f}".format(bm_s / numBM)
            if numCA > 0:
                ca_avg = "{0:.2f}".format(ca_s / numCA)
            if numCG > 0:
                cg_avg = "{0:.2f}".format(cg_s / numCG)
            if numCO > 0:
                co_avg = "{0:.2f}".format(co_s / numCO)
            if numCC > 0:
                cc_avg = "{0:.2f}".format(cc_s / numCC)
            if numEC > 0:
                ec_avg = "{0:.2f}".format(ec_s / numEC)
            if numEX > 0:
                ex_avg = "{0:.2f}".format(ex_s / numEX)
            if numKE > 0:
                ke_avg = "{0:.2f}".format(ke_s / numKE)
            if numHA > 0:
                ha_avg = "{0:.2f}".format(ha_s / numHA)
            if numHE > 0:
                he_avg = "{0:.2f}".format(he_s / numHE)
            if numHO > 0:
                ho_avg = "{0:.2f}".format(ho_s / numHO)
            if numIN > 0:
                in_avg = "{0:.2f}".format(in_s / numIN)
            if numME > 0:
                me_avg = "{0:.2f}".format(me_s / numME)
            if numOT > 0:
                ot_avg = "{0:.2f}".format(ot_s / numOT)
            if numSMJ > 0:
                smj_avg = "{0:.2f}".format(smj_s / numSMJ)
            if numEMJ > 0:
                emj_avg = "{0:.2f}".format(emj_s / numEMJ)
            if numFMJ > 0:
                fmj_avg = "{0:.2f}".format(fmj_s / numFMJ)
            if numMJC > 0:
                mjc_avg = "{0:.2f}".format(mjc_s / numMJC)
            if numMJI > 0:
                mji_avg = "{0:.2f}".format(mji_s / numMJI)
            if numMJT > 0:
                mjt_avg = "{0:.2f}".format(mjt_s / numMJT)
            if numSM > 0:
                sm_avg = "{0:.2f}".format(sm_s / numSM)
            if numST > 0:
                st_avg = "{0:.2f}".format(st_s / numST)
            if numTC > 0:
                tc_avg = "{0:.2f}".format(tc_s / numTC)
            if numTS > 0:
                ts_avg = "{0:.2f}".format(ts_s / numTS)
            if numTR > 0:
                tr_avg = "{0:.2f}".format(tr_s / numTR)
            if numPR > 0:
                pr_avg = "{0:.2f}".format(pr_s / numPR)
            if numPT > 0:
                pt_avg = "{0:.2f}".format(pt_s / numPT)
            if numMM > 0:
                mm_avg = "{0:.2f}".format(mm_s / numMM)
            if numSA > 0:
                sa_avg = "{0:.2f}".format(sa_s / numSA)
            if numGBH > 0:
                gbh_avg = "{0:.2f}".format(gbh_s / numGBH)

        if numMJ > 0:
            tlfb_cal_scr_mj_avg = mj_avg
        if numAL > 0:
            tlfb_cal_scr_sd_avg = sd_avg
        if numBL > 0:
            tlfb_cal_scr_bl_avg = bl_avg
        if numNR > 0:
            tlfb_cal_scr_nr_avg = nr_avg
        if numBM > 0:
            tlfb_cal_scr_bm_avg = bm_avg
        if numCA > 0:
            tlfb_cal_scr_ca_avg = ca_avg
        if numCG > 0:
            tlfb_cal_scr_cg_avg = cg_avg
        if numCO > 0:
            tlfb_cal_scr_co_avg = co_avg
        if numCC > 0:
            tlfb_cal_scr_cc_avg = cc_avg
        if numEC > 0:
            tlfb_cal_scr_ec_avg = ec_avg
        if numEX > 0:
            tlfb_cal_scr_ex_avg = ex_avg
        if numKE > 0:
            tlfb_cal_scr_ke_avg = ke_avg
        if numHA > 0:
            tlfb_cal_scr_ha_avg = ha_avg
        if numHE > 0:
            tlfb_cal_scr_he_avg = he_avg
        if numHO > 0:
            tlfb_cal_scr_ho_avg = ho_avg
        if numIN > 0:
            tlfb_cal_scr_in_avg = in_avg
        if numME > 0:
            tlfb_cal_scr_me_avg = me_avg
        if numOT > 0:
            tlfb_cal_scr_ot_avg = ot_avg
        if numSMJ > 0:
            tlfb_cal_scr_smj_avg = smj_avg
        if numEMJ > 0:
            tlfb_cal_scr_emj_avg = emj_avg
        if numFMJ > 0:
            tlfb_cal_scr_fmj_avg = fmj_avg
        if numMJC > 0:
            tlfb_cal_scr_mjc_avg = mjc_avg
        if numMJI > 0:
            tlfb_cal_scr_mji_avg = mji_avg
        if numMJT > 0:
            tlfb_cal_scr_mjt_avg = mjt_avg
        if numSM > 0:
            tlfb_cal_scr_sm_avg = sm_avg
        if numTC > 0:
            tlfb_cal_scr_tc_avg = tc_avg
        if numTS > 0:
            tlfb_cal_scr_ts_avg = ts_avg
        if numTR > 0:
            tlfb_cal_scr_tr_avg = tr_avg
        if numPT > 0:
            tlfb_cal_scr_pt_avg = pt_avg
        if numPR > 0:
            tlfb_cal_scr_pr_avg = pr_avg
        if numMM > 0:
            tlfb_cal_scr_mm_avg = mm_avg
        if numSA > 0:
            tlfb_cal_scr_sa_avg = sa_avg
        if numST > 0:
            tlfb_cal_scr_st_avg = st_avg
        if numGBH > 0:
            tlfb_cal_scr_gbh_avg = gbh_avg

        output.append({
            'id_redcap': pGUID,
            'redcap_event_name': event_name,
            'tlfb_calendar_scores_daic_use_only_complete': 2,
            'tlfb_cal_scr_assess_date': tlfb_cal_scr_assess_date,
            'tlfb_cal_scr_num_events': tlfb_cal_scr_num_events,
            'tlfb_cal_scr_mj_avg': tlfb_cal_scr_mj_avg,
            'tlfb_cal_scr_mj_ud': numMJ if numMJ > 0 else '',
            'tlfb_cal_scr_mj_td': mj_s if numMJ > 0 else '',
            'tlfb_cal_scr_sd_avg': tlfb_cal_scr_sd_avg,
            'tlfb_cal_scr_sd_ud': numAL if numAL > 0 else '',
            'tlfb_cal_scr_sd_td': sd_s if numAL > 0 else '',
            'tlfb_cal_scr_bl_avg': tlfb_cal_scr_bl_avg,
            'tlfb_cal_scr_bl_ud': numBL if numBL > 0 else '',
            'tlfb_cal_scr_bl_td': bl_s if numBL > 0 else '',
            'tlfb_cal_scr_nr_avg': tlfb_cal_scr_nr_avg,
            'tlfb_cal_scr_nr_ud': numNR if numNR > 0 else '',
            'tlfb_cal_scr_nr_td': nr_s if numNR > 0 else '',
            'tlfb_cal_scr_bm_avg': tlfb_cal_scr_bm_avg,
            'tlfb_cal_scr_bm_ud': numBM if numBM > 0 else '',
            'tlfb_cal_scr_bm_td': bm_s if numBM > 0 else '',
            'tlfb_cal_scr_ca_avg': tlfb_cal_scr_ca_avg,
            'tlfb_cal_scr_ca_ud': numCA if numCA > 0 else '',
            'tlfb_cal_scr_ca_td': ca_s if numCA > 0 else '',
            'tlfb_cal_scr_cg_avg': tlfb_cal_scr_cg_avg,
            'tlfb_cal_scr_cg_ud': numCG if numCG > 0 else '',
            'tlfb_cal_scr_cg_td': cg_s if numCG > 0 else '',
            'tlfb_cal_scr_co_avg': tlfb_cal_scr_co_avg,
            'tlfb_cal_scr_co_ud': numCO if numCO > 0 else '',
            'tlfb_cal_scr_co_td': co_s if numCO > 0 else '',
            'tlfb_cal_scr_cc_avg': tlfb_cal_scr_cc_avg,
            'tlfb_cal_scr_cc_ud': numCC if numCC > 0 else '',
            'tlfb_cal_scr_cc_td': cc_s if numCC > 0 else '',
            'tlfb_cal_scr_ec_avg': tlfb_cal_scr_ec_avg,
            'tlfb_cal_scr_ec_ud': numEC if numEC > 0 else '',
            'tlfb_cal_scr_ec_td': ec_s if numEC > 0 else '',
            'tlfb_cal_scr_ex_avg': tlfb_cal_scr_ex_avg,
            'tlfb_cal_scr_ex_ud': numEX if numEX > 0 else '',
            'tlfb_cal_scr_ex_td': ex_s if numEX > 0 else '',
            'tlfb_cal_scr_ke_avg': tlfb_cal_scr_ke_avg,
            'tlfb_cal_scr_ke_ud': numKE if numKE > 0 else '',
            'tlfb_cal_scr_ke_td': ke_s if numKE > 0 else '',
            'tlfb_cal_scr_ha_avg': tlfb_cal_scr_ha_avg,
            'tlfb_cal_scr_ha_ud': numHA if numHA > 0 else '',
            'tlfb_cal_scr_ha_td': ha_s if numHA > 0 else '',
            'tlfb_cal_scr_he_avg': tlfb_cal_scr_he_avg,
            'tlfb_cal_scr_he_ud': numHE if numHE > 0 else '',
            'tlfb_cal_scr_he_td': he_s if numHE > 0 else '',
            'tlfb_cal_scr_ho_avg': tlfb_cal_scr_ho_avg,
            'tlfb_cal_scr_ho_ud': numHO if numHO > 0 else '',
            'tlfb_cal_scr_ho_td': ho_s if numHO > 0 else '',
            'tlfb_cal_scr_in_avg': tlfb_cal_scr_in_avg,
            'tlfb_cal_scr_in_ud': numIN if numIN > 0 else '',
            'tlfb_cal_scr_in_td': in_s if numIN > 0 else '',
            'tlfb_cal_scr_ot_avg': tlfb_cal_scr_ot_avg,
            'tlfb_cal_scr_ot_ud': numOT if numOT > 0 else '',
            'tlfb_cal_scr_ot_td': ot_s if numOT > 0 else '',
            'tlfb_cal_scr_smj_avg': tlfb_cal_scr_smj_avg,
            'tlfb_cal_scr_smj_ud': numSMJ if numSMJ > 0 else '',
            'tlfb_cal_scr_smj_td': smj_s if numSMJ > 0 else '',
            'tlfb_cal_scr_emj_avg': tlfb_cal_scr_emj_avg,
            'tlfb_cal_scr_emj_ud': numEMJ if numEMJ > 0 else '',
            'tlfb_cal_scr_emj_td': emj_s if numEMJ > 0 else '',
            'tlfb_cal_scr_fmj_avg': tlfb_cal_scr_fmj_avg,
            'tlfb_cal_scr_fmj_ud': numFMJ if numFMJ > 0 else '',
            'tlfb_cal_scr_fmj_td': fmj_s if numFMJ > 0 else '',
            'tlfb_cal_scr_mjc_avg': tlfb_cal_scr_mjc_avg,
            'tlfb_cal_scr_mjc_ud': numMJC if numMJC > 0 else '',
            'tlfb_cal_scr_mjc_td': mjc_s if numMJC > 0 else '',
            'tlfb_cal_scr_mji_avg': tlfb_cal_scr_mji_avg,
            'tlfb_cal_scr_mji_ud': numMJI if numMJI > 0 else '',
            'tlfb_cal_scr_mji_td': mji_s if numMJI > 0 else '',
            'tlfb_cal_scr_mjt_avg': tlfb_cal_scr_mjt_avg,
            'tlfb_cal_scr_mjt_ud': numMJT if numMJT > 0 else '',
            'tlfb_cal_scr_mjt_td': mjt_s if numMJT > 0 else '',
            'tlfb_cal_scr_sm_avg': tlfb_cal_scr_sm_avg,
            'tlfb_cal_scr_sm_ud': numSM if numSM > 0 else '',
            'tlfb_cal_scr_sm_td': sm_s if numSM > 0 else '',
            'tlfb_cal_scr_st_avg': tlfb_cal_scr_st_avg,
            'tlfb_cal_scr_st_ud': numST if numST > 0 else '',
            'tlfb_cal_scr_st_td': st_s if numST > 0 else '',
            'tlfb_cal_scr_tc_avg': tlfb_cal_scr_tc_avg,
            'tlfb_cal_scr_tc_ud': numTC if numTC > 0 else '',
            'tlfb_cal_scr_tc_td': tc_s if numTC > 0 else '',
            'tlfb_cal_scr_ts_avg': tlfb_cal_scr_ts_avg,
            'tlfb_cal_scr_ts_ud': numTS if numTS > 0 else '',
            'tlfb_cal_scr_ts_td': ts_s if numTS > 0 else '',
            'tlfb_cal_scr_tr_avg': tlfb_cal_scr_tr_avg,
            'tlfb_cal_scr_tr_ud': numTR if numTR > 0 else '',
            'tlfb_cal_scr_tr_td': tr_s if numTR > 0 else '',
            'tlfb_cal_scr_pr_avg': tlfb_cal_scr_pr_avg,
            'tlfb_cal_scr_pr_ud': numPR if numPR > 0 else '',
            'tlfb_cal_scr_pr_td': pr_s if numPR > 0 else '',
            'tlfb_cal_scr_pt_avg': tlfb_cal_scr_pt_avg,
            'tlfb_cal_scr_pt_ud': numPT if numPT > 0 else '',
            'tlfb_cal_scr_pt_td': pt_s if numPT > 0 else '',
            'tlfb_cal_scr_mm_avg': tlfb_cal_scr_mm_avg,
            'tlfb_cal_scr_mm_ud': numMM if numMM > 0 else '',
            'tlfb_cal_scr_mm_td': mm_s if numMM > 0 else '',
            'tlfb_cal_scr_me_avg': tlfb_cal_scr_me_avg,
            'tlfb_cal_scr_me_ud': numME if numME > 0 else '',
            'tlfb_cal_scr_me_td': me_s if numME > 0 else '',
            'tlfb_cal_scr_gbh_avg': tlfb_cal_scr_gbh_avg,
            'tlfb_cal_scr_gbh_ud': numGBH if numGBH > 0 else '',
            'tlfb_cal_scr_gbh_td': gbh_s if numGBH > 0 else '',
            'tlfb_cal_scr_sa_avg': tlfb_cal_scr_sa_avg,
            'tlfb_cal_scr_sa_ud': numSA if numSA > 0 else '',
            'tlfb_cal_scr_sa_td': sa_s if numSA > 0 else '',
            'tlfb_cal_scr_co_mjsd_num': tlfb_cal_scr_co_mjsd_num, 
            'tlfb_cal_scr_co_mjsd_mj': tlfb_cal_scr_co_mjsd_mj, 
            'tlfb_cal_scr_co_mjsd_drinks': tlfb_cal_scr_co_mjsd_drinks,
            'tlfb_cal_scr_mj_wu': tlfb_cal_scr_mj_wu if numMJ > 0 else '',
            'tlfb_cal_scr_sd_wu': tlfb_cal_scr_sd_wu if numAL > 0 else '',
            'tlfb_cal_scr_bl_wu': tlfb_cal_scr_bl_wu if numBL > 0 else '',
            'tlfb_cal_scr_nr_wu': tlfb_cal_scr_nr_wu if numNR > 0 else '',
            'tlfb_cal_scr_bm_wu': tlfb_cal_scr_bm_wu if numBM > 0 else '',
            'tlfb_cal_scr_ca_wu': tlfb_cal_scr_ca_wu if numCA > 0 else '',
            'tlfb_cal_scr_cg_wu': tlfb_cal_scr_cg_wu if numCG > 0 else '',
            'tlfb_cal_scr_co_wu': tlfb_cal_scr_co_wu if numCO > 0 else '',
            'tlfb_cal_scr_cc_wu': tlfb_cal_scr_cc_wu if numCC > 0 else '',
            'tlfb_cal_scr_ec_wu': tlfb_cal_scr_ec_wu if numEC > 0 else '',
            'tlfb_cal_scr_ex_wu': tlfb_cal_scr_ex_wu if numEX > 0 else '',
            'tlfb_cal_scr_ke_wu': tlfb_cal_scr_ke_wu if numKE > 0 else '',
            'tlfb_cal_scr_ha_wu': tlfb_cal_scr_ha_wu if numHA > 0 else '',
            'tlfb_cal_scr_he_wu': tlfb_cal_scr_he_wu if numHE > 0 else '',
            'tlfb_cal_scr_ho_wu': tlfb_cal_scr_ho_wu if numHO > 0 else '',
            'tlfb_cal_scr_in_wu': tlfb_cal_scr_in_wu if numIN > 0 else '',
            'tlfb_cal_scr_me_wu': tlfb_cal_scr_me_wu if numME > 0 else '',
            'tlfb_cal_scr_ot_wu': tlfb_cal_scr_ot_wu if numOT > 0 else '',
            'tlfb_cal_scr_smj_wu': tlfb_cal_scr_smj_wu if numSMJ > 0 else '',
            'tlfb_cal_scr_emj_wu': tlfb_cal_scr_emj_wu if numEMJ > 0 else '',
            'tlfb_cal_scr_fmj_wu': tlfb_cal_scr_fmj_wu if numFMJ > 0 else '',
            'tlfb_cal_scr_mjc_wu': tlfb_cal_scr_mjc_wu if numMJC > 0 else '',
            'tlfb_cal_scr_mji_wu': tlfb_cal_scr_mji_wu if numMJI > 0 else '',
            'tlfb_cal_scr_mjt_wu': tlfb_cal_scr_mjt_wu if numMJT > 0 else '',
            'tlfb_cal_scr_sm_wu': tlfb_cal_scr_sm_wu if numSM > 0 else '',
            'tlfb_cal_scr_tc_wu': tlfb_cal_scr_tc_wu if numTC > 0 else '',
            'tlfb_cal_scr_ts_wu': tlfb_cal_scr_ts_wu if numTS > 0 else '',
            'tlfb_cal_scr_tr_wu': tlfb_cal_scr_tr_wu if numTR > 0 else '',
            'tlfb_cal_scr_pr_wu': tlfb_cal_scr_pr_wu if numPR > 0 else '',
            'tlfb_cal_scr_pt_wu': tlfb_cal_scr_pt_wu if numPT > 0 else '',
            'tlfb_cal_scr_mm_wu': tlfb_cal_scr_mm_wu if numMM > 0 else '',
            'tlfb_cal_scr_sa_wu': tlfb_cal_scr_sa_wu if numSA > 0 else '',
            'tlfb_cal_scr_st_wu': tlfb_cal_scr_st_wu if numST > 0 else '',
            'tlfb_cal_scr_gbh_wu': tlfb_cal_scr_gbh_wu if numGBH > 0 else ''
        })

#print("SCORES: %s" % json.dumps(output))
#sys.exit(0)

def chunker(seq, size):
        return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))
        
# now add the values to REDCap
if force == "-f":
    print("Add scores to REDCap...")
    for score_group in chunker(output, 50):
        print("try to add: " + json.dumps(score_group))
        buf = cStringIO.StringIO()
        data = {
            'token': tokens[site],
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'overwriteBehavior': 'overwrite',
            'data': json.dumps(score_group),
            'returnContent': 'count',
            'returnFormat': 'json'
        }
        ch = pycurl.Curl()
        ch.setopt(ch.URL, 'https://abcd-rc.ucsd.edu/redcap/api/')
        ch.setopt(ch.HTTPPOST, data.items())
        ch.setopt(ch.WRITEFUNCTION, buf.write)
        ch.perform()
        ch.close()
        print buf.getvalue()
        buf.close()
        # beauty sleep
        sleep(0.02)
else:        
    print(json.dumps(output, indent=4))
