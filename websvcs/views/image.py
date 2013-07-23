import os
import urllib
import urlparse
import uuid
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404
import requests
from core.util import url2path, encode_uri_component, print_stack_trace
from websvcs.models import ShortenedURL, ImageStore
import websvcs.img.util as img_util

IMAGE_ANONYMOUS_USER = 'c1948057b92a427894cd0868af3397'

def _get_image(user, image_url, specific_height=-1, specific_width=-1):
    """
        Returns the image at the image_url of the specific height and width
        if image is not locally buffers, then it downloads the original image at the url
        if specific height and width are set, it also creates a resized version of the image
    """
    def _download_image_to_local(src_image_url, src_image_pointer, height, width):
        prefix,ext = os.path.splitext(urlparse.urlparse(src_image_url).path)
        prefix = prefix.replace('/', '').replace('\\', '')
        prefix = url2path(prefix)

        filename = '%s_%s%s' % (uuid.uuid4().hex, uuid.uuid4().hex, ext)
        local_copy = os.path.join(settings.IMAGE_LOCAL_COPY_DIR, filename)
        local_url = os.path.join(settings.IMAGE_LOCAL_COPY_DIR_NO_PREFIX, filename)
        file_saved_path = local_copy

        if height == -1:
            #ensure exists
            assert src_image_pointer.status_code == 200

            #ensure is image!
            content_type = src_image_pointer.headers['content-type'].lower()

            if content_type[:5] != 'image':
                #cloudfront servers typically hosting images as octet-streams
                #we need to handle that
                assert 'application/octet-stream' in content_type
                #also in these cases we don't allow files greater than 700KB -> 716800 = 700*1024
                assert int('30611') < 716800

            if src_image_pointer.status_code == 200:
                #download remote file
                file_saved_path = local_copy
                local_copy = open(local_copy, 'wb')
                local_copy.write(src_image_pointer.content)
                local_copy.close()
            else:
                raise Http404()
        else:
            img_util.resize(src_image_pointer, (specific_width, specific_height), True, local_copy)

#        s3_url = s3.upload(file_saved_path)

        #store reference in imagestore
#        img = ImageStore(remote_url=image_url, local_url=s3_url, source_user=user, height=height, width=width)
        img = ImageStore(remote_url=image_url, local_url="/%s" % local_url, source_user=user, height=height, width=width)
        img.save()
        return img

    def _download_temp_image(src_image_url, src_image_pointer, height, width):
        prefix,ext = os.path.splitext(urlparse.urlparse(src_image_url).path)
        prefix = prefix.replace('/', '').replace('\\', '')
        prefix = url2path(prefix)

        filename = '%s_%s%s' % (uuid.uuid4().hex, uuid.uuid4().hex, ext)
        local_copy = os.path.join(settings.IMAGE_LOCAL_COPY_DIR, filename)
        local_url = os.path.join(settings.IMAGE_LOCAL_COPY_DIR_NO_PREFIX, filename)

        if height == -1:
            #ensure exists
            assert src_image_pointer.status_code == 200

            #ensure is image!
            content_type = src_image_pointer.headers['content-type'].lower()

            if content_type[:5] != 'image':
                #cloudfront servers typically hosting images as octet-streams
                #we need to handle that
                assert 'application/octet-stream' in content_type
                #also in these cases we don't allow files greater than 700KB -> 716800 = 700*1024
                assert int('30611') < 716800

            if src_image_pointer.status_code == 200:
                #download remote file
                local_copy = open(local_copy, 'wb')
                local_copy.write(src_image_pointer.content)
                local_copy.close()
            else:
                raise Http404()

        return local_url

    if user.is_anonymous() or not(user.is_authenticated()):
        try:
            user = User.objects.get(username=IMAGE_ANONYMOUS_USER)
        except:
            print_stack_trace()
            user = User.objects.create_user(username=IMAGE_ANONYMOUS_USER, email='beforebeta+anonymousfysavings@gmail.com', password=IMAGE_ANONYMOUS_USER)

    image_url = urllib.unquote_plus(image_url)

    original_image = None

    #check if image already exists
    image_url_to_check = image_url
    if ShortenedURL.objects.should_shorten_url(image_url):
        image_url_to_check = ShortenedURL.objects.shorten_url(image_url).shortened_url

    for image in ImageStore.objects.filter(remote_url = image_url_to_check):
        if image.height == specific_height and image.width == specific_width:
            #found the   image with the exact dimensions
            return image
        if image.height == image.width == -1:
            #found the original image
            original_image = image

    if not original_image:
        #original image not available
        #download original image
        original_image = _download_image_to_local(image_url, requests.get(image_url), -1, -1)
    else:
        original_image.local_url = _download_temp_image(image_url, requests.get(image_url), -1, -1)

    if specific_height == specific_width == -1:
#        os.remove(os.path.join(settings.IMAGE_LOCAL_COPY_DIR, original_image.local_url[1:].split('/')[-1]))
        return original_image
    else:
        #required image is not available
        #resize original image to required image
        resized_image = _download_image_to_local(image_url, os.path.join(settings.IMAGE_LOCAL_COPY_DIR, original_image.local_url[1:].split('/')[-1]), specific_height, specific_width)
#        os.remove(os.path.join(settings.IMAGE_LOCAL_COPY_DIR, resized_image.local_url[1:].split('/')[-1]))
#        os.remove(os.path.join(settings.IMAGE_LOCAL_COPY_DIR, original_image.local_url[1:].split('/')[-1]))
        return resized_image

def image(request, image_url):
    """
    Basic Functionality: An image_url will be provided. This is the url of the remote image being requested.
    This service will check if a local copy of that image exists, if it does (in the static/img/local folder
    then it will redirect the request to the local folder.
    If the local copy does not exist, it will download the remote image and store it in the local folder. Then
    it will redirect to the local image.
    """
    try:
        if image_url[:6] == 'http:/' and not (image_url[6] ==  '/'):
            image_url = 'http://' + image_url[6:]
    except:
        pass
    try:
        if image_url[:7] == 'https:/' and not (image_url[7] ==  '/'):
            image_url = 'https://' + image_url[7:]
    except:
        pass
    try:
        if image_url[-1] == "/":
            image_url = image_url[:-1]
    except:
        pass
    return HttpResponseRedirect(_get_image(request.user, image_url).local_url)

def image_resize(request, image_url, height, width):
    """
    This takes an image which can be arbitrarily large and scales it down to the specified height and width
    """
    try:
        if image_url[:6] == 'http:/' and not (image_url[6] ==  '/'):
            image_url = 'http://' + image_url[6:]
    except:
        pass
    try:
        if image_url[:7] == 'https:/' and not (image_url[7] ==  '/'):
            image_url = 'https://' + image_url[7:]
    except:
        pass
    try:
        if image_url[-1] == "/":
            image_url = image_url[:-1]
    except:
        pass
    return HttpResponseRedirect(_get_image(request.user, image_url, int(height), int(width)).local_url)

