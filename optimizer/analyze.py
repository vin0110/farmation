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


def percentile(lo, peak, hi, perc):
    # determine the percentile
    hgt = 100. / (hi - lo)  # using area of 50 units
    al = (peak - lo) * hgt  # area of triangle below peak

    if perc <= 0:
        return lo
    if perc >= 100:
        return hi

    if perc <= al:
        # select point on rising line to peak
        return lo + ((perc/al) * (peak - lo)**2)**0.5
    else:
        return hi - ((100. - perc)/(100. - al) * (hi - peak)**2)**0.5


def analyzeScenario(crops):
    '''analyze the scenario: find expected, pessimistic and optimistic'''

    def safety_acres(yields, safety):
        '''return acres to plant'''
        # saftey factor table of price orders
        FACTOR_TABLE = {
            'Very high': 10.,
            'High': 25.,
            'Medium': 50.,
            'Low': 75.,
            'Very low': 90.,
        }

        try:
            factor = FACTOR_TABLE[safety]
        except KeyError:
            factor = 50
        lo, peak, hi = yields
        return percentile(lo, peak, hi, factor)

    if len(crops) == 0:
        # cannot analyze
        return []

    farm = crops.first().scenario.farm

    fields = [f.acreage for f in farm.fields.all()]

    partitions = mkPartitions(len(fields), crops.count())

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
        thisDict['yields'] = yields
        thisDict['gross'] = [
            prices[0] * yields[0],
            prices[1] * yields[1],
            prices[2] * yields[2],
        ]
        thisDict['cost'] = crop.cost()

        orders = []
        order_acres = 0
        for order in crop.price_orders.all():
            factor = safety_acres(thisDict['yields'], order.safety)
            acres = order.units/factor
            value = order.price * order.units
            order_acres += acres
            orders.append(dict(
                units=order.units,
                price=order.price,
                value=value, ))
        thisDict['orders'] = orders
        thisDict['order_acres'] = order_acres
        cropDict[crop_name] = thisDict

    max_expense = farm.max_expense if farm.max_expense > 0 else None
    results = []
    for partition in partitions:
        totals = [0.0, 0.0, 0.0, ]

        valid = False
        expense = 0.0
        for i in range(len(partition)):
            dcrop = cropDict[crop_names[i]]
            pacres = partition[i] * fields[i]
            lo, hi = crops[i].limits()
            if pacres < lo or (hi > 0 and pacres > hi):
                # not a valid partition
                break
            if pacres < dcrop['order_acres']:
                # there are not enough acres in this partition to
                # fulfill the price overrides
                break

            expense += pacres * dcrop['cost']

            pacres = [pacres, pacres, pacres, ]

            for order in dcrop['orders']:
                # for each price order
                # 1) remove acres needed for the order
                # 2) add value of order to totals
                value = order['value']
                for i in range(3):
                    # round acres up (+1)
                    acres = int(order['units']/dcrop['yields'][i] + 1)
                    pacres[i] -= acres
                    totals[i] += value - acres * dcrop['cost']

            per_acre = dcrop['gross'][0] - dcrop['cost']
            totals[0] += pacres[0] * per_acre
            per_acre = dcrop['gross'][1] - dcrop['cost']
            totals[1] += pacres[1] * per_acre
            per_acre = dcrop['gross'][2] - dcrop['cost']
            totals[2] += pacres[2] * per_acre

        else:
            # ran through all crops, so all is well
            valid = True

        if not valid:
            continue
        if max_expense and expense > max_expense:
            continue

        results.append(
            dict(triangle=totals, partition=partition, expense=expense))
    return results
