import json


def mkPartitions(size, width):
    '''partitions size elements into width buckets.
    for example mkPartitions(2, 2) returns [[0, 2], [1, 1], [2, 0]]
    '''
    partitions = []
    if width == 1:
        return [[size]]

    for i in range(size+1):
        subparts = mkPartitions(size - i, width - 1)
        for p in subparts:
            partitions.append([i] + p)
    return partitions


def analyzeScenario(crops):
    '''analyze the scenario: find expected, pessimistic and optimistic'''

    if len(crops) == 0:
        # cannot analyze
        return ('', 0.0), ('', 0.0), ('', 0.0)

    farm = crops.first().scenario.farm

    fields = [f.acreage for f in farm.fields.all()]

    partitions = mkPartitions(len(fields), crops.count())
    best_mean = -1e10
    max_min = ((-1e10, 0.0, 0.0), None, 0.0)
    max_mean = ((0.0, -1e10, 0.0), None, 0.0)
    max_max = ((0.0, 0.0, -1e10), None, 0.0)

    # build price, yields, and cost arrays
    cropDict = {}
    crop_names = []

    for crop in crops.all():
        thisDict = {}
        cropdata = crop.data
        crop_name = cropdata.name
        crop_names.append(crop_name)
        farmcrop = crop.farmcrop
        if farmcrop.price_override != '':
            prices = json.loads(farmcrop.price_override)
        else:
            prices = json.loads(crop.prices())
        if farmcrop.yield_override != '':
            yields = json.loads(farmcrop.yield_override)
        else:
            yields = json.loads(crop.yields())
        thisDict['gross'] = [
            prices[0] * yields[0],
            prices[1] * yields[1],
            prices[2] * yields[2],
        ]
        thisDict['cost'] = cropdata.cost + farmcrop.cost_override +\
            crop.cost_override

        overs = []
        over_acres = 0
        for over in crop.price_overrides.all():
            median_yield = json.loads(cropdata.yield_stats)['median']
            acres = over.units*over.factor/median_yield
            over_acres += acres
            overs.append(dict(
                units=over.units,
                price=over.price,
                acres=acres))
        thisDict['overs'] = overs
        thisDict['over_acres'] = over_acres
        cropDict[crop_name] = thisDict

    for partition in partitions:
        totals = [0.0, 0.0, 0.0, ]

        valid = True
        expense = 0.0
        for i in range(len(partition)):
            dcrop = cropDict[crop_names[i]]
            pacres = partition[i] * fields[i]
            lo, hi = crops[i].limits()
            if pacres < lo or (hi > 0 and pacres > hi):
                # not a valid partition
                valid = False
                break
            if pacres < dcrop['over_acres']:
                # there are not enough acres in this partition to
                # fulfill the price overrides
                valid = False
                break
            expense += pacres * dcrop['cost']

            per_acre = dcrop['gross'][0] - dcrop['cost']
            totals[0] += pacres * per_acre
            per_acre = dcrop['gross'][1] - dcrop['cost']
            totals[1] += pacres * per_acre
            per_acre = dcrop['gross'][2] - dcrop['cost']
            totals[2] += pacres * per_acre

        if not valid or expense > farm.max_expense:
            continue

        if totals[0] > max_min[0][0]:
            max_min = (totals, partition, expense)
        this_mean = sum(totals)/3.0
        if this_mean > best_mean:
            best_mean = this_mean
            max_mean = (totals, partition, expense)
        if totals[2] > max_max[0][2]:
            max_max = (totals, partition, expense)

    if max_min[1] is None:
        # then we didn't find any solutions
        return None
    else:
        return (max_min, max_mean, max_max)
