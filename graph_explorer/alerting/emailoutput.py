import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from graph_explorer.alerting import Output, get_png
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
        if result.rule.results is not None:
            targets = [r['target'] for r in result.rule.results]
            try:
                img = MIMEImage(get_png(targets, result.rule.val_warn, result.rule.val_crit, self.config, 400))
                img.add_header('Content-ID', '<graph.png>')
                msg.attach(img)
            except Exception, e:
                print "ERROR Could not fetch PNG image: %s" % e
                msg.attach(MIMEText("Could not fetch PNG image: %s" % e))

        s = smtplib.SMTP(self.config.alerting_smtp)
        dest = [to_addr.strip() for to_addr in result.rule.dest.split(',')]
        s.sendmail(self.config.alerting_from, dest, msg.as_string())
        s.quit()
