# -*- coding: utf-8 -*-
import json
import codecs

with codecs.open('debug_live_config.json', 'r', 'utf-8') as f:
    config = json.load(f)

with codecs.open('out_keys.txt', 'w', 'utf-8') as out:
    for k, v in config.get('companies', {}).items():
        out.write(k + ': ' + str(list(v.keys())) + '\n')
