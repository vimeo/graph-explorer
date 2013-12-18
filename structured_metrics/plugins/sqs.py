from . import Plugin


class SqsPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.sqs\.(?P<region>[^\.]+)\.(?P<queue>[^\.]+)\.(?P<type>ApproximateNumberOfMessages.*)$',
            'target_type': 'gauge',
            'configure': [
                lambda self, target: self.add_tag(target, 'unit', 'Msg'),
            ]
        }
    ]

# vim: ts=4 et sw=4:
