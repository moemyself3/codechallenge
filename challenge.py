# Using an example as a guide
# http://docs.astropy.org/en/stable/generated/examples/coordinates/plot_obs-planning.html
def filter_targets(obs, target_list, date_time, airmass=2.5):
    '''
    filter_targets filters a list of observable targets above a default airmass of 2.5

    Args:
        obs: str or dict - name of observatory
        target_list: table - expects 3 columns
            col1, col2, col3
            name of object, ra, dec
        date_time: Time object - date and time of expected observation
            date_time is expected to be converted to UTC from local time
        airmass(optional): float - sets limit on airmass for filtering targets

    Returns:
        filered_list: a table with columns name, ra, dec, SkyCoord, airmass

    '''
    from astropy.coordinates import AltAz, SkyCoord
    from astropy.table import Table
    filtered_list = Table(target_list, copy=True)
    filtered_list.rename_column('col1', 'name')
    filtered_list.rename_column('col2', 'ra')
    filtered_list.rename_column('col3', 'dec')
    filtered_list['ra'].unit = 'hourangle'
    filtered_list['dec'].unit = 'deg'
    filtered_list.add_index('name')
    filtered_list['SkyCoord'] = SkyCoord.guess_from_table(filtered_list)

    if type(obs) is str:
        # from web
        # https://stackoverflow.com/questions/8653516/python-list-of-dictionaries-search
        obs_location = next(item['location'] for item in observatories if item['name'] == obs)
    elif type(obs) is dict:
        obs_location = obs['location']
    else:
        raise TypeError('First argument expects str or dict type')

    site = AltAz(obstime=date_time, location=obs_location)
    target_airmass =[]
    for target in filtered_list:
        target_name = target['name']
        target_coord = filtered_list.loc[target_name]['SkyCoord']
        target_alt = target_coord.transform_to(site)
        if target_alt.secz < 1:
            target_airmass.append(99)
        else:
            target_airmass.append(target_alt.secz)
    filtered_list['airmass'] = target_airmass

    mask = filtered_list['airmass'] > airmass

    from itertools import compress
    rows_to_remove = list(compress(range(len(mask)), mask))

    filtered_list.remove_rows(rows_to_remove)
    return print(filtered_list)

from astropy.coordinates import EarthLocation
from astropy import units as u
observatories = [
    {'name': "EABA",
     'location': EarthLocation.from_geodetic(lon='-64.5467d', lat='-31.5983d',
                                             height=1350 * u.m)},
    {'name': "Macon",
     'location': EarthLocation.from_geodetic(lon='-67.2995d', lat='-24.5554d',
                                             height=4600 * u.m)},
    {'name': "Mamalluca",
     'location': EarthLocation.from_geodetic(lon='-70.6833d', lat='-29.9833d',
                                             height=1100 * u.m)},
    {'name': "CTMO",
     'location': EarthLocation.from_geodetic(lon='-97.568956d', lat='25.995789d',
                                             height=12 * u.m)},
    {'name': "Guillermo Haro",
     'location': EarthLocation.from_geodetic(lon='-110.384722d', lat='31.052778d',
                                             height=2480 * u.m)},
]


from astropy.time import Time
# complete with Apr 10, 2019 and whatever time here
utcoffset = -5*u.hour  # Central Daylight Time
date_time = Time('2019-04-10T15:14:59') - utcoffset

# Name, RA (in hour angle!!) and Dec (in degrees)
from astropy.io import ascii
target_list = ascii.read("""
PGC003183   0.90109 73.08478
UGC03858    7.51289 73.63019
UGC03859    7.51347 73.70633
UGC03889    7.56557 73.64353
PGC616899   14.55716    -37.83552
PGC021381   7.61031 74.44653
PGC021386   7.61209 74.45029
UGC03929    7.66532 75.42469
ESO336-006  18.60201    -37.94586
ESO336-001  18.54346    -39.45677
ESO327-012  14.71358    -40.60005
UGC11902    22.09344    16.72152
UGC02860    3.85436 78.29756
UGC11848    21.92643    10.46645
ESO328-031  15.20782    -42.01764
PGC3082596  15.25485    -40.80312
PGC069732   22.79608    40.12161
PGC2211350  22.99214    43.02606
NGC7379 22.79249    40.23881
ESO274-008  15.29708    -43.50163
""")


filter_targets(observatories[3], target_list, date_time)
