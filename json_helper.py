import json

def get_normalizers(json_file):
    with open(json_file, "r") as read_file:
        data = json.load(read_file)
    result = {}
    for i in data['featureList']:
        if i['normalization'] == 'Z_SCORE' and i['isSelected'] == 'true':
            entry = {}
            entry['mean'] = i['normalizer']['data']['mean']
            entry['stdev'] = i['normalizer']['data']['stdev']
            entry['div'] = i['normalizer']['data']['div']
            result[i['name']] = entry
    return result

get_normalizers('data/2020 1 hour customers741,616,597,748,760,79,493,550,641.md.json')