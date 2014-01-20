from . import Plugin


class CatchallDiamondPlugin(Plugin):
    """
    Like catchall, but for targets from diamond (presumably)
    """
    priority = -4

    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.(?P<tosplit>.*)',
            'target_type': 'unknown',
            'configure': [
                lambda self, target: self.add_tag(target, 'unit', 'unknown'),
                lambda self, target: self.add_tag(target, 'source', 'diamond'),
                lambda self, target: self.autosplit(target)
            ]
        },
    ]


# vim: ts=4 et sw=4:
