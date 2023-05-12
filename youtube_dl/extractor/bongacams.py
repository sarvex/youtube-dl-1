from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..compat import compat_str
from ..utils import (
    int_or_none,
    try_get,
    urlencode_postdata,
)


class BongaCamsIE(InfoExtractor):
    _VALID_URL = r'https?://(?P<host>(?:[^/]+\.)?bongacams\d*\.com)/(?P<id>[^/?&#]+)'
    _TESTS = [{
        'url': 'https://de.bongacams.com/azumi-8',
        'only_matching': True,
    }, {
        'url': 'https://cn.bongacams.com/azumi-8',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        host = mobj['host']
        channel_id = mobj['id']

        amf = self._download_json(
            f'https://{host}/tools/amf.php',
            channel_id,
            data=urlencode_postdata(
                (
                    ('method', 'getRoomData'),
                    ('args[]', channel_id),
                    ('args[]', 'false'),
                )
            ),
            headers={'X-Requested-With': 'XMLHttpRequest'},
        )

        server_url = amf['localData']['videoServerUrl']

        uploader_id = try_get(
            amf, lambda x: x['performerData']['username'], compat_str) or channel_id
        uploader = try_get(
            amf, lambda x: x['performerData']['displayName'], compat_str)
        like_count = int_or_none(try_get(
            amf, lambda x: x['performerData']['loversCount']))

        formats = self._extract_m3u8_formats(
            f'{server_url}/hls/stream_{uploader_id}/playlist.m3u8',
            channel_id,
            'mp4',
            m3u8_id='hls',
            live=True,
        )
        self._sort_formats(formats)

        return {
            'id': channel_id,
            'title': self._live_title(uploader or uploader_id),
            'uploader': uploader,
            'uploader_id': uploader_id,
            'like_count': like_count,
            'age_limit': 18,
            'is_live': True,
            'formats': formats,
        }
