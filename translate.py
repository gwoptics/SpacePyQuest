class Translator:

   def __init__(self, detector, map={}):
      # No f, so as not to confuse with frequency
      self.alphabet = 'abcdeghijklmnopqrstuvwxyz'
      self.detector = detector
      self.mapping = map
      if len(self.mapping) == 0:
         print('\nMap:\n')
         for i, key in enumerate(self.detector.parameters):
            self.mapping[key] = ' ' + self.alphabet[i] + ' '
            print(self.mapping[key] + '\t\t:\t\t' + self.detector.names[key])
         print('''
\nPlease ensure thet each symbol is preceded and followed by a space.
\nSet up a dictionary where the key is the name of your noise class,
all one word, and the value is the function describing its noise curve,
using the key printed above.
				''')

   def translate(self, string):
      # Invert the mapping
      self.inversemapping = {v: k for k, v in self.mapping.items()}
      for value in self.inversemapping:
         string = string.replace(value, \
               'detector.parameters[\'' + \
                self.inversemapping[value] + \
                '\']')
      return string

   def generateNoiseScript(self, noiseDictionary):
      # Takes a dictionary that defines a new noise function like
      # {NoiseKey : 'FunctionString'}

      # Create the new noise file
      newNoiseFile = open('newnoises.py', 'w')
      newNoiseFile.write('# User-defined noises\n\n')
      self.classnames = []
      for className in noiseDictionary:
         self.classnames.append(className)
         function = self.translate(noiseDictionary[className])
         newNoiseFile.write("""
class {clsnm}:

	@staticmethod
	def Get{clsnm}(f, detector):
		return {fnct}

	@classmethod
	def ComputePoint(cls, f, detector):
		return cls.Get{clsnm}(f, detector)

			""".format(clsnm=className, fnct=function))

      newNoiseFile.close()

   def getNewNoiseClasses(self):
      import newnoises
      newClasses = {}
      for key in newnoises.__dict__:
         for clsnm in self.classnames:
            if clsnm in key:
               newClasses[clsnm] = newnoises.__dict__[key]

      return newClasses
