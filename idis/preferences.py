import re

class PreferencesStore(object):
    @staticmethod
    def loadKVpair(filename):
        """ Load a file of the format
        key = NUMERIC_VALUE
        otherkey = "test"

        and return a dict"""

        res = {}
        data = [(lineno, i, [j.strip() for j in i.split('=',1)]) for lineno,i in enumerate(open(filename).readlines()) if i.strip()]
        str_matcher = re.compile("\"([^\"]*)\"")
        int_matcher = re.compile("[0-9]+")
        for lineno, line, key_value in data:
            try:
                key, value = key_value
            except ValueError:
                raise ValueError, "Could not parse line %d: %s" % (lineno + 1, line.strip())
    
            strmatch = str_matcher.match(value)
            if strmatch:
                res[key] = strmatch.group(1)
                continue

            if int_matcher.match(value):
                res[key] = int(value)
                continue

            raise ValueError, "Could not parse value for line: %d: %s" %  (lineno + 1, line.strip())
        return res

    @staticmethod
    def loadFromFileDefaults(defaults_name, prefs_name):
        defaults = PreferencesStore.loadKVpair(defaults_name)
        prefs = PreferencesStore.loadKVpair(prefs_name)
        return PreferencesStore(defaults, prefs)

    def __init__(self, prefs, defaults):
        self.defaults = defaults
        self.prefs = prefs

    def set(self, key, value):
        if type(value) not in [str,int,long]:
            raise ValueError

        self.prefs[key] = value

    def get(self, key):
        try:
            return self.prefs[key]
        except KeyError:
            return self.defaults[key]

    def save(self, filename):
        f = open(filename, "w")
        for k,v in self.prefs.iteritems():
            if type(v) == str:
                f.write("%s = \"%s\"\n" % (k,v))
            else:
                f.write("%s = %d\n" % (k,v))
