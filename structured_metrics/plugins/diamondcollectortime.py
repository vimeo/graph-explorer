from . import Plugin


class DiamondCollectortimePlugin(Plugin):
    """
    capture collectortime of all diamond plugins
    """
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.(?P<diamond_plugin>[^\.]+)\.(?P<type>collector_time)_(?P<unit>ms)$',
            'target_type': 'gauge',
        }
    ]

# vim: ts=4 et sw=4:
