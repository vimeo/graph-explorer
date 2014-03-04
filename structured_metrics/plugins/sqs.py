from . import Plugin


class SqsPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.sqs\.(?P<region>[^\.]+)\.(?P<queue>[^\.]+)\.(?P<type>ApproximateNumberOfMessages.*)$',
            'target_type': 'gauge',
            'tags': {'unit': 'Msg'}
        }
    ]

# vim: ts=4 et sw=4:
