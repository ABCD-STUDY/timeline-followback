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
    'fields[1]': 'demo_sex_v2',
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
sex = {}
for p in v:
    participants[p['id_redcap']] = 1
    sexv = 'U'  # break down to M/F/Unkown/Other
    if 'demo_sex_v2' in p:
        if (p['demo_sex_v2'] == 1) or (p['demo_sex_v2'] == 3):
            sexv = 'M'
        if (p['demo_sex_v2'] == 2) or (p['demo_sex_v2'] == 4):
            sexv = 'F'
        if (p['demo_sex_v2'] == 7) or (p['demo_sex_v2'] == 6):
            sexv = 'U'            
    sex[p['id_redcap']] = sexv


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
    sumUse = 0
    for score in scores:
        d = parse(score['start'])
        if score['substance'] != substance:
            continue
        if d.weekday() in weekdays:
            sumWeekdays = sumWeekdays + 1
            try:
                sumUse = sumUse + float(score['amount'])
            except ValueError:
                print("Error: Amount was not a number: " + score['amount'] + ", skip this value")
                pass
    return [sumWeekdays, sumUse]


def getLastUseDay( scores, substance ):
    lastDay = ''
    dates = []
    for score in scores:
        if score['substance'] != substance:
            continue
        if score['start'] == '':
            continue
        d = parse(score['start'])
        dates.append( d )

    if len(dates) > 0:
        dates.sort()
        return dates[-1].strftime('%Y-%m-%d')
    return ''

def getDaysOverX( scores, substance, threshold ):
    daysOverX = 0
    sumUse = 0
    for score in scores:
        if score['substance'] != substance:
            continue
        try: 
            if float(score['amount']) > threshold:
                daysOverX = daysOverX + 1
            sumUse = sumUse + float(score['amount'])
        except ValueError:
            print("Error: Amount was not a number: " + score['amount'] + ", skip this value")
            pass
    return [daysOverX, sumUse]


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
            if score['substance'] in substance1:
                foundS1 = True
            if score['substance'] in substance2:
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

        tlfb_cal_scr_alc_avg = ''
        tlfb_cal_scr_blunt_avg = ''
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
        tlfb_cal_scr_ket_avg = ''
        tlfb_cal_scr_sm_avg = ''
        tlfb_cal_scr_st_avg = ''
        tlfb_cal_scr_tc_avg = ''
        tlfb_cal_scr_ts_avg = ''
        tlfb_cal_scr_tr_avg = ''
        tlfb_cal_scr_opiaterx_avg = ''
        tlfb_cal_scr_pt_avg = ''
        tlfb_cal_scr_mm_avg = ''
        tlfb_cal_scr_sa_avg = ''
        tlfb_cal_scr_gbh_avg = ''

        tlfb_cal_scr_alc_max = ''
        tlfb_cal_scr_blunt_max = ''
        tlfb_cal_scr_nr_max = ''
        tlfb_cal_scr_bm_max = ''
        tlfb_cal_scr_ca_max = ''
        tlfb_cal_scr_cg_max = ''
        tlfb_cal_scr_co_max = ''
        tlfb_cal_scr_cc_max = ''
        tlfb_cal_scr_ec_max = ''
        tlfb_cal_scr_ex_max = ''
        tlfb_cal_scr_ha_max = ''
        tlfb_cal_scr_he_max = ''
        tlfb_cal_scr_ho_max = ''
        tlfb_cal_scr_in_max = ''
        tlfb_cal_scr_me_max = ''
        tlfb_cal_scr_ot_max = ''
        tlfb_cal_scr_smj_max = ''
        tlfb_cal_scr_emj_max = ''
        tlfb_cal_scr_fmj_max = ''
        tlfb_cal_scr_mjc_max = ''
        tlfb_cal_scr_mji_max = ''
        tlfb_cal_scr_mjt_max = ''
        tlfb_cal_scr_ket_max = ''
        tlfb_cal_scr_sm_max = ''
        tlfb_cal_scr_st_max = ''
        tlfb_cal_scr_tc_max = ''
        tlfb_cal_scr_ts_max = ''
        tlfb_cal_scr_tr_max = ''
        tlfb_cal_scr_opiaterx_max = ''
        tlfb_cal_scr_pt_max = ''
        tlfb_cal_scr_mm_max = ''
        tlfb_cal_scr_sa_max = ''
        tlfb_cal_scr_gbh_max = ''


        tlfb_cal_scr_num_events = ''
        tlfb_cal_scr_co_mjsd_drinks = ''
        tlfb_cal_scr_co_mjsd_mj = ''
        tlfb_cal_scr_co_mjsd_num = ''
        tlfb_cal_scr_co_tomj_to = ''
        tlfb_cal_scr_co_tomj_mj = ''
        tlfb_cal_scr_co_tomj_num = ''
        tlfb_cal_scr_co_toal_to = ''
        tlfb_cal_scr_co_toal_al = ''
        tlfb_cal_scr_co_toal_num = ''
        tlfb_cal_scr_num_bde = ''
        tlfb_cal_scr_tot_bde = ''
        
        tlfb_cal_scr_alc_wu = ''
        tlfb_cal_scr_blunt_wu = ''
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
        tlfb_cal_scr_ket_wu = ''
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
        tlfb_cal_scr_opiaterx_wu = ''
        tlfb_cal_scr_pt_wu = ''
        tlfb_cal_scr_mm_wu = ''
        tlfb_cal_scr_sa_wu = ''
        tlfb_cal_scr_gbh_wu = ''
        
        tlfb_cal_scr_drinksperbinge = ''
        tlfb_cal_scr_num_bde = ''
        tlfb_cal_scr_tot_bde = ''
        
        alc_s = 0
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

        alc_max = 0
        bl_max = 0
        nr_max = 0
        bm_max = 0
        ca_max = 0
        cg_max = 0
        co_max = 0
        cc_max = 0
        ec_max = 0
        ex_max = 0
        ke_max = 0
        ha_max = 0
        he_max = 0
        ho_max = 0
        in_max = 0
        me_max = 0
        ot_max = 0
        smj_max = 0
        emj_max = 0
        fmj_max = 0
        mjc_max = 0
        mji_max = 0
        mjt_max = 0
        sm_max = 0
        st_max = 0
        tc_max = 0
        ts_max = 0
        tr_max = 0
        pr_max = 0
        pt_max = 0
        mm_max = 0
        sa_max = 0
        gbh_max = 0

        alc_avg = 0
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

        numAL = 0
        numBlunt = 0
        numNR = 0
        numBM = 0
        numCA = 0
        numCG = 0
        numCO = 0
        numCC = 0
        numEC = 0
        numEX = 0
        numKET = 0
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
        numOpiaterx = 0
        numPT = 0
        numMM = 0
        numSA = 0
        numGBH = 0
        mergedScores = []
        if ('data' in scores) and (len(scores['data']) > 0):
            # the average is computed per day, even if there are several events on a single day
            # group scores by day
            mergedScores = mergeDays( scores['data'] )
            tlfb_cal_scr_num_events = len(mergedScores)
            tlfb_cal_scr_co_mjsd_mj = ''
            tlfb_cal_scr_co_mjsd_drinks = ''
            tlfb_cal_scr_co_mjsd_num = ''
            [tlfb_cal_scr_co_mjsd_num, tlfb_cal_scr_co_mjsd_mj, tlfb_cal_scr_co_mjsd_drinks] = coUse( mergedScores,
                                                                                                      [ 'Smoked MJ', 'Edible MJ', 'Fake MJ',
                                                                                                        'MJ concentrates', 'MJ infused alcohol drinks',
                                                                                                        'MJ tincture' ], [ 'Alcohol' ] )
            tlfb_cal_scr_co_tomj_to = ''
            tlfb_cal_scr_co_tomj_mj = ''
            tlfb_cal_scr_co_tomj_num = ''
            [tlfb_cal_scr_co_tomj_num, tlfb_cal_scr_co_tomj_to, tlfb_cal_scr_co_tomj_mj] = coUse( mergedScores,
                                                                                                  [ 'Tobacco smoked', 'Nicotine replacement',
                                                                                                    'E-cigarettes', 'Tobacco chew', 'Cigars',
                                                                                                    'Hookah', 'Pipe Tobacco' ],
                                                                                                  [ 'Smoked MJ', 'Edible MJ', 'Fake MJ',
                                                                                                    'MJ concentrates', 'MJ infused alcohol drinks',
                                                                                                    'MJ tincture' ] )
            tlfb_cal_scr_co_toal_al = ''
            tlfb_cal_scr_co_toal_to = ''
            tlfb_cal_scr_co_toal_num = ''
            [tlfb_cal_scr_co_toal_num, tlfb_cal_scr_co_toal_to, tlfb_cal_scr_co_toal_al] = coUse( mergedScores,
                                                                                                  [ 'Tobacco smoked', 'Nicotine replacement',
                                                                                                    'E-cigarettes', 'Tobacco chew', 'Cigars',
                                                                                                    'Hookah', 'Pipe Tobacco' ],
                                                                                                  [ 'Alcohol' ] )
            
            tlfb_cal_scr_num_bde = ''
            tlfb_cal_scr_tot_bde = ''
            tlfb_cal_scr_drinksperbinge = ''
            if sex[pGUID] == 'M':
                [ tlfb_cal_scr_num_bde, tlfb_cal_scr_tot_bde ] = getDaysOverX( mergedScores, 'Alcohol', 4)
            if sex[pGUID] == 'F':
                [ tlfb_cal_scr_num_bde, tlfb_cal_scr_tot_bde ] = getDaysOverX( mergedScores, 'Alcohol', 3)
            if (sex[pGUID] == 'M') or (sex[pGUID] == 'F'):
                if tlfb_cal_scr_num_bde > 0:
                    tlfb_cal_scr_drinksperbinge = tlfb_cal_scr_tot_bde / tlfb_cal_scr_num_bde
            [ tlfb_cal_scr_alc_wu, tlfb_cal_scr_alc_wt ] = getSumWeekdays( mergedScores, 'Alcohol', [5,6] )
            [ tlfb_cal_scr_blunt_wu, tlfb_cal_scr_blunt_wt ]   = getSumWeekdays( mergedScores, 'Blunts', [5,6] )
            [ tlfb_cal_scr_nr_wu, tlfb_cal_scr_nr_wt ]   = getSumWeekdays( mergedScores, 'Nicotine replacement', [5,6] )
            [ tlfb_cal_scr_bm_wu, tlfb_cal_scr_bm_wt ]   = getSumWeekdays( mergedScores, 'Bittamugen', [5,6] )
            [ tlfb_cal_scr_ca_wu, tlfb_cal_scr_ca_wt ]   = getSumWeekdays( mergedScores, 'Cathinones', [5,6] )
            [ tlfb_cal_scr_cg_wu, tlfb_cal_scr_cg_wt ]   = getSumWeekdays( mergedScores, 'Cigars', [5,6] )
            [ tlfb_cal_scr_co_wu, tlfb_cal_scr_co_wt ]   = getSumWeekdays( mergedScores, 'Cocaine', [5,6] )
            [ tlfb_cal_scr_mm_wu, tlfb_cal_scr_mm_wt ]   = getSumWeekdays( mergedScores, 'Magic mushrooms', [5,6] )
            [ tlfb_cal_scr_sa_wu, tlfb_cal_scr_sa_wt ]   = getSumWeekdays( mergedScores, 'Saliva', [5,6] )
            [ tlfb_cal_scr_cc_wu, tlfb_cal_scr_cc_wt ]   = getSumWeekdays( mergedScores, 'Cough or cold medicine', [5,6] )
            [ tlfb_cal_scr_ec_wu, tlfb_cal_scr_ec_wt ]   = getSumWeekdays( mergedScores, 'E-cigarettes', [5,6] )
            [ tlfb_cal_scr_ex_wu, tlfb_cal_scr_ex_wt ]   = getSumWeekdays( mergedScores, 'Ecstasy', [5,6] )
            [ tlfb_cal_scr_ket_wu, tlfb_cal_scr_ket_wt ]   = getSumWeekdays( mergedScores, 'Ketamine', [5,6] )
            [ tlfb_cal_scr_ha_wu, tlfb_cal_scr_ha_wt ]   = getSumWeekdays( mergedScores, 'Hallucinogens', [5,6] )
            [ tlfb_cal_scr_he_wu, tlfb_cal_scr_he_wt ]   = getSumWeekdays( mergedScores, 'Heroin', [5,6] )
            [ tlfb_cal_scr_ho_wu, tlfb_cal_scr_ho_wt ]   = getSumWeekdays( mergedScores, 'Hookah', [5,6] )
            [ tlfb_cal_scr_in_wu, tlfb_cal_scr_in_wt ]   = getSumWeekdays( mergedScores, 'Inhalants', [5,6] )
            [ tlfb_cal_scr_me_wu, tlfb_cal_scr_me_wt ]   = getSumWeekdays( mergedScores, 'Methamphetamine', [5,6] )
            [ tlfb_cal_scr_ot_wu, tlfb_cal_scr_ot_wt ]   = getSumWeekdays( mergedScores, 'Other', [5,6] )
            [ tlfb_cal_scr_smj_wu, tlfb_cal_scr_smj_wt ] = getSumWeekdays( mergedScores, 'Smoked MJ', [5,6] )
            [ tlfb_cal_scr_emj_wu, tlfb_cal_scr_emj_wt ] = getSumWeekdays( mergedScores, 'Edible MJ', [5,6] )
            [ tlfb_cal_scr_fmj_wu, tlfb_cal_scr_fmj_wt ] = getSumWeekdays( mergedScores, 'Fake MJ', [5,6] )
            [ tlfb_cal_scr_mjc_wu, tlfb_cal_scr_mjc_wt ] = getSumWeekdays( mergedScores, 'MJ concentrates', [5,6] )
            [ tlfb_cal_scr_mji_wu, tlfb_cal_scr_mji_wt ] = getSumWeekdays( mergedScores, 'MJ infused alcohol drinks', [5,6] )
            [ tlfb_cal_scr_mjt_wu, tlfb_cal_scr_mjt_wt ] = getSumWeekdays( mergedScores, 'MJ tincture', [5,6] )
            [ tlfb_cal_scr_sm_wu, tlfb_cal_scr_sm_wt ]   = getSumWeekdays( mergedScores, 'Stimulant medication', [5,6] )
            [ tlfb_cal_scr_st_wu, tlfb_cal_scr_st_wt ]   = getSumWeekdays( mergedScores, 'Steroids', [5,6] )
            [ tlfb_cal_scr_tc_wu, tlfb_cal_scr_tc_wt ]   = getSumWeekdays( mergedScores, 'Tobacco chew', [5,6] )
            [ tlfb_cal_scr_ts_wu, tlfb_cal_scr_ts_wt ]   = getSumWeekdays( mergedScores, 'Tobacco smoked', [5,6] )
            [ tlfb_cal_scr_tr_wu, tlfb_cal_scr_tr_wt ]   = getSumWeekdays( mergedScores, 'Tranquilizers or sedatives', [5,6] )
            [ tlfb_cal_scr_opiaterx_wu, tlfb_cal_scr_opiaterx_wt ]   = getSumWeekdays( mergedScores, 'Pain relievers', [5,6] )
            [ tlfb_cal_scr_pt_wu, tlfb_cal_scr_pt_wt ]   = getSumWeekdays( mergedScores, 'Pipe Tobacco', [5,6] )
            [ tlfb_cal_scr_gbh_wu, tlfb_cal_scr_gbh_wt ] = getSumWeekdays( mergedScores, 'GBH', [5,6] )
            
            for event in mergedScores:
                if ('substance' not in event) or (event['substance'] == "undefined"):
                    print("Ignore one event because no substance is defined : %s" % json.dumps(event))
                    continue
                if event['substance'] == "Alcohol":
                    try:
                        alc_s = alc_s + float(event['amount'])
                        alc_max = max(alc_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numAL = numAL + 1
                if event['substance'] == "Blunts":
                    try:
                        bl_s = bl_s + float(event['amount'])
                        bl_max = max(bl_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numBlunt = numBlunt + 1
                if event['substance'] == "Nicotine replacement":
                    try:
                        nr_s = nr_s + float(event['amount'])
                        nr_max = max(nr_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numNR = numNR + 1
                if event['substance'] == "Bittamugen":
                    try:
                        bm_s = bm_s + float(event['amount'])
                        bm_max = max(bm_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numBM = numBM + 1
                if event['substance'] == "Cathinones":
                    try:
                        ca_s = ca_s + float(event['amount'])
                        ca_max = max(ca_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numCA = numCA + 1
                if event['substance'] == "Methamphetamine":
                    try:
                        me_s = me_s + float(event['amount'])
                        me_max = max(me_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numME = numME + 1
                if event['substance'] == "Cigars":
                    try:
                        cg_s = cg_s + float(event['amount'])
                        cg_max = max(cg_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numCG = numCG + 1
                if event['substance'] == "Cocaine":
                    try:
                        co_s = co_s + float(event['amount'])
                        co_max = max(co_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numCO = numCO + 1
                if event['substance'] == "Cough or cold medicine":
                    try:
                        cc_s = cc_s + float(event['amount'])
                        cc_max = max(cc_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numCC = numCC + 1
                if event['substance'] == "Ketamine":
                    try:
                        ke_s = ke_s + float(event['amount'])
                        ke_max = max(ke_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numKET = numKET + 1
                if event['substance'] == "E-cigarettes":
                    try:
                        ec_s = ec_s + float(event['amount'])
                        ec_max = max(ec_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numEC = numEC + 1
                if event['substance'] == "Ecstasy":
                    try:
                        ex_s = ex_s + float(event['amount'])
                        ex_max = max(ex_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numEX = numEX + 1
                if event['substance'] == "Hallucinogens":
                    try:
                        ha_s = ha_s + float(event['amount'])
                        ha_max = max(ha_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numHA = numHA + 1
                if event['substance'] == "Heroin":
                    try:
                        he_s = he_s + float(event['amount'])
                        he_max = max(he_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numHE = numHE + 1
                if event['substance'] == "Hookah":
                    try:
                        ho_s = ho_s + float(event['amount'])
                        ho_max = max(ho_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numHO = numHO + 1
                if event['substance'] == "Inhalants":
                    try:
                        in_s = in_s + float(event['amount'])
                        in_max = max(in_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numIN = numIN + 1
                if event['substance'] == "Other":
                    try:
                        ot_s = ot_s + float(event['amount'])
                        ot_max = max(ot_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numOT = numOT + 1
                if event['substance'] == "Smoked MJ":
                    try:
                        smj_s = smj_s + float(event['amount'])
                        smj_max = max(smj_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numSMJ = numSMJ + 1
                if event['substance'] == "Edible MJ":
                    try:
                        emj_s = emj_s + float(event['amount'])
                        emj_max = max(emj_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numEMJ = numEMJ + 1
                if event['substance'] == "Fake MJ":
                    try:
                        fmj_s = fmj_s + float(event['amount'])
                        fmj_max = max(fmj_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numFMJ = numFMJ + 1
                if event['substance'] == "MJ concentrates":
                    try:
                        mjc_s = mjc_s + float(event['amount'])
                        mjc_max = max(mjc_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numMJC = numMJC + 1
                if event['substance'] == "MJ infused alcohol drinks":
                    try:
                        mji_s = mji_s + float(event['amount'])
                        mji_max = max(mji_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numMJI = numMJI + 1
                if event['substance'] == "MJ tincture":
                    try:
                        mjt_s = mjt_s + float(event['amount'])
                        mjt_max = max(mjt_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numMJT = numMJT + 1
                if event['substance'] == "Stimulant medication":
                    try:
                        sm_s = sm_s + float(event['amount'])
                        sm_max = max(sm_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numSM = numSM + 1
                if event['substance'] == "Steroids":
                    try:
                        st_s = st_s + float(event['amount'])
                        st_max = max(st_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numST = numST + 1
                if event['substance'] == "Tobacco chew":
                    try:
                        tc_s = tc_s + float(event['amount'])
                        tc_max = max(tc_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numTC = numTC + 1
                if event['substance'] == "Tobacco smoked":
                    try:
                        ts_s = ts_s + float(event['amount'])
                        ts_max = max(ts_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numTS = numTS + 1
                if event['substance'] == "Tranquilizers or sedatives":
                    try:
                        tr_s = tr_s + float(event['amount'])
                        tr_max = max(tr_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numTR = numTR + 1
                if event['substance'] == "Pain relievers":
                    try:
                        pr_s = pr_s + float(event['amount'])
                        pr_max = max(pr_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numOpiaterx = numOpiaterx + 1
                if event['substance'] == "Pipe Tabacco":
                    try:
                        pt_s = pt_s + float(event['amount'])
                        pt_max = max(pt_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numPT = numPT + 1
                if event['substance'] == "Magic mushrooms":
                    try:
                        mm_s = mm_s + float(event['amount'])
                        mm_max = max(mm_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numMM = numMM + 1
                if event['substance'] == "Saliva":
                    try:
                        sa_s = sa_s + float(event['amount'])
                        sa_max = max(sa_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numSA = numSA + 1
                if event['substance'] == "GBH":
                    try:
                        gbh_s = gbh_s + float(event['amount'])
                        gbh_max = max(gbh_max, float(event['amount']))
                    except ValueError:
                        print("Value Error: \"%s\" should be number. Skip this event." % event['amount'])
                        continue
                    numGBH = numGBH + 1
            if numAL > 0:
                alc_avg = "{0:.2f}".format(alc_s / numAL)
            if numBlunt > 0:
                bl_avg = "{0:.2f}".format(bl_s / numBlunt)
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
            if numKET > 0:
                ke_avg = "{0:.2f}".format(ke_s / numKET)
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
            if numOpiaterx > 0:
                pr_avg = "{0:.2f}".format(pr_s / numOpiaterx)
            if numPT > 0:
                pt_avg = "{0:.2f}".format(pt_s / numPT)
            if numMM > 0:
                mm_avg = "{0:.2f}".format(mm_s / numMM)
            if numSA > 0:
                sa_avg = "{0:.2f}".format(sa_s / numSA)
            if numGBH > 0:
                gbh_avg = "{0:.2f}".format(gbh_s / numGBH)

        if numAL > 0:
            tlfb_cal_scr_alc_avg = alc_avg
            tlfb_cal_scr_alc_max = alc_max
        if numBlunt > 0:
            tlfb_cal_scr_blunt_avg = bl_avg
            tlfb_cal_scr_blunt_max = bl_max
        if numNR > 0:
            tlfb_cal_scr_nr_avg = nr_avg
            tlfb_cal_scr_nr_max = nr_max
        if numBM > 0:
            tlfb_cal_scr_bm_avg = bm_avg
            tlfb_cal_scr_bm_max = bm_max
        if numCA > 0:
            tlfb_cal_scr_ca_avg = ca_avg
            tlfb_cal_scr_ca_max = ca_max
        if numCG > 0:
            tlfb_cal_scr_cg_avg = cg_avg
            tlfb_cal_scr_cg_max = cg_max
        if numCO > 0:
            tlfb_cal_scr_co_avg = co_avg
            tlfb_cal_scr_co_max = co_max
        if numCC > 0:
            tlfb_cal_scr_cc_avg = cc_avg
            tlfb_cal_scr_cc_max = cc_max
        if numEC > 0:
            tlfb_cal_scr_ec_avg = ec_avg
            tlfb_cal_scr_ec_max = ec_max
        if numEX > 0:
            tlfb_cal_scr_ex_avg = ex_avg
            tlfb_cal_scr_ex_max = ex_max
        if numKET > 0:
            tlfb_cal_scr_ket_avg = ke_avg
            tlfb_cal_scr_ket_max = ke_max
        if numHA > 0:
            tlfb_cal_scr_ha_avg = ha_avg
            tlfb_cal_scr_ha_max = ha_max
        if numHE > 0:
            tlfb_cal_scr_he_avg = he_avg
            tlfb_cal_scr_he_max = he_max
        if numHO > 0:
            tlfb_cal_scr_ho_avg = ho_avg
            tlfb_cal_scr_ho_avg = ho_avg
        if numIN > 0:
            tlfb_cal_scr_in_max = in_max
        if numME > 0:
            tlfb_cal_scr_me_avg = me_avg
            tlfb_cal_scr_me_max = me_max
        if numOT > 0:
            tlfb_cal_scr_ot_avg = ot_avg
            tlfb_cal_scr_ot_max = ot_max
        if numSMJ > 0:
            tlfb_cal_scr_smj_avg = smj_avg
            tlfb_cal_scr_smj_max = smj_max
        if numEMJ > 0:
            tlfb_cal_scr_emj_avg = emj_avg
            tlfb_cal_scr_emj_max = emj_max
        if numFMJ > 0:
            tlfb_cal_scr_fmj_avg = fmj_avg
            tlfb_cal_scr_fmj_max = fmj_max
        if numMJC > 0:
            tlfb_cal_scr_mjc_avg = mjc_avg
            tlfb_cal_scr_mjc_max = mjc_max
        if numMJI > 0:
            tlfb_cal_scr_mji_avg = mji_avg
            tlfb_cal_scr_mji_max = mji_max
        if numMJT > 0:
            tlfb_cal_scr_mjt_avg = mjt_avg
            tlfb_cal_scr_mjt_max = mjt_max
        if numSM > 0:
            tlfb_cal_scr_sm_avg = sm_avg
            tlfb_cal_scr_sm_avg = sm_avg
        if numTC > 0:
            tlfb_cal_scr_tc_max = tc_max
        if numTS > 0:
            tlfb_cal_scr_ts_avg = ts_avg
            tlfb_cal_scr_ts_avg = ts_max
        if numTR > 0:
            tlfb_cal_scr_tr_avg = tr_avg
            tlfb_cal_scr_tr_max = tr_max
        if numPT > 0:
            tlfb_cal_scr_pt_avg = pt_avg
            tlfb_cal_scr_pt_max = pt_max
        if numOpiaterx > 0:
            tlfb_cal_scr_opiaterx_avg = pr_avg
            tlfb_cal_scr_opiaterx_max = pr_max
        if numMM > 0:
            tlfb_cal_scr_mm_avg = mm_avg
            tlfb_cal_scr_mm_max = mm_max
        if numSA > 0:
            tlfb_cal_scr_sa_avg = sa_avg
            tlfb_cal_scr_sa_max = sa_max
        if numST > 0:
            tlfb_cal_scr_st_avg = st_avg
            tlfb_cal_scr_st_max = st_max
        if numGBH > 0:
            tlfb_cal_scr_gbh_avg = gbh_avg
            tlfb_cal_scr_gbh_max = gbh_max

        output.append({
            'id_redcap': pGUID,
            'redcap_event_name': event_name,
            'tlfb_calendar_scores_daic_use_only_complete': 2,
            'tlfb_cal_scr_assess_date': tlfb_cal_scr_assess_date,
            'tlfb_cal_scr_num_events': tlfb_cal_scr_num_events,
            'tlfb_cal_scr_alc_avg': tlfb_cal_scr_alc_avg,
            'tlfb_cal_scr_alc_max': tlfb_cal_scr_alc_max,
            'tlfb_cal_scr_alc_ud': numAL if numAL > 0 else '',
            'tlfb_cal_scr_alc_td': alc_s if numAL > 0 else '',
            'tlfb_cal_scr_alc_lud': getLastUseDay(mergedScores, 'Alcohol'),
            'tlfb_cal_scr_blunt_avg': tlfb_cal_scr_blunt_avg,
            'tlfb_cal_scr_blunt_max': tlfb_cal_scr_blunt_max,
            'tlfb_cal_scr_blunt_ud': numBlunt if numBlunt > 0 else '',
            'tlfb_cal_scr_blunt_td': bl_s if numBlunt > 0 else '',
            'tlfb_cal_scr_blunt_lud': getLastUseDay(mergedScores, 'Blunts'),
            'tlfb_cal_scr_nicrx_avg': tlfb_cal_scr_nr_avg,
            'tlfb_cal_scr_nicrx_max': tlfb_cal_scr_nr_max,
            'tlfb_cal_scr_nicrx_ud': numNR if numNR > 0 else '',
            'tlfb_cal_scr_nicrx_td': nr_s if numNR > 0 else '',
            'tlfb_cal_scr_nicrx_lud': getLastUseDay(mergedScores, 'Nicotine replacement'),
            'tlfb_cal_scr_fake_avg': tlfb_cal_scr_bm_avg,
            'tlfb_cal_scr_fake_max': tlfb_cal_scr_bm_max,
            'tlfb_cal_scr_fake_ud': numBM if numBM > 0 else '',
            'tlfb_cal_scr_fake_td': bm_s if numBM > 0 else '',
            'tlfb_cal_scr_fake_lud': getLastUseDay(mergedScores, 'Bittamugen'),
            'tlfb_cal_scr_bthslt_avg': tlfb_cal_scr_ca_avg,
            'tlfb_cal_scr_bthslt_max': tlfb_cal_scr_ca_max,
            'tlfb_cal_scr_bthslt_ud': numCA if numCA > 0 else '',
            'tlfb_cal_scr_bthslt_td': ca_s if numCA > 0 else '',
            'tlfb_cal_scr_bthslt_lud': getLastUseDay(mergedScores, 'Cathinones'),
            'tlfb_cal_scr_cg_avg': tlfb_cal_scr_cg_avg,
            'tlfb_cal_scr_cg_max': tlfb_cal_scr_cg_max,
            'tlfb_cal_scr_cg_ud': numCG if numCG > 0 else '',
            'tlfb_cal_scr_cg_td': cg_s if numCG > 0 else '',
            'tlfb_cal_scr_cg_lud': getLastUseDay(mergedScores, 'Cigars'),
            'tlfb_cal_scr_coc_avg': tlfb_cal_scr_co_avg,
            'tlfb_cal_scr_coc_max': tlfb_cal_scr_co_max,
            'tlfb_cal_scr_coc_ud': numCO if numCO > 0 else '',
            'tlfb_cal_scr_coc_td': co_s if numCO > 0 else '',
            'tlfb_cal_scr_coc_lud': getLastUseDay(mergedScores, 'Cocaine'),
            'tlfb_cal_scr_dxm_avg': tlfb_cal_scr_cc_avg,
            'tlfb_cal_scr_dxm_max': tlfb_cal_scr_cc_max,
            'tlfb_cal_scr_dxm_ud': numCC if numCC > 0 else '',
            'tlfb_cal_scr_dxm_td': cc_s if numCC > 0 else '',
            'tlfb_cal_scr_dxm_lud': getLastUseDay(mergedScores, 'Cough or cold medicine'),
            'tlfb_cal_scr_ecig_avg': tlfb_cal_scr_ec_avg,
            'tlfb_cal_scr_ecig_max': tlfb_cal_scr_ec_max,
            'tlfb_cal_scr_ecig_ud': numEC if numEC > 0 else '',
            'tlfb_cal_scr_ecig_td': ec_s if numEC > 0 else '',
            'tlfb_cal_scr_ecig_lud': getLastUseDay(mergedScores, 'E-cigarettes'),
            'tlfb_cal_scr_mdma_avg': tlfb_cal_scr_ex_avg,
            'tlfb_cal_scr_mdma_max': tlfb_cal_scr_ex_max,
            'tlfb_cal_scr_mdma_ud': numEX if numEX > 0 else '',
            'tlfb_cal_scr_mdma_td': ex_s if numEX > 0 else '',
            'tlfb_cal_scr_mdma_lud': getLastUseDay(mergedScores, 'Ecstasy'),
            'tlfb_cal_scr_ket_avg': tlfb_cal_scr_ket_avg,
            'tlfb_cal_scr_ket_max': tlfb_cal_scr_ket_max,
            'tlfb_cal_scr_ket_ud': numKET if numKET > 0 else '',
            'tlfb_cal_scr_ket_td': ke_s if numKET > 0 else '',
            'tlfb_cal_scr_ket_lud': getLastUseDay(mergedScores, 'Ketamine'),
            'tlfb_cal_scr_hall_avg': tlfb_cal_scr_ha_avg,
            'tlfb_cal_scr_hall_max': tlfb_cal_scr_ha_max,
            'tlfb_cal_scr_hall_ud': numHA if numHA > 0 else '',
            'tlfb_cal_scr_hall_td': ha_s if numHA > 0 else '',
            'tlfb_cal_scr_hall_lud': getLastUseDay(mergedScores, 'Hallucinogens'),
            'tlfb_cal_scr_opiate_avg': tlfb_cal_scr_he_avg,
            'tlfb_cal_scr_opiate_max': tlfb_cal_scr_he_max,
            'tlfb_cal_scr_opiate_ud': numHE if numHE > 0 else '',
            'tlfb_cal_scr_opiate_td': he_s if numHE > 0 else '',
            'tlfb_cal_scr_opiate_lud': getLastUseDay(mergedScores, 'Heroin'),
            'tlfb_cal_scr_hooka_avg': tlfb_cal_scr_ho_avg,
            'tlfb_cal_scr_hooka_max': tlfb_cal_scr_ho_max,
            'tlfb_cal_scr_hooka_ud': numHO if numHO > 0 else '',
            'tlfb_cal_scr_hooka_td': ho_s if numHO > 0 else '',
            'tlfb_cal_scr_hooka_lud': getLastUseDay(mergedScores, 'Hookah'),
            'tlfb_cal_scr_inhal_avg': tlfb_cal_scr_in_avg,
            'tlfb_cal_scr_inhal_max': tlfb_cal_scr_in_max,
            'tlfb_cal_scr_inhal_ud': numIN if numIN > 0 else '',
            'tlfb_cal_scr_inhal_td': in_s if numIN > 0 else '',
            'tlfb_cal_scr_inhal_lud': getLastUseDay(mergedScores, 'Inhalants'),
            'tlfb_cal_scr_ot_avg': tlfb_cal_scr_ot_avg,
            'tlfb_cal_scr_ot_max': tlfb_cal_scr_ot_max,
            'tlfb_cal_scr_ot_ud': numOT if numOT > 0 else '',
            'tlfb_cal_scr_ot_td': ot_s if numOT > 0 else '',
            'tlfb_cal_scr_ot_lud': getLastUseDay(mergedScores, 'Other'),
            'tlfb_cal_scr_smj_avg': tlfb_cal_scr_smj_avg,
            'tlfb_cal_scr_smj_max': tlfb_cal_scr_smj_max,
            'tlfb_cal_scr_smj_ud': numSMJ if numSMJ > 0 else '',
            'tlfb_cal_scr_smj_td': smj_s if numSMJ > 0 else '',
            'tlfb_cal_scr_smj_lud': getLastUseDay(mergedScores, 'Smoked MJ'),
            'tlfb_cal_scr_emj_avg': tlfb_cal_scr_emj_avg,
            'tlfb_cal_scr_emj_max': tlfb_cal_scr_emj_max,
            'tlfb_cal_scr_emj_ud': numEMJ if numEMJ > 0 else '',
            'tlfb_cal_scr_emj_td': emj_s if numEMJ > 0 else '',
            'tlfb_cal_scr_emj_lud': getLastUseDay(mergedScores, 'Edible MJ'),
            'tlfb_cal_scr_k2_avg': tlfb_cal_scr_fmj_avg,
            'tlfb_cal_scr_k2_max': tlfb_cal_scr_fmj_max,
            'tlfb_cal_scr_k2_ud': numFMJ if numFMJ > 0 else '',
            'tlfb_cal_scr_k2_td': fmj_s if numFMJ > 0 else '',
            'tlfb_cal_scr_k2_lud': getLastUseDay(mergedScores, 'Fake MJ'),
            'tlfb_cal_scr_dab_avg': tlfb_cal_scr_mjc_avg,
            'tlfb_cal_scr_dab_max': tlfb_cal_scr_mjc_max,
            'tlfb_cal_scr_dab_ud': numMJC if numMJC > 0 else '',
            'tlfb_cal_scr_dab_td': mjc_s if numMJC > 0 else '',
            'tlfb_cal_scr_dab_lud': getLastUseDay(mergedScores, 'MJ concentrates'),
            'tlfb_cal_scr_mjalc_avg': tlfb_cal_scr_mji_avg,
            'tlfb_cal_scr_mjalc_max': tlfb_cal_scr_mji_max,
            'tlfb_cal_scr_mjalc_ud': numMJI if numMJI > 0 else '',
            'tlfb_cal_scr_mjalc_td': mji_s if numMJI > 0 else '',
            'tlfb_cal_scr_mjalc_lud': getLastUseDay(mergedScores, 'MJ infused alcohol drinks'),
            'tlfb_cal_scr_mjt_avg': tlfb_cal_scr_mjt_avg,
            'tlfb_cal_scr_mjt_max': tlfb_cal_scr_mjt_max,
            'tlfb_cal_scr_mjt_ud': numMJT if numMJT > 0 else '',
            'tlfb_cal_scr_mjt_td': mjt_s if numMJT > 0 else '',
            'tlfb_cal_scr_mjt_lud': getLastUseDay(mergedScores, 'MJ tincture'),
            'tlfb_cal_scr_stimrx_avg': tlfb_cal_scr_sm_avg,
            'tlfb_cal_scr_stimrx_max': tlfb_cal_scr_sm_max,
            'tlfb_cal_scr_stimrx_ud': numSM if numSM > 0 else '',
            'tlfb_cal_scr_stimrx_td': sm_s if numSM > 0 else '',
            'tlfb_cal_scr_stimrx_lud': getLastUseDay(mergedScores, 'Stimulant medication'),
            'tlfb_cal_scr_roid_avg': tlfb_cal_scr_st_avg,
            'tlfb_cal_scr_roid_max': tlfb_cal_scr_st_max,
            'tlfb_cal_scr_roid_ud': numST if numST > 0 else '',
            'tlfb_cal_scr_roid_td': st_s if numST > 0 else '',
            'tlfb_cal_scr_roid_lud': getLastUseDay(mergedScores, 'Steroids'),
            'tlfb_cal_scr_chew_avg': tlfb_cal_scr_tc_avg,
            'tlfb_cal_scr_chew_max': tlfb_cal_scr_tc_max,
            'tlfb_cal_scr_chew_ud': numTC if numTC > 0 else '',
            'tlfb_cal_scr_chew_td': tc_s if numTC > 0 else '',
            'tlfb_cal_scr_chew_lud': getLastUseDay(mergedScores, 'Tobacco chew'),
            'tlfb_cal_scr_cig_avg': tlfb_cal_scr_ts_avg,
            'tlfb_cal_scr_cig_max': tlfb_cal_scr_ts_max,
            'tlfb_cal_scr_cig_ud': numTS if numTS > 0 else '',
            'tlfb_cal_scr_cig_td': ts_s if numTS > 0 else '',
            'tlfb_cal_scr_cig_lud': getLastUseDay(mergedScores, 'Tobacco smoked'),
            'tlfb_cal_scr_sedrx_avg': tlfb_cal_scr_tr_avg,
            'tlfb_cal_scr_sedrx_max': tlfb_cal_scr_tr_max,
            'tlfb_cal_scr_sedrx_ud': numTR if numTR > 0 else '',
            'tlfb_cal_scr_sedrx_td': tr_s if numTR > 0 else '',
            'tlfb_cal_scr_sedrx_lud': getLastUseDay(mergedScores, 'Tranquilizers or sedatives'),
            'tlfb_cal_scr_opiaterx_avg': tlfb_cal_scr_opiaterx_avg,
            'tlfb_cal_scr_opiaterx_max': tlfb_cal_scr_opiaterx_max,
            'tlfb_cal_scr_opiaterx_ud': numOpiaterx if numOpiaterx > 0 else '',
            'tlfb_cal_scr_opiaterx_td': pr_s if numOpiaterx > 0 else '',
            'tlfb_cal_scr_opiaterx_lud': getLastUseDay(mergedScores, 'Heroin'),
            'tlfb_cal_scr_pipe_avg': tlfb_cal_scr_pt_avg,
            'tlfb_cal_scr_pipe_max': tlfb_cal_scr_pt_max,
            'tlfb_cal_scr_pipe_ud': numPT if numPT > 0 else '',
            'tlfb_cal_scr_pipe_td': pt_s if numPT > 0 else '',
            'tlfb_cal_scr_pipe_lud': getLastUseDay(mergedScores, 'Pipe Tobacco'),
            'tlfb_cal_scr_shroom_avg': tlfb_cal_scr_mm_avg,
            'tlfb_cal_scr_shroom_max': tlfb_cal_scr_mm_max,
            'tlfb_cal_scr_shroom_ud': numMM if numMM > 0 else '',
            'tlfb_cal_scr_shroom_td': mm_s if numMM > 0 else '',
            'tlfb_cal_scr_shroom_lud': getLastUseDay(mergedScores, 'Magic mushroom'),
            'tlfb_cal_scr_meth_avg': tlfb_cal_scr_me_avg,
            'tlfb_cal_scr_meth_max': tlfb_cal_scr_me_max,
            'tlfb_cal_scr_meth_ud': numME if numME > 0 else '',
            'tlfb_cal_scr_meth_td': me_s if numME > 0 else '',
            'tlfb_cal_scr_meth_lud': getLastUseDay(mergedScores, 'Methamphetamine'),
            'tlfb_cal_scr_gbh_avg': tlfb_cal_scr_gbh_avg,
            'tlfb_cal_scr_gbh_max': tlfb_cal_scr_gbh_max,
            'tlfb_cal_scr_gbh_ud': numGBH if numGBH > 0 else '',
            'tlfb_cal_scr_gbh_td': gbh_s if numGBH > 0 else '',
            'tlfb_cal_scr_gbh_lud': getLastUseDay(mergedScores, 'GBH'),
            'tlfb_cal_scr_sal_avg': tlfb_cal_scr_sa_avg,
            'tlfb_cal_scr_sal_max': tlfb_cal_scr_sa_max,
            'tlfb_cal_scr_sal_ud': numSA if numSA > 0 else '',
            'tlfb_cal_scr_sal_td': sa_s if numSA > 0 else '',
            'tlfb_cal_scr_sal_lud': getLastUseDay(mergedScores, 'Saliva'),
            'tlfb_cal_scr_co_mjsd_num': tlfb_cal_scr_co_mjsd_num, 
            'tlfb_cal_scr_co_mjsd_mj': tlfb_cal_scr_co_mjsd_mj, 
            'tlfb_cal_scr_co_mjsd_drinks': tlfb_cal_scr_co_mjsd_drinks,
            'tlfb_cal_scr_co_tomj_num': tlfb_cal_scr_co_tomj_num, 
            'tlfb_cal_scr_co_tomj_to': tlfb_cal_scr_co_tomj_to, 
            'tlfb_cal_scr_co_tomj_mj': tlfb_cal_scr_co_tomj_mj,
            'tlfb_cal_scr_co_toal_num': tlfb_cal_scr_co_toal_num, 
            'tlfb_cal_scr_co_toal_to': tlfb_cal_scr_co_toal_to, 
            'tlfb_cal_scr_co_toal_al': tlfb_cal_scr_co_toal_al,
            'tlfb_cal_scr_num_bde': tlfb_cal_scr_num_bde,
            'tlfb_cal_scr_tot_bde': tlfb_cal_scr_tot_bde,
            'tlfb_cal_scr_drinksperbinge': tlfb_cal_scr_drinksperbinge,
            'tlfb_cal_scr_alc_wu': tlfb_cal_scr_alc_wu if numAL > 0 else '',
            'tlfb_cal_scr_blunt_wu': tlfb_cal_scr_blunt_wu if numBlunt > 0 else '',
            'tlfb_cal_scr_nicrx_wu': tlfb_cal_scr_nr_wu if numNR > 0 else '',
            'tlfb_cal_scr_fake_wu': tlfb_cal_scr_bm_wu if numBM > 0 else '',
            'tlfb_cal_scr_bthslt_wu': tlfb_cal_scr_ca_wu if numCA > 0 else '',
            'tlfb_cal_scr_cg_wu': tlfb_cal_scr_cg_wu if numCG > 0 else '',
            'tlfb_cal_scr_coc_wu': tlfb_cal_scr_co_wu if numCO > 0 else '',
            'tlfb_cal_scr_dxm_wu': tlfb_cal_scr_cc_wu if numCC > 0 else '',
            'tlfb_cal_scr_ecig_wu': tlfb_cal_scr_ec_wu if numEC > 0 else '',
            'tlfb_cal_scr_mdma_wu': tlfb_cal_scr_ex_wu if numEX > 0 else '',
            'tlfb_cal_scr_ket_wu': tlfb_cal_scr_ket_wu if numKET > 0 else '',
            'tlfb_cal_scr_hall_wu': tlfb_cal_scr_ha_wu if numHA > 0 else '',
            'tlfb_cal_scr_opiate_wu': tlfb_cal_scr_he_wu if numHE > 0 else '',
            'tlfb_cal_scr_hooka_wu': tlfb_cal_scr_ho_wu if numHO > 0 else '',
            'tlfb_cal_scr_inhal_wu': tlfb_cal_scr_in_wu if numIN > 0 else '',
            'tlfb_cal_scr_meth_wu': tlfb_cal_scr_me_wu if numME > 0 else '',
            'tlfb_cal_scr_ot_wu': tlfb_cal_scr_ot_wu if numOT > 0 else '',
            'tlfb_cal_scr_smj_wu': tlfb_cal_scr_smj_wu if numSMJ > 0 else '',
            'tlfb_cal_scr_emj_wu': tlfb_cal_scr_emj_wu if numEMJ > 0 else '',
            'tlfb_cal_scr_k2_wu': tlfb_cal_scr_fmj_wu if numFMJ > 0 else '',
            'tlfb_cal_scr_dab_wu': tlfb_cal_scr_mjc_wu if numMJC > 0 else '',
            'tlfb_cal_scr_mjalc_wu': tlfb_cal_scr_mji_wu if numMJI > 0 else '',
            'tlfb_cal_scr_mjt_wu': tlfb_cal_scr_mjt_wu if numMJT > 0 else '',
            'tlfb_cal_scr_stimrx_wu': tlfb_cal_scr_sm_wu if numSM > 0 else '',
            'tlfb_cal_scr_chew_wu': tlfb_cal_scr_tc_wu if numTC > 0 else '',
            'tlfb_cal_scr_cig_wu': tlfb_cal_scr_ts_wu if numTS > 0 else '',
            'tlfb_cal_scr_sedrx_wu': tlfb_cal_scr_tr_wu if numTR > 0 else '',
            'tlfb_cal_scr_opiaterx_wu': tlfb_cal_scr_opiaterx_wu if numOpiaterx > 0 else '',
            'tlfb_cal_scr_pipe_wu': tlfb_cal_scr_pt_wu if numPT > 0 else '',
            'tlfb_cal_scr_shroom_wu': tlfb_cal_scr_mm_wu if numMM > 0 else '',
            'tlfb_cal_scr_sal_wu': tlfb_cal_scr_sa_wu if numSA > 0 else '',
            'tlfb_cal_scr_roid_wu': tlfb_cal_scr_st_wu if numST > 0 else '',
            'tlfb_cal_scr_gbh_wu': tlfb_cal_scr_gbh_wu if numGBH > 0 else '',
            
            'tlfb_cal_scr_alc_wt': tlfb_cal_scr_alc_wt if numAL > 0 else '',
            'tlfb_cal_scr_blunt_wt': tlfb_cal_scr_blunt_wt if numBlunt > 0 else '',
            'tlfb_cal_scr_nicrx_wt': tlfb_cal_scr_nr_wt if numNR > 0 else '',
            'tlfb_cal_scr_fake_wt': tlfb_cal_scr_bm_wt if numBM > 0 else '',
            'tlfb_cal_scr_bthslt_wt': tlfb_cal_scr_ca_wt if numCA > 0 else '',
            'tlfb_cal_scr_cg_wt': tlfb_cal_scr_cg_wt if numCG > 0 else '',
            'tlfb_cal_scr_coc_wt': tlfb_cal_scr_co_wt if numCO > 0 else '',
            'tlfb_cal_scr_dxm_wt': tlfb_cal_scr_cc_wt if numCC > 0 else '',
            'tlfb_cal_scr_ecig_wt': tlfb_cal_scr_ec_wt if numEC > 0 else '',
            'tlfb_cal_scr_mdma_wt': tlfb_cal_scr_ex_wt if numEX > 0 else '',
            'tlfb_cal_scr_ket_wt': tlfb_cal_scr_ket_wt if numKET > 0 else '',
            'tlfb_cal_scr_hall_wt': tlfb_cal_scr_ha_wt if numHA > 0 else '',
            'tlfb_cal_scr_opiate_wt': tlfb_cal_scr_he_wt if numHE > 0 else '',
            'tlfb_cal_scr_hooka_wt': tlfb_cal_scr_ho_wt if numHO > 0 else '',
            'tlfb_cal_scr_inhal_wt': tlfb_cal_scr_in_wt if numIN > 0 else '',
            'tlfb_cal_scr_meth_wt': tlfb_cal_scr_me_wt if numME > 0 else '',
            'tlfb_cal_scr_ot_wt': tlfb_cal_scr_ot_wt if numOT > 0 else '',
            'tlfb_cal_scr_smj_wt': tlfb_cal_scr_smj_wt if numSMJ > 0 else '',
            'tlfb_cal_scr_emj_wt': tlfb_cal_scr_emj_wt if numEMJ > 0 else '',
            'tlfb_cal_scr_k2_wt': tlfb_cal_scr_fmj_wt if numFMJ > 0 else '',
            'tlfb_cal_scr_dab_wt': tlfb_cal_scr_mjc_wt if numMJC > 0 else '',
            'tlfb_cal_scr_mjalc_wt': tlfb_cal_scr_mji_wt if numMJI > 0 else '',
            'tlfb_cal_scr_mjt_wt': tlfb_cal_scr_mjt_wt if numMJT > 0 else '',
            'tlfb_cal_scr_stimrx_wt': tlfb_cal_scr_sm_wt if numSM > 0 else '',
            'tlfb_cal_scr_chew_wt': tlfb_cal_scr_tc_wt if numTC > 0 else '',
            'tlfb_cal_scr_cig_wt': tlfb_cal_scr_ts_wt if numTS > 0 else '',
            'tlfb_cal_scr_sedrx_wt': tlfb_cal_scr_tr_wt if numTR > 0 else '',
            'tlfb_cal_scr_opiaterx_wt': tlfb_cal_scr_opiaterx_wt if numOpiaterx > 0 else '',
            'tlfb_cal_scr_pipe_wt': tlfb_cal_scr_pt_wt if numPT > 0 else '',
            'tlfb_cal_scr_shroom_wt': tlfb_cal_scr_mm_wt if numMM > 0 else '',
            'tlfb_cal_scr_sal_wt': tlfb_cal_scr_sa_wt if numSA > 0 else '',
            'tlfb_cal_scr_roid_wt': tlfb_cal_scr_st_wt if numST > 0 else '',
            'tlfb_cal_scr_gbh_wt': tlfb_cal_scr_gbh_wt if numGBH > 0 else ''
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
