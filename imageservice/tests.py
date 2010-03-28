from __future__ import with_statement
from nose.tools import raises

import os
import tempfile
import shutil
import unittest
from contextlib import contextmanager
from django.conf import settings
import stat
root = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
settings.configure(RESIZE_MAX_HEIGHT=2048,RESIZE_MAX_WIDTH=2048,
                   MEDIA_ROOT="",
                   MEDIA_CACHE_ROOT="",
                   TEST_MEDIA_ROOT=os.path.join(root, 'test_media'),
                   DATABASE_ENGINE=None,
                   INSTALLED_APP= ("imageservice"),
                   DEBUG=True,
                   ROOT_URLCONF='imageservice.urls',
                   TEMPLATE_DIRS = (os.path.join(root, 'test_settings'),)
                   )
from imageservice import views, imagemagick
from imageservice.template_repository import TemplateRepository
from imageservice.templatetags.image_service import resize
from django.http import Http404, HttpResponse
from django.test.client import Client
class ImageMagickResizeTest(unittest.TestCase):
    
    def setUp(self):
        
        self.source = settings.TEST_MEDIA_ROOT + '/test.png'
        self.tmp_dir = tempfile.mkdtemp()
        self.target = self.tmp_dir + '/target.png'
        self.old_temp_file = imagemagick.temp_file
        
        @contextmanager
        def noaction_temp_file(target): 
            yield target

        imagemagick.temp_file = noaction_temp_file

        
    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        imagemagick.temp_file = self.old_temp_file
    
    def test_should_work_with_arbitary_command(self):
        imagemagick.execute('-matte  -fill  none  -draw  matte 0,0 floodfill', self.source, self.target)
    
    def test_should_create_a_new_resized_image_on_disk(self):
        imagemagick.resize(self.source, self.target, 320, 200)
        self.assertTrue(os.path.isfile(self.target))
    
    def test_should_create_target_path_if_not_exists(self):
        target = self.tmp_dir + "/newdir/target.png"
        imagemagick.resize(self.source, target, 320, 200)
        self.assertTrue(os.path.isfile(target))
    
    def test_should_not_resize_file_if_target_already_exists(self):
        imagemagick.resize(self.source, self.target, 320, 200)
        time = os.path.getmtime(self.target)
        imagemagick.resize(self.source, self.target, 320, 200)
        self.assertEquals(time, os.path.getmtime(self.target))
    
    @raises(IOError)    
    def test_should_raise_exception_if_source_file_is_missing(self):
        imagemagick.resize("missing_file.png", self.target, 320, 200)
        
    @raises(Exception)
    def test_should_raise_exception_if_imagemagick_process_returns_error_code(self):
        imagemagick._image_magick_resize("-fail-", self.target, 320, 200)
        
    def test_should_work_on_temporary_file(self):
        temp_file = self.tmp_dir + "/tempfile.png"
        @contextmanager
        def mock_temp_file(target): 
            yield temp_file
            open(target, 'a').close() # create dummy target

        imagemagick.temp_file = mock_temp_file
        imagemagick.resize(self.source, self.target, 320, 200)
        self.assertTrue(os.path.isfile(temp_file))
        
    def test_should_keep_permissisions_of_source_file(self):
        original_mode = os.stat(self.source).st_mode
        try:
            os.chmod(self.source, original_mode|stat.S_IXUSR)
            imagemagick.resize(self.source, self.target, 320, 200)
            self.assertEquals(os.stat(self.source).st_mode, os.stat(self.target).st_mode)    
        finally:
            os.chmod(self.source, original_mode)
    
    def test_should_be_case_sensitive(self):
        source = settings.TEST_MEDIA_ROOT + "/Case.PNG"
        target = self.tmp_dir + "/Case.PNG"
        imagemagick.resize(source, target, 320, 200)
        self.assertTrue(os.path.isfile(target))
        
    def test_should_match_both_upper_and_lower_cases_when_no_extension_is_provided(self):
        source = settings.TEST_MEDIA_ROOT + "/Case"
        target = self.tmp_dir + "/Case.PNG"
        imagemagick.resize(source, target, 320, 200)
        self.assertTrue(os.path.isfile(target))
  
class TemporaryFileTest(unittest.TestCase):
   
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.target = self.tmp_dir + "/target.png"
        
        self.temp_file = self.tmp_dir + "/tempfile.png"
        self.old_mkstemp = tempfile.mkstemp
        tempfile.mkstemp = lambda **kwargs: (None, self.temp_file)  
         
        
    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        tempfile.mkstemp = self.old_mkstemp
       
    def test_should_work_on_temp_file(self): 
        with imagemagick.temp_file(self.target) as result:
            open(result, 'w').write("hello")
            self.assertEquals(self.temp_file, result)
            self.assertTrue(os.path.isfile(self.temp_file))
    
    def test_should_replace_target_with_temp_file(self): 
        with imagemagick.temp_file(self.target) as result:
            open(result, 'w').write("hello")
        
        self.assertEquals("hello", open(self.target, 'r').read())
        
    def test_should_overwrite_target_file_if_already_exists(self):
        open(self.target,'w').write("good bye")
        
        with imagemagick.temp_file(self.target) as result:
            open(result, 'w').write("hello")
        
        self.assertEquals("hello", open(self.target, 'r').read())
        
    def test_should_remove_tempfile_after_done(self):
        with imagemagick.temp_file(self.target) as result:
            open(result, 'w').write("hello")
                        
        self.assertFalse(os.path.isfile(self.temp_file))
        
    def test_should_remove_tempfile_if_failing(self):
        
        try:
            with imagemagick.temp_file(self.target) as result:
                open(result, 'w').write("hello")
                raise Exception
                
        except Exception:
            self.assertFalse(os.path.isfile(self.temp_file))
        
    def test_should_keep_fileending_of_target_file(self):
        tempfile.mkstemp = self.old_mkstemp
        with imagemagick.temp_file(self.target) as result:
            self.assertEquals(self.target.split('.')[-1], result.split('.')[-1])
            open(result, 'w').write("hello")

class ResizeImageViewTest(unittest.TestCase):
    
    def setUp(self):
        self.file_name_without_extension = "/dir1/dir2/hello"
        self.file_extension = ".png"
        self.width = "100"
        self.height = "200"
    
        def mock_resize(source_file, target_file, width, height):
            self.result = {'source_file': source_file,
                    'target_file': target_file,
                    'width': width,
                    'height': height,
                    }
       
        def mock_render_image_to_response(file_name):
            self.result['rendered_to_http_response'] = True
            return self.result
            
        self.old_render_image_to_response = views.render_image_to_response
        self.old_resize = imagemagick.resize
        views.render_image_to_response = mock_render_image_to_response
        imagemagick.resize = mock_resize
        
        self.old_MAX_HEIGHT = settings.RESIZE_MAX_HEIGHT
        self.old_MAX_WIDTH = settings.RESIZE_MAX_WIDTH
       
        settings.RESIZE_MAX_HEIGHT = 1000
        settings.RESIZE_MAX_WIDTH = 1000
       
    def tearDown(self):
        views.render_image_to_response = self.old_render_image_to_response
        imagemagick.resize = self.old_resize
        settings.RESIZE_MAX_HEIGHT = self.old_MAX_HEIGHT
        settings.RESIZE_MAX_WIDTH = self.old_MAX_WIDTH
        
    @raises(Http404)
    def test_should_limit_maximum_height(self):
        self.height = settings.RESIZE_MAX_HEIGHT + 1;
        views.resize_image(None, self.file_name_without_extension, self.width, self.height, self.file_extension)
    
    @raises(Http404)
    def test_should_limit_maximum_width(self):
        self.width = settings.RESIZE_MAX_WIDTH + 1;
        views.resize_image(None, self.file_name_without_extension, self.width, self.height, self.file_extension)   
    
    @raises(Http404)
    def test_should_give_404_if_resize_fails(self):
        def mock_resize(source_file, target_file, width, height):
            raise Exception
            
        imagemagick.resize = mock_resize
        
        views.resize_image(None, self.file_name_without_extension, self.width, self.height, self.file_extension)
        
    
    def test_should_fetch_source_image_from_media_root(self):
        result = views.resize_image(None, self.file_name_without_extension, self.width, self.height, self.file_extension)
        self.assertTrue(result['target_file'].startswith(settings.MEDIA_ROOT))
    
    def test_should_store_resized_image_under_cached_media_root(self):
        result = views.resize_image(None, self.file_name_without_extension, self.width, self.height, self.file_extension)
        self.assertTrue(result['target_file'].startswith(settings.MEDIA_CACHE_ROOT))
   
    def test_the_paths_of_source_and_resized_image_should_be_the_same_except_for_their_root_path(self):
        self.old_media_cache_root = settings.MEDIA_CACHE_ROOT
        
        try:
            settings.MEDIA_CACHE_ROOT = settings.MEDIA_ROOT 
            result = views.resize_image(None, self.file_name_without_extension, self.width, self.height, self.file_extension)
            (source_path, _) = os.path.split(result['source_file'])
            (target_path, _) = os.path.split(result['target_file'])
        
            self.assertEquals(source_path, target_path)
        
        finally:
            settings.MEDIA_CACHE_ROOT = self.old_media_cache_root


    def test_file_names_of_source_and_resized_image_should_be_the_same_except_for_the_size(self):
        result = views.resize_image(None, self.file_name_without_extension, self.width, self.height, self.file_extension)
        (_, source_file) = os.path.split(result['source_file'])
        (_, target_file) = os.path.split(result['target_file'])
    
        self.assertEquals(source_file.split('.')[0], target_file.split('.')[0])

    def test_should_append_image_size_to_resized_image(self):
        result = views.resize_image(None, self.file_name_without_extension, self.width, self.height, self.file_extension)
        (_, file_name) = os.path.split(result['target_file'])
        self.assertEquals("hello.100x200.png", file_name)
 
    def test_should_support_images_without_file_extension(self):
        result = views.resize_image(None, self.file_name_without_extension, self.width, self.height, "")
        (_, file_name) = os.path.split(result['target_file'])
        self.assertEquals("hello.100x200", file_name)
   
    def test_should_render_resized_image_to_http_response(self):
        result = views.resize_image(None, self.file_name_without_extension, self.width, self.height, self.file_extension)
        self.assertTrue(result['rendered_to_http_response'])

    def test_should_be_case_sensitive(self):
        result = views.resize_image(None, "Case", self.width, self.height, ".PNG")
        (_, source_file_name) = os.path.split(result['source_file'])
        (_, target_file_name) = os.path.split(result['target_file'])
        
        self.assertEquals("Case.PNG", source_file_name)
        self.assertEquals("Case.100x200.PNG", target_file_name)
        
   

class TemplatesRepositoryTest(unittest.TestCase):
    
    def setUp(self):
        self.templateRepo = TemplateRepository()
        
    def test_get_template_returns_expected_value(self):
        self.assertEquals('arg1  arg2', self.templateRepo.getTemplate('TEST'))
            
class MockFile(object):
    def __init__(self, file_name):
        self.file_name = file_name
        
    def read(self):
        return ["mocked_binary:", self.file_name]

class RenderImageToResponseTest(unittest.TestCase):
    
    def setUp(self):
        self.old_open = views._open
        views._open = lambda f: MockFile(f)
        
    def tearDown(self):
        views._open = self.old_open
    
    def test_should_inlude_file_data_in_response_content(self):
        result = views.render_image_to_response("foo.jpg")
        self.assertEquals("mocked_binary:foo.jpg", result.content)

    def test_should_have_image_as_content_type(self):
        result = views.render_image_to_response("foo.jpg")
        self.assertEquals("image/jpg", result['content-type'])


class ResizeUrlTest(unittest.TestCase):
    
    def setUp(self):
        ResizeUrlTest.file_name_without_extension = "test"
        ResizeUrlTest.width = u'100'
        ResizeUrlTest.height = u'200'
        ResizeUrlTest.file_extension = ".jpg"

        self.old_resize_image = views.resize_image
        def mock_resize_image(request, file_name_without_extension, width, height, file_extension):
            self.assertEquals(ResizeUrlTest.file_name_without_extension, file_name_without_extension)
            self.assertEquals(ResizeUrlTest.width, width)
            self.assertEquals(ResizeUrlTest.height, height) 
            self.assertEquals(ResizeUrlTest.file_extension, file_extension)
            return HttpResponse()

        views.resize_image = mock_resize_image
        
        self.client = Client();
        
    def tearDown(self):  
        views.resize_image = self.old_resize_image 
    
    def test_should_support_images_with_extensions(self):
        ResizeUrlTest.file_extension = ".jpg"
        result = self.client.get("/test.100x200.jpg")
        self.assertEquals(200, result.status_code)
        
    def test_should_support_images_without_extensions(self):
    
        ResizeUrlTest.file_extension = ""
        result = self.client.get("/test.100x200")
        
        self.assertEquals(200, result.status_code)
    
    def test_should_not_support_images_with_special_characters_in_extension(self):
        ResizeUrlTest.file_extension = ""
        result = self.client.get("/test.100x200./")
        self.assertEquals(404, result.status_code)
            
    def test_should_not_support_images_ending_with_dot(self):
        ResizeUrlTest.file_extension = ""
        result = self.client.get("/test.100x200.")

        self.assertEquals(404, result.status_code)
   
    def test_should_be_case_sensitive(self):
        ResizeUrlTest.file_name_without_extension = "UpperCase"
        ResizeUrlTest.file_extension = ".PNG"
        result = self.client.get("/UpperCase.100x200.PNG")
        self.assertEquals(200, result.status_code)
        
class ResizeFilterTest(unittest.TestCase):
    
    def test_should_rewrite_url_with_given_size(self):
        result = resize("http://www.test.com/file.jpg", "100x300")
        self.assertEquals("http://www.test.com/file.100x300.jpg", result)
    
    def test_should_work_without_file_ending(self):
        result = resize("http://www.test.com/file", "100x300")
        self.assertEquals("http://www.test.com/file.100x300", result)

    def test_should_work_with_absolute_paths(self):
        result = resize("/file.jpg", "100x300")
        self.assertEquals("/file.100x300.jpg", result)

    def test_should_work_with_absolute_paths_without_fileendings(self):
        result = resize("/file", "100x300")
        self.assertEquals("/file.100x300", result)

    def test_should_work_with_filename_alone(self):
        result = resize("file.jpg", "100x300")
        self.assertEquals("file.100x300.jpg", result)

    def test_should_work_with_filename_alone_without_file_ending(self):
        result = resize("file", "100x300")
        self.assertEquals("file.100x300", result)
