import os
import codecs
from setuptools import setup

readme_path = os.path.join(os.path.dirname(__file__), 'README.md')

with codecs.open(readme_path, mode='r', encoding='utf-8') as f:
    description = f.read()

setup(
    name='parse-torrent-title',
    version=__import__('PTN').__version__,
    author=__import__('PTN').__author__,
    author_email=__import__('PTN').__email__,
    license=__import__('PTN').__license__,
    url='https://github.com/platelminto/parse-torrent-title',
    description='Extract media information from torrent-like filename',
    long_description=description,
    long_description_content_type='text/markdown',
    packages=['PTN'],
    keywords=('parse parser torrent torrents name names proper rename '
              'movie movies tv show shows series extract find source '
              'group codec audio resolution title season episode year '
              'information filename filenames file files meaningful'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Topic :: Text Processing'
    ]
)
