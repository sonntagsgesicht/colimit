from colimit import Location

EARTH_CIRCUMFERENCE = 40075000.0


def min_dist_to_way_nodes(loc, way):
    if not way.geometry:
        return EARTH_CIRCUMFERENCE
    return min(loc.dist(g) for g in way.geometry)


def get_limit(latitude, longitude, speed, direction, get_ways):
    limit, ways = -1.0, ()
    # note 'get_ways' requires keyword arguments. positional arguments like
    # get_ways(latitude, longitude, 2*speed) are not allowed!
    ways = get_ways(latitude=latitude, longitude=longitude, radius=2 * speed)
    if not ways:
        return limit, ()
    loc = Location(latitude)
    data = list((min_dist_to_way_nodes(loc, way), way) for way in ways)
    data.sort(key=lambda pair: pair[0])  # sort by min_dist_to_way_nodes
    # not the best choice to do but a good starting point
    return ways[0].limit, ways


if __name__ == "__main__":

    import os
    import sys
    from colimit import Connection

    get_limit_file = 'full path to your file'
    # add file location to sys.path to be able to import it as a modul
    path, file = os.path.split(get_limit_file)
    if path not in sys.path:
        sys.path.append(path)
    module = __import__(file.replace('.py', ''))  # , fromlist=(FUNC_NAME,))
    get_limit = getattr(module, 'get_limit')
    # now, 'get_limit' can be tested

    # setup server connection
    user, password = 'your username', 'your password'
    url, port = 'https://limits.pythonanywhere.com', 443

    # start connection to limits server
    ci = Connection(user, password, url, port)
