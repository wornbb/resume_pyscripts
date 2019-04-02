import argparse
import sys
import regex as re


# declaration of a global variable. 
# I hate to use global variable, but this is the easiest way to pass "trace" with no speed cost.
trace = []

def read_original_output(line):
	# trace is a global variable.
	line = line.strip()
	component = component_pattern.match(line)
	mcpat = mcpat_pattern.match(line)
	if (mcpat):
		return 1
	if end_pattern.match(line):
		trace.append(trace[-1].copy())
		write_tile = False
	if (component):
		unit = component.group(1)
		#if write_tile:
		trace[-1][unit] = 0
	elif unit is not None:
		result = result_pattern.match(line)
		if result:
			trace[-1][unit] += float(result.group(2))
	return 0
def read_simple_output(line):
	line = line.strip()
	component = component_pattern.match(line)
	mcpat = mcpat_pattern.match(line)
	if end_pattern.match(line):
		# The line below does NOT work. It is sad, Python. You suck.
		#new_copy = dict.fromkeys(trace[-1].keys(), [])
		new_copy = {key:[] for key in trace[-1].keys()}
		trace.append(new_copy.copy())
		write_tile = False
	if (component):
		unit = component.group(1)
                if unit == "Core":
                    return 0
		power = component.group(2)
		if power == '-nan' or power == 'inf':
			power = '0'
		AddValue(unit,power)


def AddValue(unit, power):
	# This function is added to handle multi-core case
	# Since in each cycle, the mcpat output does NOT distinguish whether a component is form core 0 or core 1
	# we handle this situation by adding power to a list. So for each cycle, we have multiple power for the same unit
	# this list will be unraveled later.

	# This branch is for add new unit to the trace. Should only be called in cycle 1
	if trace[-1].get(unit)==None:
		trace[-1][unit] = [power]
	# This branch is for add new power to existing unit.	
	else:
		trace[-1][unit].append(power)
def unravel():
	offset = 1
	for key in trace[-1]:
		num_cpu = len(trace[-1][key])
		break
	keys = list(trace[-1].keys())
	for index, t in enumerate(trace):
		new_trace	= {}
		for key, power in t.iteritems():
			for counter, cur_power in enumerate(power):
				new_trace[key+str(counter+offset)] = cur_power		
		trace[index] = new_trace.copy()
		

			
# TODO: Add a configuration for filtering out unwanted components
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("file", nargs='+', type=argparse.FileType('r'),
			help="File containing McPAT output.")
	parser.add_argument("-o", "--output-file", type=argparse.FileType('w'),
			default=sys.stdout, help="HotSpot input file.  If not specified, output will be to the terminal.")
	parser.add_argument("-m", "--mcpat_mode", action='store',default=1, help="Specify the mcpat output mode. (default) 1: simplified mode, 0: original mode")
	args = parser.parse_args()
	
	original_pattern = re.compile(r'^(?!Total| McPAT)\s*(?:\S+\s+)+(\S+):')
	# switch 1 is a output format changing argument in modified McPAT
	switch_1_pattern = re.compile(r'(?!version)([\w]+)\s((\d+.\d*)|-*(\w{3}\b))+')
	# switch_1_pattern = re.compile(r'(?!version)([\w]+)\s(\d+.\d*)+')
	if args.mcpat_mode is 0:
		component_pattern = original_pattern
	else:
		component_pattern = switch_1_pattern
	result_pattern = re.compile(r'^(?!Area)(.*)\s+=\s+((?:\+|-)?\d+.\d+)\s+.*')
	end_pattern = re.compile(r'END')
	mcpat_pattern = re.compile(r'McPAT')
	write_tile = True
        idx = 1
	for file in args.file:
		trace.append({})
		unit = None
		for line in file:
			if args.mcpat_mode is 0:
				cont = read_original_output(line)
				if cont is 1:
					continue
			else:
				read_simple_output(line)
        # the first cycle usually doesn't make any sense. 	
        trace.pop(0) 
	# sicne we append a new trace at every end of cycle, the last one has to be discarded. Otherwise, we have 1 more copy.
	trace.pop()
	unravel()
	a = 0
	for step in trace:
		a = a + 1
		if set(step.keys()) != set(trace[0].keys()):
			print("Components must have the same names in all input files!")
			raise KeyError
	components = trace[0].keys()
	args.output_file.write('\t'.join(components) + '\n')
	for step in trace:
		args.output_file.write('\t'.join([str(step[c]) for c in components]) + '\n')
	args.output_file.write('\n')
