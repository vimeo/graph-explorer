import sys
import os

sys.path = ["%s/%s" % (os.path.dirname(os.path.realpath(__file__)), 'wtforms')] + sys.path

from wtforms import Form, Field, BooleanField, StringField, validators, DecimalField, TextAreaField, HiddenField, IntegerField

from wtforms.validators import ValidationError


class is_None_or(object):
    def __init__(self, other, message=None):
        self.other = other
        if not message:
            message = u'Field must be None or %s' % other.message
        self.message = message
        self.other.message = message

    def __call__(self, form, field):
        if field.data is None:
            return True
        self.other(form, field)


class is_iterable(object):
    def __init__(self, message=None):
        if not message:
            message = u'Field must be an iterable'
        self.message = message

    def __call__(self, form, field):
        if not hasattr(field.data, '__iter__'):
            raise ValidationError(self.message)


class String_and(object):
    def __init__(self, other, message=None):
        self.other = other
        if not message:
            message = u'Field must be a string'
        self.message = message

    def __call__(self, form, field):
        if not isinstance(field.data, basestring):
            raise ValidationError(self.message)
        self.other(form, field)


# note don't use BooleanField, or wtforms will assume no data -> false
# use regular Field to catch when field not set (field.data will be None)
def isBool(form, field):
    if not isinstance(field.data, bool):
        raise ValidationError('Field must be a boolean')


class ConfigValidator(Form):
    listen_host = StringField('listen_host', [String_and(validators.Length(min=2))])
    listen_port = IntegerField('listen_port', [validators.NumberRange(0, 65535)])
    filename_metrics = StringField('filename_metrics', [String_and(validators.Length(min=2))])
    log_file = StringField('log_file', [String_and(validators.Length(min=2))])
    graphite_url_server = StringField('graphite_url_server', [String_and(validators.Length(min=2))])
    graphite_url_client = StringField('graphite_url_client', [String_and(validators.Length(min=2))])
    # the following 4 can be None.  validators.InputRequired gives weird errors
    graphite_username = StringField('graphite_username', [is_None_or(String_and(validators.Length(min=1)))])
    graphite_password = StringField('graphite_password', [is_None_or(String_and(validators.Length(min=1)))])
    # anthracite_url = StringField('anthracite_url', [is_None_or(String_and(validators.Length(min=1)))])
    anthracite_host = StringField('es_host', [String_and(validators.Length(min=2))])
    anthracite_port = IntegerField('es_port', [validators.NumberRange(0, 65535)])
    anthracite_index= StringField('es_index', [String_and(validators.Length(min=2))])
    anthracite_add_url = StringField('anthracite_add_url', [is_None_or(String_and(validators.Length(min=1)))])
    metric_plugin_dirs = Field('metric_plugin_dirs', [is_iterable()])
    es_host = StringField('es_host', [String_and(validators.Length(min=2))])
    es_port = IntegerField('es_port', [validators.NumberRange(0, 65535)])
    es_index = StringField('es_index', [String_and(validators.Length(min=2))])
    limit_es_metrics = IntegerField('limit_es_metrics', [validators.NumberRange(0, 1000000000000)])
    process_native_proto2 = Field('process_native_proto2', [isBool])
    alerting = Field('alerting', [isBool])
    alerting_db = StringField('alerting_db', [String_and(validators.Length(min=2))])
    # note: validation.Email() doesn't recognize strings like 'Graph Explorer <graph-explorer@yourcompany.com>'
    alerting_from = StringField('alerting_from', [String_and(validators.Length(min=2))])
    alert_backoff = IntegerField('alerting_backoff', [validators.NumberRange(1, 99999)])
    alerting_base_uri = StringField('alerting_base_uri', [String_and(validators.Length(min=2))])
    collectd_StoreRates = Field('collectd_StoreRates', [isBool])
    collectd_prefix = StringField('collectd_prefix', [String_and(validators.Length(min=2))])


class RuleAddForm(Form):
    alias = StringField('Alias')
    expr = TextAreaField('Expression', [validators.Length(min=5)])
    val_warn = DecimalField('Value warning')
    val_crit = DecimalField('Value critical')  # TODO at some point validate that val_warn != val_crit
    dest = StringField('Destination (1 or more comma-separated email addresses)', [validators.Length(min=2)])
    active = BooleanField('Active')
    warn_on_null = BooleanField('Warn on null')


class RuleEditForm(RuleAddForm):
    Id = HiddenField()
