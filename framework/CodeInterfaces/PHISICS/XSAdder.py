"""
Created on June 19th, 2017
@author: rouxpn
"""

import os
import sys
import re 
from shutil import copyfile 
import fileinput 
from decimal import Decimal
import xml.etree.ElementTree as ET 
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom

class XSAdder():

  def replaceValues(self, genericXMLdict):
    """
    replace the values from the perturbed dict and put them in the deconstructed original dictionary
    """
    setXML = set(genericXMLdict)
    #print setXML
    setPertDict = set(self.pertDict)
    #print setPertDict
    for key in setPertDict.intersection(setXML):
      genericXMLdict[key] = self.pertDict.get(key, {})
    #print genericXMLdict
    return genericXMLdict

  def dictFormating_from_perturbed_to_generic(self, XMLdict):
    """
    Transform the ditionary comning from the XML input into the templated dictionary.
    The templated format is {DENSITY|FUEL|ISOTOPE}
    """
    genericXMLdict = {}
    #print XMLdict
    for paramXML in XMLdict.iterkeys():
      for tabXML in XMLdict.get(paramXML).iterkeys():
        for matXML in XMLdict.get(paramXML).get(tabXML).iterkeys():
          for isotopeXML in XMLdict.get(paramXML).get(tabXML).get(matXML).iterkeys():
            for reactionXML in XMLdict.get(paramXML).get(tabXML).get(matXML).get(isotopeXML).iterkeys():
              for groupXML, pertValue in XMLdict.get(paramXML).get(tabXML).get(matXML).get(isotopeXML).get(reactionXML).iteritems():
                genericXMLdict[paramXML.upper()+'|'+str(tabXML).upper()+'|'+matXML.upper()+'|'+isotopeXML.upper()+'|'+reactionXML.upper()+'|'+str(groupXML).upper()] = pertValue 
    #print genericXMLdict
    return genericXMLdict

  def dictFormating_from_XML_to_perturbed(self):
    """
    Transform the dictionary of dictionaries from the XML tree to a dictionary of dictionaries
    formatted identically as the perturbed dictionary 
    the perturbed dictionary template is {'XS':{'FUEL1':{'u238':{'FISSION':{'1':1.000}}}}}
    """
    # declare the dictionaries 
    XMLdict = {}
    matList = []
    isotopeList = []
    reactionList = []
    XMLdict['XS'] = {}
    reactionList = []
    """
    count = 0 
    tab   = 0 
    dummyTabDict = {}
    mappingDict  = {}
    for tabXML in self.root.getiterator('tab'):
      #print tabXML.attrib.get('name')
      if tabXML.attrib.get('name') in tabNames: 
        numberOfTabPoints = len(tabNames)
        #print numberOfTabPoints
        tabDict[tuple(tabNames)] = tuple(tabValues) 
        #print tabDict
        tabNames = [] 
        tabValues = []
        break         
      else: 
        tabName = tabXML.attrib.get('name')
        tabValue = tabXML.text
        tabNames.append(tabName)
        tabValues.append(tabValue)
    #print numberOfTabPoints    
    
    for tabXML in self.root.getiterator('tab'):
      dummyTabDict[tabXML.attrib.get('name')] = tabXML.text
      count = count + 1 
      if count == numberOfTabPoints:
        tab = tab + 1 
        mappingDict[tab] = dummyTabDict
        count = 0 
        dummyTabDict = {}
    #print mappingDict
    
    count = 0
    tab   = 0 
    """
    count = 0
    for tabulationXML in self.root.getiterator('tabulation'):
      #print count 
      count = count + 1 
      XMLdict['XS'][count] = {}
      #print tabulationXML.attrib.get('name')
      for libraryXML in tabulationXML.getiterator('library'):
        #print libraryXML.attrib.get('lib_name')
        currentMat = libraryXML.attrib.get('lib_name')
        XMLdict['XS'][count][libraryXML.attrib.get('lib_name')] = {}
        for isotopeXML in libraryXML.getiterator('isotope'):
          currentIsotope = isotopeXML.attrib.get('id')
          currentType = isotopeXML.attrib.get('type')
          #print currentType
          reactionList = [j.tag for j in isotopeXML]
          #print reactionList
          XMLdict['XS'][count][libraryXML.attrib.get('lib_name')][isotopeXML.attrib.get('id')+isotopeXML.attrib.get('type')] = {}
          #print XMLdict
          for k in xrange (0, len(reactionList)):
            XMLdict['XS'][count][libraryXML.attrib.get('lib_name')][isotopeXML.attrib.get('id')+isotopeXML.attrib.get('type')][reactionList[k]] = {}
            for groupXML in isotopeXML.getiterator(reactionList[k]):
              individualGroup = [x.strip() for x in groupXML.attrib.get('g').split(',')]
              individualGroupValues = [y.strip() for y in groupXML.text.split(',')]
              #print (individualGroup+individualGroupValues)
              for position in xrange(0,len(individualGroup)):
                #print (reactionList[k]+"\t\t"+individualGroup[position]+' '+individualGroupValues[position]) 
                XMLdict['XS'][count][libraryXML.attrib.get('lib_name')][isotopeXML.attrib.get('id')+isotopeXML.attrib.get('type')][reactionList[k]][individualGroup[position]] = individualGroupValues[position]
    #print XMLdict
    return XMLdict
  
  def prettify(self, elem):
    """
      Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
    
    
  def detectXML(self):
    """
      Detects if the XS.xml exists. 
      In: None
      Out: Boolean: True means the XS.xml exists, False means XS.xml does not exist 
    """
    
    top = Element('scaling_library')

    comment = Comment('Generated by rouxpn')
    top.append(comment)

    child = SubElement(top, 'child')
    child.text = 'This child contains text.'

    child_with_tail = SubElement(top, 'child_with_tail')
    child_with_tail.text = 'This child has regular text.'
    child_with_tail.tail = 'And "tail" text.'

    child_with_entity_ref = SubElement(top, 'child_with_entity_ref')
    child_with_entity_ref.text = 'This & that'
    
    file_obj = open('XS.xml', 'w')
    file_obj.write(self.prettify(top))
    #print self.prettify(top)
    
    
  def __init__(self, inputFiles, **pertDict):
    """
      Parse the PHISICS XS.xml data file   
      In: XS.xml
      Out: None 
    """
    self.pertDict = pertDict
    #print self.pertDict
    #print "\n\n\n"
    #print inputFiles
    booleanCreator = self.detectXML()
    for key, value in self.pertDict.iteritems(): 
      self.pertDict[key] = '%.3E' % Decimal(str(value)) #convert the values into scientific values   
    self.inputFiles = inputFiles
    self.tree = ET.parse(self.inputFiles)
    self.root = self.tree.getroot()
    self.listedDict = self.fileReconstruction(self.pertDict)
    self.printInput()

  def fileReconstruction(self, deconstructedDict):
    """
      Converts the formatted dictionary -> {'XS|FUEL1|U235|FISSION|1':1.30, 'XS|FUEL2|U238|ABS|2':4.69} 
      into a dictionary of dictionaries that has the format -> {'XS':{'FUEL1':{'U235':{'FISSION':{'1':1.30}}}}, 'FUEL2':{'U238':{'ABS':{'2':4.69}}}}
      In: Dictionary deconstructedDict
      Out: Dictionary of dictionaries reconstructedDict 
    """
    #print deconstructedDict
    reconstructedDict           = {}
    perturbedPhysicalParameters = []
    perturbedTabulationPoint    = []
    perturbedMaterials          = []
    perturbedReactions          = []
    perturbedGroups             = []
    perturbedIsotopes           = []
    
    pertDictSet = set(self.pertDict)
    deconstructedDictSet = set(deconstructedDict)
    #for variable in pertDictSet.intersection(deconstructedDictSet):
    for i in pertDictSet.intersection(deconstructedDictSet): 
      splittedKeywords = i.split('|')
      perturbedPhysicalParameters.append(splittedKeywords[0])
      perturbedTabulationPoint.append(splittedKeywords[1])
      perturbedMaterials.append(splittedKeywords[2])
      perturbedIsotopes.append(splittedKeywords[3])
      perturbedReactions.append(splittedKeywords[4])
      perturbedGroups.append(splittedKeywords[5])  
    
    #print perturbedReactions
    for i in xrange (0,len(perturbedPhysicalParameters)):
      reconstructedDict[perturbedPhysicalParameters[i]] = {}
      for j in xrange (0,len(perturbedTabulationPoint)):
        reconstructedDict[perturbedPhysicalParameters[i]][perturbedTabulationPoint[j]] = {} 
        for k in xrange (0,len(perturbedMaterials)):
          reconstructedDict[perturbedPhysicalParameters[i]][perturbedTabulationPoint[j]][perturbedMaterials[k]] = {}
          for l in xrange (0,len(perturbedIsotopes)):
            reconstructedDict[perturbedPhysicalParameters[i]][perturbedTabulationPoint[j]][perturbedMaterials[k]][perturbedIsotopes[l]] = {} 
            for m in xrange (0,len(perturbedReactions)):
              reconstructedDict[perturbedPhysicalParameters[i]][perturbedTabulationPoint[j]][perturbedMaterials[k]][perturbedIsotopes[l]][perturbedReactions[m]] = {}
              for n in xrange (0,len(perturbedGroups)):
                reconstructedDict[perturbedPhysicalParameters[i]][perturbedTabulationPoint[j]][perturbedMaterials[k]][perturbedIsotopes[l]][perturbedReactions[m]][perturbedGroups[n]] = {}
    #print reconstructedDict
    for typeKey, value in deconstructedDict.iteritems():
      if typeKey in pertDictSet:
        keyWords = typeKey.split('|')
        #print keyWords
        reconstructedDict[keyWords[0]][keyWords[1]][keyWords[2]][keyWords[3]][keyWords[4]][keyWords[5]] = value
    #print reconstructedDict
    return reconstructedDict
   
    
  def printInput(self):
    """
      Method to print out the new input
      @ In, outfile, string, optional, output file root
      @ Out, None
    """
    modifiedFile = 'modif.xml'     
    open(modifiedFile, 'w')
    XMLdict = {}
    genericXMLdict = {}
    newXMLdict = {}
    templatedNewXMLdict = {} 
    mapAttribIsotope = {}
    
    XMLdict = self.dictFormating_from_XML_to_perturbed()
    #print XMLdict
    genericXMLdict = self.dictFormating_from_perturbed_to_generic(XMLdict)
    #print genericXMLdict
    newXMLDict = self.replaceValues(genericXMLdict)
    #print newXMLDict
    templatedNewXMLdict = self.fileReconstruction(newXMLDict)
    #print templatedNewXMLdict 
    templatedNewXMLdict = self.listedDict
    #print templatedNewXMLdict
    count = 0
    for tabulationXML in self.root.getiterator('tabulation'):
      count = count + 1 
      for libraryXML in tabulationXML.getiterator('library'):
        for isotopeXML in libraryXML.getiterator('isotope'):
          reactionList = [j.tag for j in isotopeXML]
          #print reactionList
          for k in xrange(0,len(reactionList)):
            for groupXML in isotopeXML.getiterator(reactionList[k]):
              individualGroup = [x.strip() for x in groupXML.attrib.get('g').split(',')]
              individualGroupValues = [y.strip() for y in groupXML.text.split(',')]
              #print isotopeXML.attrib.get('id').upper()+isotopeXML.attrib.get('type').upper()
              #print (individualGroup+individualGroupValues)
              for position in xrange(0,len(individualGroup)):
                
                #print templatedNewXMLdict.get('XS').get(str(count).upper()).get(libraryXML.attrib.get('lib_name').upper()).get(isotopeXML.attrib.get('id').upper()+isotopeXML.attrib.get('type').upper()).get(reactionList[k].upper()).get(groupXML.attrib.get('g'))
                #print isotopeXML.attrib
                #print groupXML.text
                #print groupXML.text.split(',')[position]
                #print "\n\n"
                groupXML.text = templatedNewXMLdict.get('XS').get(str(count).upper()).get(libraryXML.attrib.get('lib_name').upper()).get(isotopeXML.attrib.get('id').upper()+isotopeXML.attrib.get('type').upper()).get(reactionList[k].upper()).get(groupXML.attrib.get('g'))
                #print groupXML.text
          self.tree.write(modifiedFile)
    copyfile('modif.xml', self.inputFiles)  
   

