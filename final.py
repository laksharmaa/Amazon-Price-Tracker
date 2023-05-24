from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
import random as rd
import time
from datetime import date,datetime
from email.message import EmailMessage
import smtplib


def get_title(soup):
    try:
        title=soup.find('span',attrs={'id':'productTitle'})
        title_string=title.text
        product_title=title_string.strip()
    except AttributeError:
        product_title=""
    
    return product_title

def get_price(soup):
    try:
        price=soup.find('span',attrs={'class':'a-offscreen'})
        price_string=price.text.strip()

        price_string=price_string[1:]
        price_string=price_string.replace(',','')
        product_price=float(price_string)

    except AttributeError:
        try:
            price_whole=soup.find('span',attrs={'class':'a-price-whole'}).text.strip()
            price_decimal=soup.find('span',attrs={'class':'a-price-decimal'}).text.strip()

            price_string=price_whole+'.'+price_decimal
            # product_price=price_string
            product_price=float(price_string)
        except AttributeError:
            product_price=""   
    return product_price

def get_rating(soup):
    try:
        rating=soup.find('span',attrs={'class':'a-icon-alt'})
        rating_string=rating.text.strip()
        rating_list=rating_string.split()

        product_rating=rating_list[0]
    except AttributeError:
        product_rating=""
    
    return product_rating
    
#user functions
def send_mail(n, otp, email,userid):
    server = smtplib.SMTP('smtp.gmail.com', '587')
    server.starttls()
    server.login('parthapratimpaul2003@gmail.com', 'zxocqilpwogykbms')
    msg = EmailMessage()
    msg['From'] = "parthapratimpaul2003@gmail.com"
    msg['To'] = email
    if n == 1:
        msg.set_content(f'your login otp is {otp}')
        msg['Subject'] = f'OTP for Amazon Price Tracker with username [{userid}]'
    elif n == 2:
        msg.set_content('You have logged In with our system.\nIf u think someone trying to login into your account,Please contact us\nThank you Amazon Price Tracker Team')
        msg['Subject'] = 'Login warning'
    elif n==3:
        msg.set_content(f'Your Paasword is {userid}\nDont not share with anayone\nThank you Amazon Price Tracker Team')
        msg['Subject'] = 'Password restore for Amazon Price Tracker'
    server.send_message(msg)

def generate_username():
    u_data=pd.read_csv('users.csv')
    user_name=list(u_data['username'])
    username=input("Enter a username : ")
    while(username in user_name):
        print('This user name is already registered with us !!')
        username=input('Enter unique user name : ')
    return username

def sign_up_page():
    u_data=pd.read_csv('users.csv')
    name = input('Enter your name : ')
    email = input('Enter your email : ')
    email_list=list(u_data['email'])
    while (email in email_list): 
        print('This email is already registered with us!!')
        ch=input("Do you want to login with existing email ? (y/n) : ")
        if ch=='y':
            login_page()
            return
        email = input("Enter another email : ")
    username=generate_username()
    send_otp = str(rd.randint(10000, 99999))
    send_mail(1, send_otp, email,username)
    # send_otp='0'
    for i in range(3):
        if send_otp == input('Enter the otp : '):
            login_password = input('Create the password : ')
            f=open("users.csv","a",newline='')
            writer=csv.writer(f)
            writer.writerow([username,name,email,login_password])
            print('Your account created successfully')
            f.close()
            print("\n-- Now you can login using your email --\n")
            login_page()
            break
        print('You have left', 3-i-1, 'chance')
    else:
        print('You have entered 3 wrong otp')
        print('please do sign up process again')
        sign_up_page()
    return username

def forgot_password():
    u_data=pd.read_csv('users.csv')
    email=input("Enter email to restore password : ")
    email_list=list(u_data['email'])
    while email not in email_list:
        email=input('Enter valid email : ')
    password=email_list.index(email)
    send_mail(3,0,email,u_data.loc[password,'password'])


def login_page():
    u_data=pd.read_csv('users.csv')
    email = input('Enter your email : ')
    email_list = list(u_data['email'])
    if email in email_list:
        password = input('Enter the password : ')
        id_loc = email_list.index(email)
        if password == str(u_data.loc[id_loc, 'password']):
            print("Welcome", str(u_data.loc[id_loc, 'name']))
            send_mail(2, 0, email,'')
            return u_data.loc[id_loc, 'username']
        else:
            print("Wrong password\n")
            print('''select the option:
              1. Try again
              2. Forgot Password''')
            while (1):
                n = input(' --> ')
                match n:
                    case '1':
                        login_page()
                        break
                    case '2':
                        forgot_password()
                        print("Password has been succesfully sent to your registered email.")
                        print("\n-- Now you can login using your email --\n")
                        login_page()
                        break
                    case default:
                        print('Enter Valid Option !!')
    else:
        print('We unable to find your account\n')
        print('''Select the option:
              1. Try again
              2. Sign up with New Account''')
        while (1):
            n = input(' --> ')
            match n:
                case '1':
                    login_page()
                    break
                case '2':
                    sign_up_page()
                    break
                case default:
                    print('Enter Valid Option !!')


def get_url_id(username):
    url_data=pd.read_csv('url_data.csv')
    abc=list(url_data['username'])

    if username in abc:
        return url_data.loc[abc.index(username),'urlid']

    url=input("Enter URL of the Product : ")
    HEADERS = ({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36','Accept-Language': 'en-US,en;q=0.9'})
    webpage=requests.get(url,headers=HEADERS)
    soup=BeautifulSoup(webpage.content,'html.parser')
    title=get_title(soup)
    price=get_price(soup)
    rating=get_rating(soup)
    url_id=generate_urlid(url)
    store_url_data("url_data.csv",username,url,url_id)
    write_data(f'{url_id}.csv',title,price,rating)
    return url_id

def current_date():
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")
    return d1

def current_time():
    now = datetime.now()
    t = now.strftime("%H:%M:%S")
    return t

# csv functions
def check_file(filename):
    try:
        f=open(filename,"r")
        f.close()
    except:
        f=open(filename,"a",newline='')
        writer=csv.writer(f)
        writer.writerow(['name','price','rating','date','time'])
        f.close()   

def write_data(filename,name,price,rating):
    check_file(filename)
    f=open(filename,"a")
    writer=csv.writer(f)
    d=current_date()
    t=current_time()
    writer.writerow([name,price,rating,d,t])
    f.close()

def track_data(username):
    u_list=pd.read_csv('url_data.csv')
    ind=list(u_list['username']).index(username)
    url=u_list.loc[ind,'url']
    urlid=u_list.loc[ind,'urlid']
    HEADERS = ({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36','Accept-Language': 'en-US,en;q=0.9'})
    webpage=requests.get(url,headers=HEADERS)
    soup=BeautifulSoup(webpage.content,'html.parser')
    title=get_title(soup)
    price=get_price(soup)
    rating=get_rating(soup)
    write_data(f'{urlid}.csv',title,price,rating)

def generate_urlid(url):
    url_data=pd.read_csv('url_data.csv')
    url_list=list(url_data['url'])
    if url in url_list:
        return url_data.loc[url_list.index(url),'urlid']
    raw="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567"
    id=""
    # print("Generating URL-ID . . . . . . . ")
    for i in range(6):
        time.sleep(0.2)
        id+=raw[rd.randint(0,58)]
    return id
    
def store_url_data(filename,username,url,urlid):
    # generate url id using generate_urlid
    f=open(filename,"a",newline='')
    writer=csv.writer(f)
    writer.writerow([username,urlid,url])
    f.close()

def get_data_title(url_id):
    data=pd.read_csv(f'{url_id}.csv')
    # title_list=list(data['name'])
    # title=title_list[0]
    # return title
    return data.loc[0,'name']

def display_all_data(filename):
    data=pd.read_csv(f'{filename}.csv')
    print(data.loc[list(range(len(data.index))),['price','rating','time','date']])

# main function
print(" -- Welcome to Amazon Price Tracker -- ")
username=''
while (1):
    print("\n1.Login\n2.SignUp\n")
    ch=int(input("Enter Your Choice : "))
    if ch==1:
        username=login_page()        
        break
    elif ch==2:
        username=sign_up_page()
        break
    else:
        print("Invalid Choice !! Enter valid choice from menu.....")
url_id=get_url_id(username)

print(f'You are currently tracking the product : {get_data_title(url_id)}')
print("Tracking Data......(Press Ctrl+C to exit tracking)")
while(1):
    try:
        time.sleep(5)
        track_data(username)
    except:
        print("Price Successfully Tracked...Now Displaying data...")
        break
display_all_data(url_id)