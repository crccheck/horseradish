"""
Load a test instance with some photos from Flickr.

Warning: Photos may be NSFW.
"""
from __future__ import unicode_literals

import requests
import json

from photolib.models import Photo
from django.core.files.base import ContentFile


# try and be a good netizen
user_agent = 'Horseradish Bootstrapper/0.0 https://github.com/crccheck/horseradish'


if __name__ == '__main__':
    import django
    django.setup()
    url = 'https://api.flickr.com/services/feeds/photos_public.gne?format=json&nojsoncallback=1'
    response = requests.get(url, headers={
        'User-Agent': user_agent,
    })
    # So Flickr's "JSON" api does not return json
    # https://www.flickr.com/groups/api/discuss/72157622950514923
    text = response.text.replace("\\\'", "\'")
    data = json.loads(text)
    for idx, item in enumerate(data['items'], start=1):
        # alt = item['title']
        photo_data = {
            'filename': 'flickr-demo-{}.jpg'.format(idx),
            'caption': item['title'],
            'notes': 'Raw JSON data:\n' + json.dumps(item, indent=2),
            'credits': item['author'],
            'source': 'Flickr',
            'source_url': item['link'],
        }
        img_small = item['media']['m']
        # Flickr sizes: small=m, large=b, original=o
        img_desired = img_small.replace('_m', '_b')
        img_response = requests.get(img_desired, headers={
            'User-Agent': user_agent,
        })
        assert img_response.ok
        photo = Photo.objects.create(**photo_data)
        photo.image.save(photo_data['filename'], ContentFile(img_response.content))
        if item['tags']:
            photo.photo_tags.add(*item['tags'].split(' '))
