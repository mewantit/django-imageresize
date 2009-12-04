from django.conf import settings
import fnmatch
import os

class TemplateRepository(object):
    
    def __init__(self):
        self.templates = self._readTemplates()
    
    def getTemplate(self, templateName):
        return self.templates[templateName]
    
    def _readTemplates(self):
        file = self._findTemplateFile()
        
        templates = {}
        for line in open(file, "r"):
            keyValue = line.split("=")
            templates[keyValue[0].strip()] = keyValue[1].strip()
        
        return templates
    
    def _findTemplateFile(self):
        dirs = settings.TEMPLATE_DIRS
        for dir in dirs:
            for file in os.listdir(dir):
                if fnmatch.fnmatch(file, 'imagemagick.templates'):
                    return dir + '/' + file
        raise IOError('Templates file (imagemagick.templates) not found in Django templates dirs. Following dirs where searched: ' + ", ".join(dirs))