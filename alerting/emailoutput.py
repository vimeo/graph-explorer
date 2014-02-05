import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from alerting import Output, get_png


class EmailOutput(Output):
    def __init__(self, config):
        self.config = config

    def submit(self, result):
        content = [
            "==== %s ====" % result.rule.name(),
            " val_warn: %f" % result.rule.val_warn,
            " val_crit: %f" % result.rule.val_crit,
            "\nResult:\n%s" % "\n".join(result.body),
            "\n\nThis email is sent to %s" % result.rule.dest
        ]
        msg = MIMEMultipart()
        msg["To"] = result.rule.dest
        msg["From"] = self.config.alerting_from
        msg["Subject"] = result.title
        import time

        msgText = MIMEText('%s<br><img src="cid:graph-%s.png">' % ("\n".join(content).replace("\n", "\n<br>"), time.time()), 'html')
        msg.attach(msgText)
        targets = [target for (target, value, status) in result.rule.results]
        img = MIMEImage(get_png(targets, self.config, 400))
        msg.attach(img)

        s = smtplib.SMTP('localhost')
        s.sendmail(self.config.alerting_from, result.rule.dest, msg.as_string())
        s.quit()
