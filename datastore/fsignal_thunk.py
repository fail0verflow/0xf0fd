# Optional dependancy - allow the datastore
# to be instantiated without some of the harness
# integration code
try:
    from idis.fsignal import FSignal
except ImportError:
    # Mock FSignal if datastore is being used
    # t without pulling the entire "harness"
    class FSignal(object):
        def emit(*args):
            pass

        def connect(*args):
            raise NotImplementedError()
