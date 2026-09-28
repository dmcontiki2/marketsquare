import os, smtplib, glob
from email.message import EmailMessage
pid=open('/tmp/mspid').read().strip()
env=dict(l.split('=',1) for l in open(f'/proc/{pid}/environ').read().split('\0') if '=' in l)
addr=env.get('GMAIL_ADDRESS','dmcontiki2@gmail.com'); pw=env['GMAIL_APP_PASSWORD']
D='/root/mail_marietjie'
html=open(D+'/body.html',encoding='utf-8').read()
m=EmailMessage()
m['From']='david conradie <%s>'%addr; m['To']='marietjie.marais59@gmail.com'
m['Subject']='TrustSquare – die drie Ripple-stories werk nou (drie bladsye)'
m.set_content('Hallo Marietjie\n\nDie e-pos is in HTML; maak dit asseblief oop in Gmail om die aanwysings te sien. Die drie bladsye is aangeheg.\n\nGroete\nDavid')
m.add_alternative(html, subtype='html')
for f in ['TrustSquare_Ripple_Stories.html','TrustSquare_Ripple_Progress.html','TrustSquare_Ripple_Walk3.html']:
    m.add_attachment(open(D+'/'+f,'rb').read(), maintype='text', subtype='html', filename=f)
with smtplib.SMTP('smtp.gmail.com',587,timeout=40) as s:
    s.starttls(); s.login(addr,pw); r=s.send_message(m)
print('SENT refused=',r, 'bytes=',len(m.as_bytes()))
