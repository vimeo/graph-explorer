from . import Plugin


class CatchallDiamondPlugin(Plugin):
    """
    Like catchall, but for targets from diamond (presumably)
    """
    priority = -4

    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.(?P<n1>[^\.]+)\.?(?P<n2>[^\.]*)\.?(?P<n3>[^\.]*)\.?(?P<n4>[^\.]*)$',
            'target_type': 'unknown',
            'configure': [
                lambda self, target: self.add_tag(target, 'what', 'unknown'),
                lambda self, target: self.add_tag(target, 'source', 'diamond'),
                lambda self, target: self.strip_empty_tags(target)
            ]
        },
    ]


# vim: ts=4 et sw=4:
