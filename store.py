import requests
import json
import calendar
import datetime
import redis
import argparse
import traceback

from dateutil.relativedelta import relativedelta

stndata_url = 'http://data.srcc.rcc-acis.org/'
stndata_url2 = 'http://data.rcc-acis.org/'

def readvals(param_dict, url, url2):

	try: r = requests.post(url, data=json.dumps(param_dict), headers={'content-type':'application/json'}, timeout=60)
	except: r = requests.post(url2, data=json.dumps(param_dict), headers={'content-type':'application/json'}, timeout=60)
	vals = r.json()

	return vals

def readstnslist():

	file_stns = open('./asos_stns.txt', 'r')
	stnslist = file_stns.readlines()
	file_stns.close()

	li_stns = []
	len_stns = len(stnslist)/30
	for i in range(len_stns):
		stns = ','.join(map(lambda t: t[:-1], stnslist[i*30: (i+1)*30]))
		li_stns.append(stns)
	if not len(stnslist) == len_stns*30:
		li_stns.append(','.join(map(lambda t: t[:-1], stnslist[len_stns*30:])))

	return li_stns

def redisMly(list_stns, coef, sdate):

	if coef == "init":
		for stns in list_stns:
			print(stns)
			for i in range(1, 13): getExtremeData(stns, i, "mly")
	elif coef == "update":
		try:
			sd = datetime.datetime.strptime(sdate, "%m")
			ed = (datetime.datetime.today() - datetime.timedelta(days=1))
			for stns in list_stns:
				print(stns)
				for i in range(abs(relativedelta(sd, ed).months)+1):
					month = (ed - relativedelta(months=i)).month
					getExtremeData(stns, month, "mly")
		except:
			print("Please input month")
			print(traceback.print_exc())

def redisDly(list_stns, coef, sdate):

	for stns in list_stns:
		print(stns)

		if coef == "init":
			for i in range(0, 366):
				date = datetime.date(1904, 1, 1) + datetime.timedelta(days=i)
				md = date.strftime('%m%d')
				getExtremeData(stns, md, "dly")

		elif coef == "update":
			try:
				sd = datetime.datetime.strptime(sdate, "%m%d")
				ed = datetime.datetime.today() - datetime.timedelta(days=1)
				days = (ed - (sd + relativedelta(years=abs(relativedelta(ed, sd).years)))).days+1
				for i in range(days):
					md = (ed - datetime.timedelta(days=i)).strftime('%m%d')
					getExtremeData(stns, md, "dly")
			except:
				print("Please input month and day")
				print(traceback.print_exc())

def getExtremeData(stns, md, coef):

	input_url = "%sMultiStnData" %stndata_url
	input_url2 = "%sMultiStnData" %stndata_url2
	r_extreme = redis.Redis(host='localhost', port=6379)

	if coef == "dly" or coef == "mly":

		if coef == "dly":

			eyear = datetime.date.today().year

			if md == '0229':
				sdate = '1896%s' %md
				eyear = getLeapYear(eyear)
				edate = "%s%s" %(eyear, md)
			else:
				sdate = '1895%s' %md
				edate = "%s%s" %(eyear, md)

			input_dict = {"sids":stns,"sdate":sdate,"edate":edate,"elems":[
				{"name":"mint","interval":[1,0,0],"duration":"dly","smry":{"reduce":"min","add":"date"},"smry_only":1},
				{"name":"maxt","interval":[1,0,0],"duration":"dly","smry":{"reduce":"max","add":"date"},"smry_only":1},
				{"name":"mint","interval":[1,0,0],"duration":"dly","smry":{"reduce":"max","add":"date"},"smry_only":1},
				{"name":"maxt","interval":[1,0,0],"duration":"dly","smry":{"reduce":"min","add":"date"},"smry_only":1},
				{"name":"pcpn","interval":[1,0,0],"duration":"dly","smry":{"reduce":"max","add":"date"},"smry_only":1},
			],"meta":"name,sids,ll,valid_daterange"}

		elif coef == 'mly':

			num_days_1895 = calendar.monthrange(1895, md)[-1]

			eyear = datetime.date.today().year
			num_days = calendar.monthrange(eyear, md)[-1]

			if md < 10: md = "0%s" %md
			else: md = str(md)

			sdate = "1895%s%s" %(md, num_days_1895)
			edate = "%s%s%s" %(eyear, md, num_days)

			input_dict = {"sids":stns,"sdate":sdate,"edate":edate,"elems":[
				{"name":"mint","interval":[1,0,0],"duration":"mtd","reduce":"min","smry":{"reduce":"min","add":"date"},"smry_only":1},
				{"name":"maxt","interval":[1,0,0],"duration":"mtd","reduce":"max","smry":{"reduce":"max","add":"date"},"smry_only":1},
				{"name":"mint","interval":[1,0,0],"duration":"mtd","reduce":"max","smry":{"reduce":"max","add":"date"},"smry_only":1},
				{"name":"maxt","interval":[1,0,0],"duration":"mtd","reduce":"min","smry":{"reduce":"min","add":"date"},"smry_only":1},
				{"name":"pcpn","interval":[1,0,0],"duration":"mtd","reduce":"max","smry":{"reduce":"max","add":"date"},"smry_only":1},
			],"meta":"name,sids,ll,valid_daterange"}

		print(sdate, edate)

		originvals = readvals(input_dict, input_url, input_url2)['data']

		for li_vals in originvals:

			r_extreme.hset('%s_low_mint_value' %md, li_vals['meta']['sids'][0][:-2], li_vals['smry'][0][0])
			r_extreme.hset('%s_low_mint_date' %md, li_vals['meta']['sids'][0][:-2], li_vals['smry'][0][1])
			r_extreme.hset('%s_high_maxt_value' %md, li_vals['meta']['sids'][0][:-2], li_vals['smry'][1][0])
			r_extreme.hset('%s_high_maxt_date' %md, li_vals['meta']['sids'][0][:-2], li_vals['smry'][1][1])
			r_extreme.hset('%s_high_mint_value' %md, li_vals['meta']['sids'][0][:-2], li_vals['smry'][2][0])
			r_extreme.hset('%s_high_mint_date' %md, li_vals['meta']['sids'][0][:-2], li_vals['smry'][2][1])
			r_extreme.hset('%s_low_maxt_value' %md, li_vals['meta']['sids'][0][:-2], li_vals['smry'][3][0])
			r_extreme.hset('%s_low_maxt_date' %md, li_vals['meta']['sids'][0][:-2], li_vals['smry'][3][1])
			r_extreme.hset('%s_high_pcpn_value' %md, li_vals['meta']['sids'][0][:-2], li_vals['smry'][4][0])
			r_extreme.hset('%s_high_pcpn_date' %md, li_vals['meta']['sids'][0][:-2], li_vals['smry'][4][1])
			r_extreme.hset('lng', li_vals['meta']['sids'][0][:-2], li_vals['meta']['ll'][0])
			r_extreme.hset('lat', li_vals['meta']['sids'][0][:-2], li_vals['meta']['ll'][1])
			r_extreme.hset('stnname', li_vals['meta']['sids'][0][:-2], li_vals['meta']['name'])
			r_extreme.hset('low_mint_daterange', li_vals['meta']['sids'][0][:-2], formatDateRange(li_vals['meta']['valid_daterange'][0]))
			r_extreme.hset('high_maxt_daterange', li_vals['meta']['sids'][0][:-2], formatDateRange(li_vals['meta']['valid_daterange'][1]))
			r_extreme.hset('high_mint_daterange', li_vals['meta']['sids'][0][:-2], formatDateRange(li_vals['meta']['valid_daterange'][2]))
			r_extreme.hset('low_maxt_daterange', li_vals['meta']['sids'][0][:-2], formatDateRange(li_vals['meta']['valid_daterange'][3]))
			r_extreme.hset('high_pcpn_daterange', li_vals['meta']['sids'][0][:-2], formatDateRange(li_vals['meta']['valid_daterange'][4]))

	elif coef == "rct":

		date_begin = datetime.datetime.strptime(md, "%Y%m%d")

		for i in range((datetime.datetime.today() - date_begin).days):
			md = (date_begin + datetime.timedelta(days=i)).strftime("%Y%m%d")
			print('md=',md)
			for sid in r_extreme.hkeys('%s_high_maxt_value' %md[4:]):
				rctExtreme(md, sid, r_extreme)

def rctExtreme(md, sid, r_extreme):

	highmaxt_extreme = r_extreme.hget('%s_high_maxt_date' %md[4:], sid)
	lowmaxt_extreme = r_extreme.hget('%s_low_maxt_date' %md[4:], sid)
	lowmint_extreme = r_extreme.hget('%s_low_mint_date' %md[4:], sid)
	highmint_extreme = r_extreme.hget('%s_high_mint_date' %md[4:], sid)
	highpcpn_extreme = r_extreme.hget('%s_high_pcpn_date' %md[4:], sid)

	if md == "%s%s%s" %(highmaxt_extreme[:4], highmaxt_extreme[5:7], highmaxt_extreme[8:]): r_extreme.hset("%s_high_maxt_value" %md, sid, r_extreme.hget('%s_high_maxt_value' %md[4:], sid))
	if md == "%s%s%s" %(lowmaxt_extreme[:4], lowmaxt_extreme[5:7], lowmaxt_extreme[8:]): r_extreme.hset("%s_low_maxt_value" %md, sid, r_extreme.hget('%s_low_maxt_value' %md[4:], sid))
	if md == "%s%s%s" %(lowmint_extreme[:4], lowmint_extreme[5:7], lowmint_extreme[8:]): r_extreme.hset("%s_low_mint_value" %md, sid, r_extreme.hget('%s_low_mint_value' %md[4:], sid))
	if md == "%s%s%s" %(highmint_extreme[:4], highmint_extreme[5:7], highmint_extreme[8:]): r_extreme.hset("%s_high_mint_value" %md, sid, r_extreme.hget('%s_high_mint_value' %md[4:], sid))
	if md == "%s%s%s" %(highpcpn_extreme[:4], highpcpn_extreme[5:7], highpcpn_extreme[8:]): r_extreme.hset("%s_high_pcpn_value" %md, sid, r_extreme.hget('%s_high_pcpn_value' %md[4:], sid))

def getLeapYear(year):

	while not calendar.isleap(year):
		year -= 1

	return year

def getRecentData(list_stns, coef, sdate):

	sd = (datetime.datetime.today() - relativedelta(months=6))

	if coef == "init":
		redisDly(list_stns, "init", "")
		getExtremeData("", sd.strftime("%Y%m01"), "rct")

	elif coef == "update":

		try:
			ed = datetime.datetime.today() - datetime.timedelta(days=1)
			mhs = relativedelta(ed, datetime.datetime.strptime(sdate, "%Y%m%d")).months

			if mhs > 6 or mhs < 0: print("Please input the start date within 6 months")
			else:
				redisDly(list_stns, "update", sdate[4:])
				getExtremeData("", sdate, "rct")
				r_extreme = redis.Redis(host='localhost', port=6379)
				for i in r_extreme.keys(pattern='????????_high_maxt_value'):
					if (datetime.datetime.strptime(i[:8], "%Y%m%d") - sd.replace(day=1)).days < -1:
						print("delete %s" %i[:8])
						r_extreme.delete("%s_high_maxt_value" %i[:8])
						r_extreme.delete("%s_high_mint_value" %i[:8])
						r_extreme.delete("%s_low_maxt_value" %i[:8])
						r_extreme.delete("%s_low_mint_value" %i[:8])
						r_extreme.delete("%s_high_pcpn_value" %i[:8])
		except:
			print("Please input date")
			print(traceback.print_exc())

def getAllTimeData(list_stns):

	edate = datetime.date.today().strftime("%Y%m%d")

	for stns in list_stns:

		print(stns)

		input_dict = {"sids":stns,"sdate":"18950301","edate":edate,"elems":[
			{"name":"mint","duration":"dly","smry":{"reduce":"min","add":"date"},"smry_only":1},
			{"name":"maxt","duration":"dly","smry":{"reduce":"max","add":"date"},"smry_only":1},
			{"name":"mint","duration":"dly","smry":{"reduce":"max","add":"date"},"smry_only":1},
			{"name":"maxt","duration":"dly","smry":{"reduce":"min","add":"date"},"smry_only":1},
			{"name":"pcpn","duration":"dly","smry":{"reduce":"max","add":"date"},"smry_only":1}
		],"meta":"name,sids,ll,valid_daterange"}

		input_url =  "%sMultiStnData" %stndata_url
		input_url2 =  "%sMultiStnData" %stndata_url2
		originvals = readvals(input_dict, input_url, input_url2)["data"]

		r_extreme = redis.Redis(host='localhost', port=6379)

		for vals in originvals:

			r_extreme.hset('_low_mint_value', vals['meta']['sids'][0][:-2], vals['smry'][0][0])
			r_extreme.hset('_low_mint_date', vals['meta']['sids'][0][:-2], vals['smry'][0][1])
			r_extreme.hset('_high_maxt_value', vals['meta']['sids'][0][:-2], vals['smry'][1][0])
			r_extreme.hset('_high_maxt_date', vals['meta']['sids'][0][:-2], vals['smry'][1][1])
			r_extreme.hset('_high_mint_value', vals['meta']['sids'][0][:-2], vals['smry'][2][0])
			r_extreme.hset('_high_mint_date', vals['meta']['sids'][0][:-2], vals['smry'][2][1])
			r_extreme.hset('_low_maxt_value', vals['meta']['sids'][0][:-2], vals['smry'][3][0])
			r_extreme.hset('_low_maxt_date', vals['meta']['sids'][0][:-2], vals['smry'][3][1])
			r_extreme.hset('_high_pcpn_value', vals['meta']['sids'][0][:-2], vals['smry'][4][0])
			r_extreme.hset('_high_pcpn_date', vals['meta']['sids'][0][:-2], vals['smry'][4][1])
			r_extreme.hset('lng', vals['meta']['sids'][0][:-2], vals['meta']['ll'][0])
			r_extreme.hset('lat', vals['meta']['sids'][0][:-2], vals['meta']['ll'][1])
			r_extreme.hset('stnname', vals['meta']['sids'][0][:-2], vals['meta']['name'])
			r_extreme.hset('low_mint_daterange', vals['meta']['sids'][0][:-2], formatDateRange(vals['meta']['valid_daterange'][0]))
			r_extreme.hset('high_maxt_daterange', vals['meta']['sids'][0][:-2], formatDateRange(vals['meta']['valid_daterange'][1]))
			r_extreme.hset('high_mint_daterange', vals['meta']['sids'][0][:-2], formatDateRange(vals['meta']['valid_daterange'][2]))
			r_extreme.hset('low_maxt_daterange', vals['meta']['sids'][0][:-2], formatDateRange(vals['meta']['valid_daterange'][3]))
			r_extreme.hset('high_pcpn_daterange', vals['meta']['sids'][0][:-2], formatDateRange(vals['meta']['valid_daterange'][4]))

def formatDateRange(daterange):

	try:

		sPeriod = daterange[0].split('-')
		ePeriod = daterange[1].split('-')

		output = "%s/%s/%s-%s/%s/%s" %(sPeriod[1], sPeriod[2], sPeriod[0], ePeriod[1], ePeriod[2], ePeriod[0])

	except:

		output = "None"

	return output

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Enter user input and process requested data.')
	parser.add_argument("-mtd", metavar='input', type=str, help='user input: method (get, del, or clear)', choices=['get', 'del', 'clear'], required=True)
	parser.add_argument("-pr", metavar='input', type=str, help='user input: product (mlyetm, dlyetm, rctdly, or altetm)', choices=['mlyetm', 'dlyetm', 'rctdly', 'altetm'])
	parser.add_argument("-init", metavar='input', type=str, help='user input: initilize or update (init or update)', choices=['init', 'update'])
	parser.add_argument("-sd", metavar='input', type=str, help='user input: start date, month_day, or day (e.g. 20141009, 0930, 18)')

	args = parser.parse_args()

	method = args.mtd
	product = args.pr
	datarange = args.init
	sdate = args.sd

	list_stns = readstnslist()

	if method == 'get':
		if product == 'mlyetm':
			if datarange == 'init': redisMly(list_stns, 'init', "")
			elif datarange == 'update':
				if sdate == None: sdate = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%m")
				redisMly(list_stns, 'update', sdate)
		elif product == 'dlyetm':
			if datarange == 'init': redisDly(list_stns, 'init', "")
			elif datarange == 'update':
				if sdate == None: sdate = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%m%d")
				redisDly(list_stns, 'update', sdate)
		elif product == 'altetm': getAllTimeData(list_stns)
		elif product == "rctdly":
			if datarange == "init": getRecentData(list_stns, "init", "")
			elif datarange == "update":
				if sdate == None: sdate = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
				getRecentData(list_stns, "update", sdate)
	elif method == 'del':
		keyextend = ['_low_mint_value', '_low_mint_date', '_high_maxt_value', '_high_maxt_date', '_high_mint_value', '_high_mint_date', '_low_maxt_value', '_low_maxt_date', '_high_pcpn_value', '_high_pcpn_date']
		r_extreme = redis.Redis(host='localhost', port=6379)
		if product == 'mlyetm':
			for i in r_extreme.keys(pattern='??_low_mint_value'):
				for j in keyextend:
					print("delete %s" %i[:2])
					r_extreme.delete("%s%s" %(i[:2], j))
		elif product == 'dlyetm':
			for i in r_extreme.keys(pattern='????_low_mint_value'):
				for j in keyextend:
					print("delete %s" %i[:4])
					r_extreme.delete("%s%s" %(i[:4], j))
		elif product == 'altetm':
			for i in keyextend: r_extreme.delete(i)
		elif product == "rctdly":
			for i in r_extreme.keys(pattern='????????_low_mint_value'):
				print("delete %s" %i[:8])
				r_extreme.delete("%s_high_maxt_value" %i[:8])
				r_extreme.delete("%s_high_mint_value" %i[:8])
				r_extreme.delete("%s_low_maxt_value" %i[:8])
				r_extreme.delete("%s_low_mint_value" %i[:8])
				r_extreme.delete("%s_high_pcpn_value" %i[:8])
	elif method == 'clear':
		r_extreme = redis.Redis(host='localhost', port=6379)
		r_extreme.flushall()
