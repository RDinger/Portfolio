# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 21:14:01 2018

@author: Remy H
Email functie maakt gebruik van
1)config.ini om log in gegevens gebruiker en server op te halen.
2)tijden checkFiles.txt; leeg tekstbestand waar tijden laatste check worden weggeschreven. In dezelfde map als script.
Config.ini file hoort in dezelfde map als dit script en te bestaan uit:

[Email_Handler]
server=<<server naam (bijv. smtp.live.com voor hotmail, smtp.gmail.com voor gmail, plus.smtp.mail.yahoo.com voor yahoo)>> 
port=<<port nummer (bijv 587 voor hotmail, 465 gmail, yahoo SSL)>>
receiver= <<vul hier emailadres ontvanger in>>
user= <<vul hier emailadres verzender in>>
password=<<wachtwoord van verzender>>

Dit script maakt enkel gebruik van de standaard libararies van Python
"""

import os,time, os.path, datetime, sys

CurrentTime=time.strftime("%d-%m-%Y %H:%M:%S")
path=r"C:\pad\naar\locatie"
targetPath=r"C:\pad\naar\locatie\voor\kopieren\bestanden"

def EmailBody(File_List):    
    print("Building up e-mail body...")

    # Create the container (outer) email message.
    Subject='laatst gewijzigde bestanden'
    text=''
    if len(File_List) > 0:
        for i in File_List:
            text=", ".join(File_List)
    else:
        text="Geen bestanden gewijzigd na laatste datum"
    
    message='Hierbij laatste bestanden: \n{}'.format(text)
    
    # start SendMail functie
    SendMail(File_List,message,Subject)

def SendMail(File_List,message,Subject):
    #https://stackoverflow.com/questions/3362600/how-to-send-email-attachments#3363254


    import smtplib, configparser
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText 


    print('Connecting to e-mail server')    
    
    # Config voor login gegevens
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    msg = MIMEMultipart()    
    msg.attach(MIMEText(message))
    msg['Subject'] = Subject
    msg['From'] = me=config.get('Email_Handler','user')
    msg['To'] = receiver=config.get('Email_Handler','receiver')
    
    # attach bestanden uit File_List
    if len(File_List) > 0:
        for file in File_List: #_voor test: ListPath
            part = MIMEBase('application', "octet-stream")
            with open(file, 'r') as att:
                part.set_payload(att.read())
            encoders.encode_base64(part) #encoding
            part.add_header('Content-Disposition',
                            'attachment; filename="{}"'.format(os.path.basename(file)))   
            msg.attach(part)  # bestand bijvoegen aan email
        att.close()
    else:
        pass

    # Send the email via SMTP server.
    try:
        s = smtplib.SMTP(config.get('Email_Handler','server'), config.get('Email_Handler','port'))
    except:
        print("Servnaam of port nr onjuist. Check config.ini.")
        sys.exit()
    s.ehlo() # Hostname checkt volledig gekwalificeerde domeinnaam van de localhost.
    s.starttls() #Zet verbinding van SMTP server in Transport Layer Security mode
    s.ehlo()
    try:
        s.login(config.get('Email_Handler','user'),config.get('Email_Handler','password'))
    except: # SMTPAuthenticationError wordt niet gepakt. Onduidelijk waarom.
        print("Onjuist emailadres en/ of wachtwoord opgegeven. Check config.ini")
        sys.exit()
    s.sendmail(me, receiver, msg.as_string())
    s.quit()
    print("E-mail send succesfully")

def CopyFolder(File_List, targetPath):
    # Niet gebruikt maar apart op te roepen via import door andere scripts, eventueel.
    import shutil
    # maak nieuwe directory aan, en geen error als dir al bestaat (exist_ok=True)
    os.makedirs(targetPath, exist_ok=True)
    
    # kopiëren van bestanden
    for file in File_List:
        shutil.copy(os.path.basename(file), targetPath)
    print("{} bestanden gekopieerd.".format(len(File_List)))

def FindFolder(path):    
    # lees textfile om laatste update tijd terug te halen (laatste regel)
    # Indien textfile leeg, hu default datum aan als baseline datum
    with open ("tijden checkFiles.txt", 'r')as doc:
        try:
            lines = doc.read().splitlines()
            last_line = lines[-1]
        except IndexError:
            last_line='01-01-2000 12:00:00' # default tijd voor eerste keer
    doc.close()
    
    counter=0
    File_List=[]
    Mod_list=[]
    CurrentTime=time.strftime("%d-%m-%Y %I:%M:%S")    
    
    print("Checking files and modification dates")
    
    # list comprehension om enkel bestanden te krijgen en directories uit te sluiten
    FilePath= [ f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))]
    os.chdir(path)
    for file in FilePath: # itereer door de lijst heen

        t=time.strftime('%d-%m-%Y %H:%M:%S', time.gmtime(os.path.getmtime(file)))
        #modificatietijd van file
        Mod_list.append(t) # append modificatie tijden aan lijst
        
        from dateutil.parser import parse  # parsing om te kunnen vergelijken
        CurTime_parsed = parse(CurrentTime) # niet gebruikt
        ModTime_parsed = parse(t) 
        LastTime_parsed=parse(last_line)
        
        # Vrgelijk tijden met huidige tijd. Modificatietijd moet groter zijn dan laatste check
        if (LastTime_parsed < ModTime_parsed):   
            counter+=1
            File_List.append(file)
            # print telkens de laatste toegevoegd van de lijst
            print("File: {} \t\tlast modified {}".format(File_List[-1],Mod_list[-1])) 
        else:   
            pass

    print("{} modified files found.".format(counter))
    
    # schrijf de tijd van deze actie in tekstfile weg (onderaan lijst)
    with open("tijden checkFiles.txt", 'a', encoding='utf-8') as doc:
        doc.writelines(CurrentTime + "\n")
    doc.close()
    
    EmailBody(File_List) # start EmailBody functie 


   
if __name__=='__main__':
    FindFolder(path)
