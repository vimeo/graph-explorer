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
            """<head><style>
            body {
                background-color: rgb(18, 20, 23);
                color: rgb(173, 175, 174);
            }
            a {
                text-decoration: none;
                color: rgb(51, 181, 229);
            }
            </style></head>""",
            "<body>",
            "<b>%s</b>" % result.rule.name(),
            "<br>val_warn: %f" % result.rule.val_warn,
            "<br>val_crit: %f" % result.rule.val_crit,
            "<br>Result:",
            "<br>%s" % "\n<br>".join(result.body),
            '<br><img src="cid:graph.png">',
            '<br><a href="%s">Manage alert</a>' % manage_uri,
            "</body>"
        ]
        msg = MIMEMultipart()
        msg["To"] = result.rule.dest
        msg["From"] = self.config.alerting_from
        msg["Subject"] = result.title

        msgText = MIMEText("\n".join(content), 'html')
        msg.attach(msgText)
        targets = [target for (target, value, status) in result.rule.results]
        img = MIMEImage(get_png(targets, self.config, 400))
        msg.attach(img)

        s = smtplib.SMTP('localhost')
        s.sendmail(self.config.alerting_from, result.rule.dest, msg.as_string())
        s.quit()
