from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


# Suitcase subpackages must follow strict naming and interface conventions. The
# public API should include some subset of the following. Any functions not
# implemented should be omitted, rather than included and made to raise
# NotImplementError, so that a client importing this library can immediately
# know which portions of the suitcase API it supports without calling any
# functions.
#
from collections import defaultdict
import json


def export(gen, filepath):
    """
    Export a stream of documents to CSV files.

    Creates {filepath}_meta.json and then {filepath}_{stream_name}.csv
    for every Event stream.

    The structure of the json is:

    {'start': {...},
     'descriptors':
         {'<stream_name>': [{...}, {...}, ...],
          ...},
     'stop': {...}}
    """
    meta = {}  # to be exported as JSON at the end
    meta['descriptors'] = defaultdict(list)  # map stream_name to descriptors
    files = {}  # map descriptor uid to file handle of CSV file
    try:
        for name, doc in gen:
            if name == 'start':
                if 'start' in meta:
                    raise RuntimeError("This exporter expects documents from one "
                                    "run only.")
                meta['start'] = doc
            elif name == 'stop':
                meta['stop'] = doc
            elif name == 'descriptor':
                stream_name = doc.get('name')
                meta['descriptors'][stream_name].append(doc)
                filepath = f"{filepath}_{stream_name}_{doc['uid'][:8]}.csv"
                files[doc['uid']] = open(filepath, 'w')
            elif name == 'event':
                row = ', '.join(map(str, (doc['time'], *doc['data'].values())))
                f = files[doc['descriptor']]
                f.write(row)
    finally:
        for f in files.values():
            f.close()
    with open(f"{filepath}_meta.json", 'w') as f:
        json.dump(meta, f)
#
# def ingest(...):
#     ...
#
#
# def reflect(...):
#     ...
#
#
# handlers = []