import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from alerting import Output, get_png
from urlparse import urljoin


class EmailOutput(Output):
    def __init__(self, config):
        self.config = config

    def submit(self, result):
        manage_uri = urljoin(self.config.alerting_base_uri, "/rules/view/%d" % result.rule.Id)
        content = [
            """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"/>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>%s</title><style type="text/css" >
            body {
                background-color: rgb(18, 20, 23);
                color: rgb(173, 175, 174);
            }
            a {
                text-decoration: none;
                color: rgb(51, 181, 229);
            }
            </style></head>""" % result.title,
            "<body>",
            "<center><b>%s</b></center>" % result.title,
            "<br/>val_warn: %f" % result.rule.val_warn,
            "<br/>val_crit: %f" % result.rule.val_crit,
            "<br/>Result:",
            "<br/>%s" % "\n<br/>".join(result.body),
            '<br/><img src="cid:graph.png" alt="graph" type="image/png" />',
            '<br/><a href="%s">Manage alert</a>' % manage_uri,
            "</body></html>"
        ]
        msg = MIMEMultipart()
        msg["To"] = result.rule.dest
        msg["From"] = self.config.alerting_from
        msg["Subject"] = result.title

        msgText = MIMEText("\n".join(content), 'html')
        msg.attach(msgText)
        targets = [target for (target, value, status) in result.rule.results]
        img = MIMEImage(get_png(targets, result.rule.val_warn, result.rule.val_crit, self.config, 400))
        img.add_header('Content-ID', '<graph.png>')

        msg.attach(img)

        s = smtplib.SMTP('localhost')
        s.sendmail(self.config.alerting_from, result.rule.dest, msg.as_string())
        s.quit()
