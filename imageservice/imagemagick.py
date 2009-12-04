from __future__ import with_statement

import os
import subprocess
import tempfile
import shutil

from contextlib import contextmanager

def resize(src, target, width, height):
    """ Resizes a source image to given dimensions and stores the resized image as target
    
        src: Full path to image to be resized.
        
        target: Full path where to store resized image. (Path does not need to exist before)
        
        width: Width of the resized image.
        
        height: Height of the resized image.
    
    """
    command = '-trim  -resize  %dx%d>  -size  %dx%d  xc:white  +swap  -gravity  center  -composite' % (width, height, width, height)
    
    execute(command, src, target);
    
def execute(command, src, target):
    if os.path.isfile(target):
        return
    _findAndVerifySource(src)
    _prepareTargetFolder(target)        
    _callImageMagick(command, src, target);
    
def _findAndVerifySource(src):
    if (_hasExtension(src)):
        if not os.path.isfile(src):
            raise IOError("Source image not found: %s." % src)
        return src
    else:
        return _guessAndAppendExtension(src);
        
    
def _hasExtension(file):
    return '.' in file

exts = ('.png', '.jpg', '.jpeg', '.gif')
def _guessAndAppendExtension(srcWithoutExtension):
    for ext in exts:
        file = srcWithoutExtension + ext
        if (os.path.isfile(file)):
            return file
        
    raise IOError("Source image not found: %s. Tried with following extensions: %s" %(srcWithoutExtension,", ".join(exts)) ) 

def _prepareTargetFolder(target):
    (target_path, _) = os.path.split(target)
    
    if not os.path.isdir(target_path):
        os.makedirs(target_path)
        
def _callImageMagick(command, src, target):
    with temp_file(target) as tmp_target: 
        args = ['convert', src] + command.split('  ')
        args.append(tmp_target)
        subprocess.check_call(args)

    shutil.copymode(src, target)
    
    
 
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

def _create_tempfile_for_target(target):
    (_, target_filename) = os.path.split(target)    
    target_fileending = target_filename.split(".")[-1]
    (_, temp_file) = tempfile.mkstemp(suffix="." + target_fileending)
    return temp_file

def _replace_target_file_with_temp_file(temp_file, target):    
    shutil.move(temp_file, target)
    
def _remove_tempfile(temp_file):
    if temp_file and os.path.isfile(temp_file):
        os.remove(temp_file)
        
