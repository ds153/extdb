import tornado.ioloop
import tornado.web
import redis

import numpy as np
import json
import os
import datetime

from dateutil.relativedelta import relativedelta

class Homepage(tornado.web.RequestHandler):

	def get(self):

		self.render('extreme.html')

class getExtremeData(tornado.web.RequestHandler):

	def get(self):

		variable = self.get_argument("variable")
		month = self.get_argument("month")
		day = self.get_argument("day")
		product = self.get_argument("product")
		north = self.get_argument("north")
		south = self.get_argument("south")
		east = self.get_argument("east")
		west = self.get_argument("west")

		if day == "":
			if month == "": md = ""
			else: md = month
		else:
			if len(day) < 2: day = "0%s" %day
			md = "%s%s" %(month, day)

		r_extreme = redis.Redis(host='localhost', port=6379)
		r_fields = r_extreme.hkeys("%s_%s_value" %(md, variable))

		values = []
		sids_available = []
		legend = []

		for sid in r_fields:
			lat = r_extreme.hget('lat', sid)
			lng = r_extreme.hget('lng', sid)
			if float(lat) < float(north) and float(lat) > float(south) and float(lng) < float(east) and float(lng) > float(west):
				try:
					if variable == "high_pcpn": values.append(float(r_extreme.hget("%s_%s_value" %(md, variable), sid)))
					else: values.append(int(r_extreme.hget("%s_%s_value" %(md, variable), sid)))
					sids_available.append(sid)
				except: None

		if sids_available == []: geojson = []

		else:
			value_gap = list(map(lambda t: np.percentile(values, t * 20), range(6)))
			# value_gap = np.linspace(min(values), max(values), 6)
			geojson = []

			for sid in sids_available:

				try:
					if variable == "high_pcpn": value = float(r_extreme.hget("%s_%s_value" %(md, variable), sid))
					else: value = int(r_extreme.hget("%s_%s_value" %(md, variable), sid))
					if value == -99: value = "M"
				except: value = "M"

				if variable == "high_pcpn":
					if value > value_gap[4]:
						color = "#00441b"
						if round(value_gap[4], 2) == round(value_gap[5], 2) or round(value_gap[4], 2)+0.01 == round(value_gap[5], 2): symbol = "%.2f" %value_gap[5]
						else: symbol = "%.2f - %.2f" %(value_gap[4]+0.01, value_gap[5])
					elif value > value_gap[3]:
						color = "#006d2c"
						if round(value_gap[3], 2) == round(value_gap[4], 2) or round(value_gap[3], 2)+0.01 == round(value_gap[4], 2): symbol = "%.2f" %value_gap[4]
						else: symbol = "%.2f - %.2f" %(value_gap[3]+0.01, value_gap[4])
					elif value > value_gap[2]:
						color = "#238b45"
						if round(value_gap[2], 2) == round(value_gap[3], 2) or round(value_gap[2], 2)+0.01 == round(value_gap[3], 2): symbol = "%.2f" %value_gap[3]
						else: symbol = "%.2f - %.2f" %(value_gap[2]+0.01, value_gap[3])
					elif value > value_gap[1]:
						color = "#41ab5d"
						if round(value_gap[1], 2) == round(value_gap[2], 2) or round(value_gap[1], 2)+0.01 == round(value_gap[2], 2): symbol = "%.2f" %value_gap[2]
						else: symbol = "%.2f - %.2f" %(value_gap[1]+0.01, value_gap[2])
					else:
						color = "#74c476"
						if round(value_gap[0], 2) == round(value_gap[1], 2): symbol = "%.2f" %value_gap[1]
						else: symbol = "%.2f - %.2f" %(value_gap[0], value_gap[1])

				else:

					if value > int(value_gap[4]):
						if int(value_gap[4]) == int(value_gap[5]) or int(value_gap[4])+1 == int(value_gap[5]): symbol = "%d" %value_gap[5]
						else: symbol = "%d - %d" %(value_gap[4]+1, value_gap[5])
					elif value > int(value_gap[3]):
						if int(value_gap[3]) == int(value_gap[4]) or int(value_gap[3])+1 == int(value_gap[4]): symbol = "%d" %value_gap[4]
						else: symbol = "%d - %d" %(value_gap[3]+1, value_gap[4])
					elif value > int(value_gap[2]):
						if int(value_gap[2]) == int(value_gap[3]) or int(value_gap[2])+1 == int(value_gap[3]): symbol = "%d" %value_gap[3]
						else: symbol = "%d - %d" %(value_gap[2]+1, value_gap[3])
					elif value > int(value_gap[1]):
						if int(value_gap[1]) == int(value_gap[2]) or int(value_gap[1])+1 == int(value_gap[2]): symbol = "%d" %value_gap[2]
						else: symbol = "%d - %d" %(value_gap[1]+1, value_gap[2])
					else:
						if int(value_gap[0]) == int(value_gap[1]): symbol = "%d" %value_gap[1]
						else: symbol = "%d - %d" %(value_gap[0], value_gap[1])

					if variable == "low_mint":
						if value > int(value_gap[4]): color = "#6baed6"
						elif value > int(value_gap[3]): color = "#4292c6"
						elif value > int(value_gap[2]): color = "#2171b5"
						elif value > int(value_gap[1]): color = "#08519c"
						else: color = "#08306b"

					else:
						if value > int(value_gap[4]): color = "#800026"
						elif value > int(value_gap[3]): color = "#bd0026"
						elif value > int(value_gap[2]): color = "#e31a1c"
						elif value > int(value_gap[1]): color = "#fc4e2a"
						else: color = "#fd8d3c"

				if not [symbol, color] in legend: legend.append([symbol, color])

				li_geojson = {
					"type": "Feature",
					"geometry": {
						"type": "Point",
						"coordinates": [
							r_extreme.hget('lng', sid).decode('utf-8'),
							r_extreme.hget('lat', sid).decode('utf-8'),
						]
					},
					"properties": {
						"title": r_extreme.hget('stnname', sid).decode('utf-8'),
						"marker-symbol": symbol,
						"icon": {
							"iconUrl": "/static/%s/number_%s.png" %(color[1:], value),
							"shadowUrl": "/static/shadow.png",
							"iconSize": [32, 37],
							"shadowSize": [70, 25],
							"iconAnchor": [16, 35],
							"shadowAnchor": [35, 23],
							"popupAnchor": [0, -30],
						}
					}
				}

				if product != "dlyqry" and variable != "high_pcpn": li_geojson["properties"]["description"] = "%s<br>Period of Record: %s" %(r_extreme.hget("%s_%s_date" %(md, variable), sid).decode('utf-8'), r_extreme.hget("%s_daterange" %variable, sid).decode('utf-8'))
				elif product == "dlyqry" and variable == "high_pcpn": li_geojson["properties"]["description"] = "value: %s<br>Period of Record: %s" %(value, r_extreme.hget("%s_daterange" %variable, sid).decode('utf-8'))
				elif product != "dlyqry" and variable == "high_pcpn": li_geojson["properties"]["description"] = "%s<br>value: %s<br>Period of Record: %s" %(r_extreme.hget("%s_%s_date" %(md, variable), sid).decode('utf-8'), value, r_extreme.hget("%s_daterange" %variable, sid).decode('utf-8'))
				elif product == "dlyqry" and variable != "high_pcpn": li_geojson["properties"]["description"] = "Period of Record: %s" %r_extreme.hget("%s_daterange" %variable, sid).decode('utf-8')

				if variable == "high_pcpn":

					if value == "M": None
					elif value > 23: value = ">23"
					elif value > 22: value = ">22"
					elif value > 21: value = ">21"
					elif value > 20: value = ">20"
					elif value > 19: value = ">19"
					elif value > 18: value = ">18"
					elif value > 17: value = ">17"
					elif value > 16: value = ">16"
					elif value > 15: value = ">15"
					elif value > 14: value = ">14"
					elif value > 13: value = ">13"
					elif value > 12: value = ">12"
					elif value > 11: value = ">11"
					elif value > 10: value = ">10"
					elif value > 9: value = ">9"
					elif value > 8: value = ">8"
					elif value > 7: value = ">7"
					elif value > 6: value = ">6"
					elif value > 5: value = ">5"
					elif value > 4: value = ">4"
					elif value > 3: value = ">3"
					elif value > 2: value = ">2"
					elif value > 1: value = ">1"
					else: value = "<1"

					li_geojson["properties"]["icon"]["iconUrl"] = "/static/%s/number_%s.png" %(color[1:], value)

				geojson.append(li_geojson)

		if variable == "low_mint": legend.sort(key=lambda t: float(t[0].split(" - ")[0]), reverse=True)
		else: legend.sort(key=lambda t: float(t[0].split(" - ")[0]))

		output = {
			"geojson": geojson,
			"legend": legend,
		}

		return self.write(json.dumps(output))

settings = {
	"static_path": os.path.join(os.path.dirname(__file__), "static"),
}

application = tornado.web.Application([
	(r"/", Homepage),
	(r"/getExtremeData", getExtremeData),
], **settings)

if __name__ == "__main__":
	application.listen(8889)
	tornado.ioloop.IOLoop.instance().start()
