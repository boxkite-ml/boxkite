import json
import uuid
from datetime import date, datetime, timezone


class JSONEncoder(json.JSONEncoder):
    """
    The default JSON encoder.  This one extends the default simplejson encoder by also supporting
    ``datetime`` objects, ``UUID`` as well as ``Markup`` objects which are serialized as RFC 822
    datetime strings (same as the HTTP date format).  In order to support more data types override
    the :meth:`default` method.

    Adapted from `flask.json`.
    """

    def default(self, o):
        """Implement this method in a subclass such that it returns a
        serializable object for ``o``, or calls the base implementation (to
        raise a :exc:`TypeError`).
        For example, to support arbitrary iterators, you could implement
        default like this::
            def default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    return list(iterable)
                return JSONEncoder.default(self, o)
        """
        if isinstance(o, (date, datetime)):
            # Use isoformat to support lexical ordering needed for pagination
            return o.replace(tzinfo=timezone.utc).isoformat()
        if isinstance(o, uuid.UUID):
            return str(o)
        if hasattr(o, "__html__"):
            return str(o.__html__())
        return json.JSONEncoder.default(self, o)
