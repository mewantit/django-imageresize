from __future__ import with_statement

import os
import subprocess
import tempfile

from contextlib import contextmanager

def resize(src, target, width, height):
    """ Resizes a source image to given dimensions and stores the resized image as target
    
        src: Full path to image to be resized.
        
        target: Full path where to store resized image. (Path does not need to exist before)
        
        width: Width of the resized image.
        
        height: Height of the resized image.
    
    """
    if not os.path.isfile(src):
        raise IOError("Source image not found: %s" % src)
    
    if not os.path.isfile(target):
        (target_path, _) = os.path.split(target)
        
        if not os.path.isdir(target_path):
            os.makedirs(target_path)
        
        with temp_file(target) as target: 
            _image_magick_resize(src, target, width, height)
 
@contextmanager
def temp_file(target):
    """ Wraps a filename with a temporary filename. If working with the temporary file is successful 
    the temporary file will be renamed to the target filename.  
    
    target: filename that the temporary file should be renamed to if no exceptions are raised   
    """
    temp = None
    try:
        temp = _create_tempfile_for_target(target)
        yield temp
        _replace_target_file_with_temp_file(temp, target)    
    finally:
        _remove_tempfile(temp)

 
def _image_magick_resize(src, target, width, height):
    subprocess.check_call(['convert', src, '-trim', '-resize', '%dx%d>' % (width, height),
                           '-size','%dx%d' % (width, height), 'xc:white', '+swap',
                           '-gravity', 'center', '-composite', target])

def _create_tempfile_for_target(target):
    (_, target_filename) = os.path.split(target)    
    target_fileending = target_filename.split(".")[-1]
    (_, temp_file) = tempfile.mkstemp(suffix="." + target_fileending)
    return temp_file

def _replace_target_file_with_temp_file(temp_file, target):    
    os.rename(temp_file, target)
    
def _remove_tempfile(temp_file):
    if temp_file and os.path.isfile(temp_file):
        os.remove(temp_file)
        