##!/usr/bin/python
# TODO: 
#   - Add support for switch_cpu. when switch, cpu should be "switch_cpus"
#   - Add support for multicores
from optparse import OptionParser
import sys
import re
import json
import types
import math
from xml.etree import ElementTree as ET
import copy
import os
#This is a wrapper over xml parser so that 
#comments are preserved.
#source: http://effbot.org/zone/element-pi.htm
class PIParser(ET.XMLTreeBuilder):
   def __init__(self):
       ET.XMLTreeBuilder.__init__(self)
       # assumes ElementTree 1.2.X
       self._parser.CommentHandler = self.handle_comment
       self._parser.ProcessingInstructionHandler = self.handle_pi
       self._target.start("document", {})

   def close(self):
       self._target.end("document")
       return ET.XMLTreeBuilder.close(self)

   def handle_comment(self, data):
       self._target.start(ET.Comment, {})
       self._target.data(data)
       self._target.end(ET.Comment)

   def handle_pi(self, target, data):
       self._target.start(ET.PI, {})
       self._target.data(target + " " + data)
       self._target.end(ET.PI)

def parse(source):
    return ET.parse(source, PIParser())

class processor():
    def __init__(self,opts,args):
        self.opts = opts
        self.statsFile = args[0]
        self.configFile = args[1]
        self.templateFile = args[2]
        self.outdir = os.path.join(os.getcwd(),opts.outdir)
        # make directory if not exist
        if not os.path.isdir(self.outdir):
            os.mkdir(self.outdir)
        self.cycle = 0
        self.stats = None
        self.config = None
        self.templateMcpat = None
#This list is added by Yaswanth on 27th Jan, 2016 to substitute missing stats from gem5 with zeros. Gem5 doesn't print these stats if they are zero; it prints only if they are non-zero
        self.zero_stats_list = ['ReadReq_accesses::total', 'ReadReq_misses::total', 'WriteReq_accesses::total',  \
                    'WriteReq_hits::total', 'iqInstsIssued', 'int_rename_lookups', 'RenamedOperands', \
                    'int_rename_lookups', 'RenameLookups', 'fp_rename_lookups', 'int_inst_queue_reads', \
                    'int_inst_queue_writes', 'int_regfile_reads', 'int_regfile_writes', 'fp_regfile_reads', \
                    'fp_regfile_writes', \
                    'ReadReq_hits::total', 'WriteReq_hits::total', 'overall_accesses::total', \
                    'overall_misses::total', 'trans_dist::ReadReq', \
                    'fp_rename_lookups', 'fp_regfile_reads', 'fp_regfile_writes','trans_dist::WriteReq', \
                    'system.ruby.L1Cache_Controller.Ifetch.core0','system.ruby.L1Cache_Controller.Load.core0', 'system.ruby.L1Cache_Controller.Store.core0', \
                    'system.ruby.L1Cache_Controller.L2_Replacement.core0', 'system.ruby.l1_cntrl0.L2cache.demand_accesses', \
                    'system.ruby.L1Cache_Controller.Ifetch.core1', 'system.ruby.L1Cache_Controller.Load.core1', \
                    'system.ruby.L1Cache_Controller.Store.core1', 'system.ruby.l1_cntrl1.L2cache.demand_accesses', \
                    'system.ruby.L1Cache_Controller.L2_Replacement.core1', \
                    'system.ruby.network.routers1.msg_count.Request_Control::2', 'system.ruby.network.routers0.msg_count.Request_Control::3', \
                    'system.ruby.network.routers0.msg_count.Response_Data::4', 'system.ruby.network.routers0.msg_count.Response_Control::4', \
                    'system.ruby.network.routers0.msg_count.Writeback_Data::5', 'system.ruby.network.routers0.msg_count.Writeback_Control::2', \
                    'system.ruby.network.routers0.msg_count.Writeback_Control::3', 'system.ruby.network.routers0.msg_count.Writeback_Control::5', \
                    'system.ruby.network.routers0.msg_count.Broadcast_Control::3', 'system.ruby.network.routers0.msg_count.Unblock_Control::5', \
                    'system.ruby.network.routers1.msg_count.Request_Control::2', 'system.ruby.network.routers1.msg_count.Request_Control::3', \
                    'system.ruby.network.routers1.msg_count.Response_Data::4', 'system.ruby.network.routers1.msg_count.Response_Control::4', \
                    'system.ruby.network.routers1.msg_count.Writeback_Data::5', 'system.ruby.network.routers1.msg_count.Writeback_Control::2', \
                    'system.ruby.network.routers1.msg_count.Writeback_Control::3', 'system.ruby.network.routers1.msg_count.Writeback_Control::5', \
                    'system.ruby.network.routers1.msg_count.Broadcast_Control::3', 'system.ruby.network.routers1.msg_count.Unblock_Control::5']        
        self.reps = ["cpus", "cntrl", "core", "routers"]    
        #self.reps = ["cpus0", "cntrl0", "core0", "routers0"]   
    def readStats_dump(self):
        ruby_stats_list = ['system.ruby.L1Cache_Controller.Load', 'system.ruby.L1Cache_Controller.Store', 'system.ruby.L1Cache_Controller.Ifetch', \
                            'system.ruby.L1Cache_Controller.L2_Replacement']
        if self.opts.verbose: print "Reading GEM5 stats from: %s" %  self.statsFile
        F = open(self.statsFile)
        ignores = re.compile(r'^---|^$')
        countline = re.compile(r'^---')
        statLine = re.compile(r'([a-zA-Z0-9_\.:-]+)\s+([-+]?[0-9]+\.[0-9]+|[-+]?[0-9]+|nan|inf)')
        count = 0
        stats = {}                          
        for line in F:
            #ignore empty lines and lines starting with "---"  
            #if not ignores.match(line):
            #The above line is commented and below line is added by Yaswanth on 9th Dec, 2015 to ignore reading some unnecessary lines from stat file which are also not in regex format of statLine
            if not ignores.match(line) and statLine.match(line):
                # count += 1
                statKind = statLine.match(line).group(1)
                statValue = statLine.match(line).group(2)
                #This line is added by Yaswanth on 9th Dec, 2015 to print and debug
                #print "statKind=%s, statValue=%s" % (statKind, statValue)
                if statValue == 'nan':
                    print "\tWarning (stats): %s is nan. Setting it to 0" % statKind
                    statValue = '0'
                stats[statKind] = statValue
            #The below elif clause is added by Yaswanth on 24th Feb, 2016 to read ruby cacheController lines in stats file.
            elif not ignores.match(line) and not statLine.match(line):
                ruby_stats = line.split()
                #if ruby_stats[0] == 'system.ruby.L1Cache_Controller.Load':
                ruby_jump_offset = 4
                ncore = int(len(ruby_stats) / ruby_jump_offset)
                if ruby_stats[0] in ruby_stats_list:
                    # statKind = ruby_stats[0] + '.core0'
                    # statValue = ruby_stats[2]
                    # stats[statKind] = statValue 

                    # print statKind, statValue

                    # statKind = ruby_stats[0] + '.core1'
                    # statValue = ruby_stats[6]
                    # stats[statKind] = statValue

                    # print statKind, statValue
                    for index in range(ncore):
                        statKind = ruby_stats[0] + '.core' + str(index)
                        statValue = ruby_stats[2 + index * ruby_jump_offset]
                        stats[statKind] = statValue 
                        print statKind, statValue
            if countline.match(line):
                # every time the count increment, there is a match of string "--------"
                # but each cycle has "-----start" and "-----end"
                # so there is only 1 cycle every 2 counts
                count += 1
                self.cycle = int(math.floor(count/2))
                if opts.verbose: print "Total cycle: %i" %  self.cycle
                if self.cycle >= 1 and count % 2 == 0:
                    self.stats = stats
                    stats = {}                     
                    self.dumpMcpatOut()
        F.close()
    def dumpMcpatOut(self):
        cyc = self.cycle
        template_print = copy.deepcopy(self.templateMcpat)
        rootElem = template_print
        configMatch = re.compile(r'config\.([a-zA-Z0-9_:\.]+)')
        #replace params with values from the GEM5 config file 
        for param in rootElem.iter('param'):
            name = param.attrib['name']
            value = param.attrib['value']
            if 'config' in value:
                allConfs = configMatch.findall(value)
                for conf in allConfs:
                    confValue = self.getConfValue(conf)
                    value = re.sub("config."+ conf, str(confValue), value)
                if "," in value:
                    exprs = re.split(',', value)
                    if confValue == False: # When getConfValue throw error
                        value = '1'  # This is the default value for the stuff in tempalte that is NOT in the config
                    else: # This is the normal case
                        for i in range(len(exprs)):
                            exprs[i] = str(eval(exprs[i]))
                    param.attrib['value'] = ','.join(exprs)
                else:
                    param.attrib['value'] = str(eval(str(value)))

        #replace stats with values from the GEM5 stats file 
        statRe = re.compile(r'stats\.([a-zA-Z0-9_:\.]+)')
        for stat in rootElem.iter('stat'):
            name = stat.attrib['name']
            value = stat.attrib['value']
            #added by Yaswanth
            #print name
            #print value
            if 'stats' in value:
                allStats = statRe.findall(value)
                expr = value
                for i in range(len(allStats)):
                    if allStats[i] in self.stats:
                        expr = re.sub('stats.%s' % allStats[i], self.stats[allStats[i]], expr)
                    #The else clause below is added by Yaswanth. only the else part of "print statements is there before"
                    else:
                        names_stat = allStats[i].split('.')
                        print names_stat[-1]

                        #if names_stat[-1] == "fp_rename_lookups":
                        if names_stat[-1] in self.zero_stats_list or allStats[i] in zero_stats_list:
                            if names_stat[-1] == 'RenameLookups':
                                expr = re.sub('stats.%s' % allStats[i], '1' , expr)
                            else:
                                expr = re.sub('stats.%s' % allStats[i], '0' , expr)

                        else:
                            print "***WARNING: %s does not exist in stats***, and assumed 1" % allStats[i]
                            print "\t Please use the right stats in your McPAT template file"
                            # Yi still wants unreported stats has a value. So that tool chain could continue
                            expr = re.sub('stats.%s' % allStats[i], '1' , expr)


                if 'config' not in expr and 'stats' not in expr:
                    try:
                        stat.attrib['value'] = str(eval(expr))
                    except ZeroDivisionError, e:
                        stat.attrib['value'] = '0'
                    #stat.attrib['value'] = str(eval(expr))
                    #The above line is commented and try clause is added by Yaswanth to make terms with zero denominator as zero values.

        #Write out the xml file
        if opts.verbose: print "Writing input to McPAT in: %s" % str(cyc) + self.opts.out
        out = os.path.join(self.outdir,str(cyc) + self.opts.out)
        template_print.write(out)
# This method read all cycles to memory at once. Depreciated since slow when cycles are many.
    def readAllStatsFile(self):
        
        ruby_stats_list = ['system.ruby.L1Cache_Controller.Load', 'system.ruby.L1Cache_Controller.Store', 'system.ruby.L1Cache_Controller.Ifetch', \
                            'system.ruby.L1Cache_Controller.L2_Replacement']
        if self.opts.verbose: print "Reading GEM5 stats from: %s" %  self.statsFile
        if self.opts.r is True:
            self.stats = []
        F = open(self.statsFile)
        ignores = re.compile(r'^---|^$')
        countline = re.compile(r'^---')
        statLine = re.compile(r'([a-zA-Z0-9_\.:-]+)\s+([-+]?[0-9]+\.[0-9]+|[-+]?[0-9]+|nan|inf)')
        count = 0
        stats = {}                          
        for line in F:
            #ignore empty lines and lines starting with "---"  
            #if not ignores.match(line):
            #The above line is commented and below line is added by Yaswanth on 9th Dec, 2015 to ignore reading some unnecessary lines from stat file which are also not in regex format of statLine
            if not ignores.match(line) and statLine.match(line):
                # count += 1
                statKind = statLine.match(line).group(1)
                statValue = statLine.match(line).group(2)
                #This line is added by Yaswanth on 9th Dec, 2015 to print and debug
                #print "statKind=%s, statValue=%s" % (statKind, statValue)
                if statValue == 'nan':
                    print "\tWarning (stats): %s is nan. Setting it to 0" % statKind
                    statValue = '0'
                stats[statKind] = statValue
            #The below elif clause is added by Yaswanth on 24th Feb, 2016 to read ruby cacheController lines in stats file.
            elif not ignores.match(line) and not statLine.match(line):
                ruby_stats = line.split()
                #if ruby_stats[0] == 'system.ruby.L1Cache_Controller.Load':
                if ruby_stats[0] in ruby_stats_list:
                    statKind = ruby_stats[0] + '.core0'
                    statValue = ruby_stats[2]
                    stats[statKind] = statValue 

                    print statKind, statValue

                    statKind = ruby_stats[0] + '.core1'
                    statValue = ruby_stats[6]
                    stats[statKind] = statValue

                    print statKind, statValue
            if countline.match(line):
                count += 1
                self.cycle = int(math.floor(count/2))
                if opts.verbose: print "Total cycle: %i" %  self.cycle
                if self.cycle >= 2 and count % 2 == 0:
                    self.stats.append(stats)
                    stats = {}                          
        F.close()
    def readConfigFile(self):
        if opts.verbose: print "Reading config from: %s" % self.configFile
        F = open(self.configFile)
        self.config = json.load(F)
        #print config
        #print config["system"]["membus"]
        #print config["system"]["cpu"][0]["clock"]
        F.close()
    def readMcpatFile(self):
        if opts.verbose: print "Reading McPAT template from: %s" % self.templateFile 
        self.templateMcpat = parse(self.templateFile)
# This method outputs all buffered cycles at once. Depreciated due to speed
    def dumpAllMcpatOut(self):
        for cyc in range(self.cycle):
            template_print = copy.deepcopy(self.templateMcpat)
            rootElem = template_print
            configMatch = re.compile(r'config\.([a-zA-Z0-9_:\.]+)')
            #replace params with values from the GEM5 config file 
            for param in rootElem.iter('param'):
                name = param.attrib['name']
                value = param.attrib['value']
                if 'config' in value:
                    allConfs = configMatch.findall(value)
                    for conf in allConfs:
                        confValue = self.getConfValue(conf)
                        value = re.sub("config."+ conf, str(confValue), value)
                    if "," in value:
                        exprs = re.split(',', value)
                        if confValue == False: # When getConfValue throw error
                            value = '1'  # This is the default value for the stuff in tempalte that is NOT in the config
                        else: # This is the normal case
                            for i in range(len(exprs)):
                                exprs[i] = str(eval(exprs[i]))
                        param.attrib['value'] = ','.join(exprs)
                    else:
                        param.attrib['value'] = str(eval(str(value)))

            #replace stats with values from the GEM5 stats file 
            statRe = re.compile(r'stats\.([a-zA-Z0-9_:\.]+)')
            for stat in rootElem.iter('stat'):
                name = stat.attrib['name']
                value = stat.attrib['value']
                #added by Yaswanth
                #print name
                #print value
                if 'stats' in value:
                    allStats = statRe.findall(value)
                    expr = value
                    for i in range(len(allStats)):
                        if allStats[i] in self.stats:
                            expr = re.sub('stats.%s' % allStats[i], self.stats[allStats[i]], expr)
                        #The else clause below is added by Yaswanth. only the else part of "print statements is there before"
                        else:
                            names_stat = allStats[i].split('.')
                            print names_stat[-1]

                            #if names_stat[-1] == "fp_rename_lookups":
                            if names_stat[-1] in zero_stats_list or allStats[i] in zero_stats_list:
                                if names_stat[-1] == 'RenameLookups':
                                    expr = re.sub('stats.%s' % allStats[i], '1' , expr)
                                else:
                                    expr = re.sub('stats.%s' % allStats[i], '0' , expr)

                            else:
                                print "***WARNING: %s does not exist in stats***, and assumed 1" % allStats[i]
                                print "\t Please use the right stats in your McPAT template file"
                                # Yi still wants unreported stats has a value. So that tool chain could continue
                                expr = re.sub('stats.%s' % allStats[i], '1' , expr)


                    if 'config' not in expr and 'stats' not in expr:
                        try:
                            stat.attrib['value'] = str(eval(expr))
                        except ZeroDivisionError, e:
                            stat.attrib['value'] = '0'
                        #stat.attrib['value'] = str(eval(expr))
                        #The above line is commented and try clause is added by Yaswanth to make terms with zero denominator as zero values.

            #Write out the xml file
            if opts.verbose: print "Writing input to McPAT in: %s" % str(cyc) + self.opts.out
            out = os.path.join(self.outdir,str(cyc) + self.opts.out)
            template_print.write(out)
    # how does this function takes care of abnormal case is certainly questionable. 
    # The main purpose is to make the tool chain work.
    def getConfValue(self,confStr):
        spltConf = re.split('\.', confStr) 
        currConf = self.config
        currHierarchy = ""
        for x in spltConf:
            currHierarchy += x
            try: 
                # This takes care of the case where currConf becomes "None"
                (x not in currConf)
            except Exception, e:
                currConf = 1
                return currConf
            if x not in currConf:
                if isinstance(currConf, types.ListType):
                    #this is mostly for system.cpu* as system.cpu is an array
                    #This could be made better
                    if x not in currConf[0]: 
                        print "%s does not exist in config" % currHierarchy 
                        currConf = 1 
                        # Even it does not exist, Yi still assigned a value to it so that tool-chain could run
                        return currConf
                    else:
                        currConf = currConf[0][x]
                else:
                        print "***WARNING: %s does not exist in config.***" % currHierarchy 
                        print "\t Please use the right config param in your McPAT template file"
            else:
                try: 
                    currConf = currConf[x]
                except KeyError, e:
                    return False
            currHierarchy += "."
        if type(currConf) is list:
            # In some case, currConf becomes a list 
            if len(currConf) == 1: 
                #if it is a list with single value, we just take it out.
                currConf = currConf[0]
            else: 
                #In the other case, we don't know. Your situation is in deep shit. Good Luck.
                print "Parsed data is a list of more than 1 element, this is an unhandled case."
        return currConf






def main():
    global opts
    usage = "usage: %prog [options] <gem5 stats file> <gem5 config file (json)> <mcpat template file>"
    parser = OptionParser(usage=usage)
    parser.add_option("-q", "--quiet", 
        action="store_false", dest="verbose", default=True,
        help="don't print status messages to stdout")
    parser.add_option("-o", "--out", type="string",
        action="store", dest="out", default="mcpat-out.xml",
        help="output file (input to McPAT)")
    # enable batch processing
    parser.add_option("-r",action="store_true", 
        dest="r",help="indicating stats file has multiple cycles")
    parser.add_option('-d',type="string",action='store',dest="outdir",default="output")
    (opts, args) = parser.parse_args()
    if len(args) != 3:
        parser.print_help()
        sys.exit(1)
    # prelimilary attempt, I guess only need to change stat and dump
    # readStatsFile(args[0])
    # readConfigFile(args[1])
    # readMcpatFile(args[2])
    # dumpMcpatOut(opts.out)
    worker = processor(opts,args)
    worker.readConfigFile()
    worker.readMcpatFile()
    worker.readStats_dump()
    #worker.dumpMcpatOut()

#This list is added by Yaswanth on 27th Jan, 2016 to substitute missing stats from gem5 with zeros. Gem5 doesn't print these stats if they are zero; it prints only if they are non-zero
zero_stats_list = ['ReadReq_accesses::total', 'ReadReq_misses::total', 'WriteReq_accesses::total',  \
                    'WriteReq_hits::total', 'iqInstsIssued', 'int_rename_lookups', 'RenamedOperands', \
                    'int_rename_lookups', 'RenameLookups', 'fp_rename_lookups', 'int_inst_queue_reads', \
                    'int_inst_queue_writes', 'int_regfile_reads', 'int_regfile_writes', 'fp_regfile_reads', \
                    'fp_regfile_writes', \
                    'ReadReq_hits::total', 'WriteReq_hits::total', 'overall_accesses::total', \
                    'overall_misses::total', 'trans_dist::ReadReq', \
                    'fp_rename_lookups', 'fp_regfile_reads', 'fp_regfile_writes','trans_dist::WriteReq', \
                    'system.ruby.L1Cache_Controller.Ifetch.core0','system.ruby.L1Cache_Controller.Load.core0', 'system.ruby.L1Cache_Controller.Store.core0', \
                    'system.ruby.L1Cache_Controller.L2_Replacement.core0', 'system.ruby.l1_cntrl0.L2cache.demand_accesses', \
                    'system.ruby.L1Cache_Controller.Ifetch.core1', 'system.ruby.L1Cache_Controller.Load.core1', \
                    'system.ruby.L1Cache_Controller.Store.core1', 'system.ruby.l1_cntrl1.L2cache.demand_accesses', \
                    'system.ruby.L1Cache_Controller.L2_Replacement.core1', \
                    'system.ruby.network.routers1.msg_count.Request_Control::2', 'system.ruby.network.routers0.msg_count.Request_Control::3', \
                    'system.ruby.network.routers0.msg_count.Response_Data::4', 'system.ruby.network.routers0.msg_count.Response_Control::4', \
                    'system.ruby.network.routers0.msg_count.Writeback_Data::5', 'system.ruby.network.routers0.msg_count.Writeback_Control::2', \
                    'system.ruby.network.routers0.msg_count.Writeback_Control::3', 'system.ruby.network.routers0.msg_count.Writeback_Control::5', \
                    'system.ruby.network.routers0.msg_count.Broadcast_Control::3', 'system.ruby.network.routers0.msg_count.Unblock_Control::5', \
                    'system.ruby.network.routers1.msg_count.Request_Control::2', 'system.ruby.network.routers1.msg_count.Request_Control::3', \
                    'system.ruby.network.routers1.msg_count.Response_Data::4', 'system.ruby.network.routers1.msg_count.Response_Control::4', \
                    'system.ruby.network.routers1.msg_count.Writeback_Data::5', 'system.ruby.network.routers1.msg_count.Writeback_Control::2', \
                    'system.ruby.network.routers1.msg_count.Writeback_Control::3', 'system.ruby.network.routers1.msg_count.Writeback_Control::5', \
                    'system.ruby.network.routers1.msg_count.Broadcast_Control::3', 'system.ruby.network.routers1.msg_count.Unblock_Control::5']

    

if __name__ == '__main__':
    main()
