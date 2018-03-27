"""
Created on June 19th, 2017
@author: rouxpn
"""
import os
import re 
from shutil import copyfile 
from decimal import Decimal 
from random import *

class QValuesParser():
  """
    Parses the PHISICS Qvalues library and replaces the nominal values by the perturbed values 
  """
  def matrix_printer(self, infile, outfile):
    """
      Prints the perturbed Qvalues matrix in the outfile 
      @ In, infile, string, input file name 
      @ In, outfile, string, output file name 
      @ Out, None 
    """
    for line in infile :
      line = line.upper().split()
      line[0] = re.sub(r'(.*?)(\w+)(-)(\d+M?)',r'\1\2\4',line[0])
      for isotopeID in self.listedQValuesDict.iterkeys():
        if line[0] == isotopeID :
          try :
            line[1] = str(self.listedQValuesDict.get(isotopeID))
          except : 
            raise Exception('Error. Check if the unperturbed library has defined values relative to the requested perturbed isotopes')
      try :
        if len(line) > 1:
          line[0] = "{0:<7s}".format(line[0])
          line[1] = "{0:<7s}".format(line[1])
          outfile.writelines(' '+line[0]+line[1]+"\n") 
      except KeyError: 
        pass

  def hardcopy_printer(self,modifiedFile):
    """
      Prints the hardcopied information at the begining of the xml file
      @ In, modifiedFile, string, output temperary file name
      @ Out, None 
    """
    with open(modifiedFile, 'a') as outfile:
      with open(self.inputFiles) as infile:
        for line in infile:
          if not line.split(): continue   # if the line is blank, ignore it 
          if re.match(r'(.*?)\s+\w+\s+\d+.\d+',line) : 
            break
          outfile.writelines(line)
        self.matrix_printer(infile, outfile)
        
  def __init__(self, inputFiles, **pertDict):
    """  
      @ In, inputFiles, string, Qvalues library file 
      @ In, pertDict, dictionary, dictionary of perturbed variables
      @ Out, None
    """
    self.inputFiles = inputFiles
    self.pertQValuesDict = pertDict
    for key, value in self.pertQValuesDict.iteritems(): 
      self.pertQValuesDict[key] = '%.3E' % Decimal(str(value)) #convert the values into scientific values
    self.fileReconstruction()    
    
  def fileReconstruction(self):
    """
      Converts the formatted dictionary pertdict -> {'QVALUES|U235':1.30} 
      into a dictionary of dictionaries that has the format -> {'QVALUES':{'U235':1.30}}
      @ In, None  
      @ Out, None 
    """
    self.listedQValuesDict = {}
    perturbedIsotopes = []
    for i in self.pertQValuesDict.iterkeys() :
      splittedDecayKeywords = i.split('|')
      perturbedIsotopes.append(splittedDecayKeywords[1])
    for i in xrange (0,len(perturbedIsotopes)):
      self.listedQValuesDict[perturbedIsotopes[i]] = {}   # declare all the dictionaries
    for isotopeKeyName, QValue in self.pertQValuesDict.iteritems():
      isotopeName = isotopeKeyName.split('|')
      self.listedQValuesDict[isotopeName[1]] = QValue
    self.printInput()
  
  def removeRandomlyNamedFiles(self, modifiedFile):
    """
      Removes the temporary file with a random name in the working directory
      @ In, modifiedFile, string
      @ Out, None 
    """
    os.remove(modifiedFile)
  
  def generateRandomName(self):
    """
      Generates a random file name for the modified file
      @ In, None
      @ Out, string
    """
    return str(randint(1,1000000000000))+'.dat'  
      
  def printInput(self):
    """
      Prints out the pertubed Qvalues library into a file 
      @ In, None 
      @ Out, None
    """
    modifiedFile = self.generateRandomName()
    open(modifiedFile, 'w')
    self.hardcopy_printer(modifiedFile)
    copyfile(modifiedFile, self.inputFiles)
    self.removeRandomlyNamedFiles(modifiedFile)
