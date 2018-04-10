"""
Created on July 17th, 2017
@author: rouxpn
"""
from __future__ import division, print_function, unicode_literals, absolute_import
import warnings
warnings.simplefilter('default',DeprecationWarning)
import os
import re
from decimal import Decimal

class PathParser():
  """
    Parses the PHISICS xml decay library located in the path folder (betadecay, alphadecay etc.)
    and replaces the nominal values by the perturbed values.
  """
  def matrixPrinter(self,line,outfile):
    """
      Prints the perturbed decay matrix in the outfile.
      @ In, line, string
      @ In, outfile, string, output file name
      @ Out, None
    """
    line = re.sub(r'(.*?)(\w+)(-)(\d+M?)',r'\1\2\4',line)
    line = line.upper().split()
    if line[0] in self.setOfPerturbedIsotopes:
      try:
        line[1] = str(self.listedQValuesDict.get(line[0]))
      except:
        raise Exception('Error. Check if the unperturbed library has defined values relative to the requested perturbed isotopes')
    if len(line) > 1:
      line[0] = "{0:<7s}".format(line[0])
      line[1] = "{0:<11s}".format(line[1])
      line = ''.join(line[0]+line[1]+"\n")
      outfile.writelines(line)
    if re.search(r'(.*?)END', line[0]):
      self.stopFlag = self.stopFlag + 1
      self.harcodingSection = 0
          
  def __init__(self,inputFiles,workingDir,**pertDict):
    """  
      Constructor.
      @ In, inputFiles, string, decay Qvalue library file
      @ In, workingDir, string, absolute path to working directory
      @ In, pertDict, dictionary, dictionary of perturbed variables
      @ Out, None
    """
    self.inputFiles = inputFiles
    self.pertQValuesDict = pertDict
    for key, value in self.pertQValuesDict.iteritems():
      self.pertQValuesDict[key] = '%.3E' % Decimal(str(value)) #convert the values into scientific values
    self.fileReconstruction()
    self.printInput(workingDir)
    
  def fileReconstruction(self):
    """
      Converts the formatted dictionary -> {'XXXDECAY|U235':1.30, XXXDECAY|FUEL2|U238':4.69}.
      into a dictionary of dictionaries that has the format -> {'XXXDECAY':{'U235':1.30}, 'XXXDECAY':{'U238':4.69}}
      @ In, None
      @ Out, reconstructedDict, nested dictionary
    """
    self.listedQValuesDict = {}
    perturbedIsotopes = []
    for i in self.pertQValuesDict.iterkeys():
      splittedDecayKeywords = i.split('|')
      perturbedIsotopes.append(splittedDecayKeywords[1])
    for i in xrange (0,len(perturbedIsotopes)):
      self.listedQValuesDict[perturbedIsotopes[i]] = {}   # declare all the dictionaries
    for isotopeKeyName, QValue in self.pertQValuesDict.iteritems():
      isotopeName = isotopeKeyName.split('|')
      self.listedQValuesDict[isotopeName[1]] = QValue
    self.setOfPerturbedIsotopes = set(self.listedQValuesDict.iterkeys())
    
  def printInput(self,workingDir):
    """
      Prints out the pertubed decay Qvalues library into a file.
      @ In, workingDir, string, absolute path to working directory
      @ Out, None
    """
    sectionCounter = 0
    self.stopFlag = 0
    self.harcodingSection = 0
    modifiedFile = os.path.join(workingDir,'test.dat')
    open(modifiedFile, 'w')
    with open(modifiedFile, 'a') as outfile:
      with open(self.inputFiles) as infile:
        for line in infile:
          if re.search(r'(.*?)(\s?)[a-zA-Z](\s+Qvalue)',line.strip()):
            sectionCounter = sectionCounter + 1
          if not line.split(): 
            continue  # if the line is blank, ignore it
          if sectionCounter == 1 and self.stopFlag == 0: #actinide section
            self.harcodingSection = 1
            self.matrixPrinter(line, outfile)
          if sectionCounter == 2 and self.stopFlag == 1: #FP section
            self.harcodingSection = 2
            self.matrixPrinter(line, outfile)
          if self.harcodingSection != 1 and self.harcodingSection !=2:
            outfile.writelines(line)
    os.rename(modifiedFile,self.inputFiles)
