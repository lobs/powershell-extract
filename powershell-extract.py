from datetime import datetime
import json
from Evtx import Evtx as evtx
import sys
import os

LOGS = {
	# date : {
		# time : {
			# ScriptBlockId : {
				# MessageNumber : ScriptBlockText
			# }
		# }
	# }
}


def usage():
	print("./%s Microsoft-Windows-PowerShell%4Operational.evtx" % sys.argv[0])
	print("")

def if_not_dir_create(d):
	if not os.path.exists(d):
		print("Making directory: %s" % d)
		os.makedirs(d)

def output_LOGS():
	base = "powershell_extract"
	if_not_dir_create(base)
	for date, time_d in LOGS.items():
		path = os.path.join(base,date)
		if_not_dir_create(path)
		for time, script_d in time_d.items():
			for script_id, message_d in script_d.items():
				fn = "%s.%s.txt" % (time,script_id)
				cmd = ""
				for i in range(1,len(message_d)+1):
					try:
						cmd+=message_d[str(i)]
					except KeyError:
						cmd+="\n\n### MISSING BLOCK ###\n\n"
				if cmd == "": continue
				fn = os.path.join(path,fn)
				print("Writing file: %s" %fn)
				with open(fn,"w") as f:
					f.write(cmd)

def check_dict(v,k):
	try:
		v[k]
		return True
	except KeyError:
		return False

def add_to_LOGS(system,eventdata):
	global LOGS
	date = datetime.strptime(system.find("{http://schemas.microsoft.com/win/2004/08/events/event}TimeCreated").get("SystemTime"),"%Y-%m-%d %H:%M:%S.%f")
	time = date.strftime("%H_%M_%S")
	date = date.strftime("%Y_%m_%d")
	script_id , message_number , script_block_text = ("","","")

	for data in eventdata.findall("{http://schemas.microsoft.com/win/2004/08/events/event}Data"):
		if data.get("Name") == "ScriptBlockId":
			script_id = data.text

		if data.get("Name") == "MessageNumber":
			message_number = data.text
	
		if data.get("Name") == "ScriptBlockText":
			script_block_text = data.text

	if check_dict(LOGS,date):
		if check_dict(LOGS[date],time):
			if check_dict(LOGS[date][time],script_id):
				LOGS[date][time][script_id][message_number] = script_block_text 
			else:
				LOGS[date][time][script_id] = { message_number : script_block_text }
		else:
			LOGS[date][time]  = { script_id : { message_number : script_block_text } } 
	else:
		LOGS[date] = { time : { script_id : { message_number : script_block_text } } }

	print("Found command ID: %s" % script_id)

def main(f):
	try: 
		with evtx.Evtx(f) as log:
			for record in log.records():
				event = record.lxml()
				if event[0].find("{http://schemas.microsoft.com/win/2004/08/events/event}EventID").text == "4104":
					add_to_LOGS(event[0],event[1])
		output_LOGS()
	except IOError:
		print("IOError. Check permissions and path to the file actually exists.")
		print(usage())

if __name__ == "__main__":
	if len(sys.argv) < 2:
		usage()
	else:
		main(sys.argv[1])
