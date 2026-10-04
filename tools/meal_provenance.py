"""Lossless wire representation of repeated nutrient source records.

The full source objects remain available to every meal consumer. Sharing equal
objects reduces transferred bytes without dropping dates, uncertainty or sources.
"""
from copy import deepcopy
import json
import re


def pack(metadata):
    records = deepcopy(metadata)
    sources, lookup = [], {}
    for record in records.values():
        for nutrient, source in record.get('nutrientProvenance', {}).items():
            key = json.dumps(source, sort_keys=True, ensure_ascii=False)
            if key not in lookup:
                lookup[key] = len(sources)
                sources.append(source)
            record['nutrientProvenance'][nutrient] = lookup[key]
    # Repeated official URLs and inspection notes are interned too. Runtime
    # consumers receive the exact original strings, never opaque source IDs.
    fields=('source','checked','sourceDate','region','verificationStatus','notes','serving')
    texts, text_lookup=[],{}
    for record in records.values():
        for field in fields:
            value=record.get(field)
            if not isinstance(value,str):continue
            if value not in text_lookup:
                text_lookup[value]=len(texts);texts.append(value)
            record[field]=text_lookup[value]
    compact = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    return ('/* Source records; missing fat is not estimated from calories. */\n'
            '(function(){var records=' + compact(records) + ';var nutrientSources=' + compact(sources) + ';var sourceTexts='+compact(texts)+';'
            'Object.values(records).forEach(function(r){'+compact(fields)+'.forEach(function(k){if(typeof r[k]==="number")r[k]=sourceTexts[r[k]];});Object.keys(r.nutrientProvenance||{}).forEach(function(k){'
            'r.nutrientProvenance[k]=nutrientSources[r.nutrientProvenance[k]];});});'
            ' (window.GM_MEALS||[]).forEach(function(m){var r=records[m.chain+"||"+m.name];'
            'if(r)Object.assign(m,r);});})();\n')


def read(path):
    text = path.read_text(encoding='utf-8')
    records = json.loads(re.search(r'var records=(\{.*?\});', text)[1])
    match = re.search(r'var nutrientSources=(\[.*?\]);', text)
    if match:
        sources = json.loads(match[1])
        for record in records.values():
            for nutrient, index in record.get('nutrientProvenance', {}).items():
                record['nutrientProvenance'][nutrient] = deepcopy(sources[index])
    text_match=re.search(r'var sourceTexts=(\[.*?\]);',text)
    if text_match:
        texts=json.loads(text_match[1])
        for record in records.values():
            for field in ('source','checked','sourceDate','region','verificationStatus','notes','serving'):
                if isinstance(record.get(field),int):record[field]=texts[record[field]]
    return records
