import random
import string
import datetime


##
def randomUsername(num):
	username = []
	i = 0
	while i < num:
		temp = string.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789',random.randint(6,15))).replace(' ','')
		if not temp in username:
			username.append(temp)
			i += 1
	return username

def randomPassword(num):
	password = []
	for i in range (0,num):
		temp = string.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()123456789',random.randint(6,15))).replace(' ','')
		password.append(temp)
	return password


def randomEmail(num):
	email = []
	i = 0
	while i < num:
		temp = string.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789',random.randint(6,15))).replace(' ','')
		mail = random.choice(["gmail.com","qq.com","sina.com","126.com","163.com","sjtu.com","yahoo.com","sohu.com","hotmail.com","sjtu.edu.cn"])
		temp = temp + "@" + mail
		if not temp in email:
			email.append(temp)
			i +=1
	return email

def randomBirthday(num):
	birthday = []
	for  i in range(0,num):
		year = random.randint(1960,2010)
		month = random.randint(1,12)
		day = random.randint(1,31)
		month_str = str(month)
		if len(month_str) == 1:
			month_str = '0' + month_str
		day_str = str(day)
		if len(day_str) == 1:
			day_str = '0' + day_str 
		temp = str(year) + month_str + day_str
		birthday.append(temp)
	return birthday

def randomSex(num):
	sex=[]
	for i in range (0,num):
		temp = random.randint(0,1)
		sex.append(temp)
	return sex

def randomMacID(num):
	macID=[]
	i = 0
	while i < num:
		temp = ""
		for j in range(0,6):
			temp += string.join(random.sample('ABCDEF123456789',2)).replace(' ','')
			if j!=5:
				temp += "-"
		if not temp in macID:
			macID.append(temp)
			i += 1
	return macID

def randomValue(num,low,high):
	value=[]
	for i in range (0,num):
		value.append(str("%.2f" % random.uniform(low, high)))
	return value

def randomDate(num):
	date=[]
	i = 0
	while  i < num:
		#year = random.randint(2010,2012)
		#month = random.randint(1,12)
		#day = random.randint(1,28)
		# this may be out of range if with 2/30 2/31
		year = 2015
		month = 10
		day = random.randint(7,9)
		hour = random.randint(0,23)
		minute = random.randint(0,59)
		second = random.randint(0,59)

		month_str = str(month)
		if len(month_str) == 1:
			month_str = '0' + month_str
		day_str = str(day)
		if len(day_str) == 1:
			day_str = '0' + day_str 
		hour_str = str(hour)
		if len(hour_str) == 1:
			hour_str = '0' + hour_str
		minute_str = str(minute)
		if len(minute_str) == 1:
			minute_str = '0' + minute_str 		
		second_str = str(second)
		if len(second_str) == 1:
			second_str = '0' + second_str 	

		temp = str(year) + "-" + month_str + "-" + day_str + " " + hour_str + ":" + minute_str + ":" + second_str
		if not temp in date:
			date.append(temp)
			i += 1
	return date

def randomArea(num):
	area = []
	for i in range (0,num):
		#temp = random.choice(["Putuo","Fengxian","Jinshan","Minghang","Xuhui","Jingan","Jiading","Nanhui","Huangpu","Luwan"])
		#area.append(temp)
		area.append("Minghang")
	return area

def randomAreaTrue(num):
	area = []
	for i in range (0,num):
		temp = random.choice(["Putuo","Fengxian","Jinshan","Minghang","Xuhui","Jingan","Jiading","Nanhui","Huangpu","Luwan"])
		area.append(temp)
		#area.append("Minghang")
	return area


def randomWether(num):
	weather = []
	for i in range (0,num):
		temp = random.choice(["Cloudy","Wind","Fog","Snow","Drizzle","Fair","Haze","Light Rain","Mist"])
		weather.append(temp)
	return weather

def randomSunTime(num):
	sunrise = []
	sunset = []
	uploadTime = []

	baseDateStr = "2015-01-01 08:00:00"
	baseDate = datetime.datetime.strptime(baseDateStr,'%Y-%m-%d %H:%M:%S')
	date = ""

	for  i in range(0,num):
		baseDate += datetime.timedelta(days = 1)
		randomSeconds = random.randint(-7200,7200)
		date =baseDate + datetime.timedelta(seconds = randomSeconds)
		dateStr = date.strftime("%Y-%m-%d %H:%M:%S")
		uploadTime.append(dateStr)

		year = baseDate.year
		month = baseDate.month
		day = baseDate.day
		# this may be out of range if with 2/30 2/31
		hour1 = random.randint(5,7)
		minute1 = random.randint(0,59)
		second1 = random.randint(0,59)

		hour2 = random.randint(17,19)
		minute2 = random.randint(0,59)
		second2 = random.randint(0,59)



		month_str = str(month)
		if len(month_str) == 1:
			month_str = '0' + month_str
		day_str = str(day)
		if len(day_str) == 1:
			day_str = '0' + day_str

		hour1_str = str(hour1)
		if len(hour1_str) == 1:
			hour1_str = '0' + hour1_str
		minute1_str = str(minute1)
		if len(minute1_str) == 1:
			minute1_str = '0' + minute1_str
		second1_str = str(second1)
		if len(second1_str) == 1:
			second1_str = '0' + second1_str

		hour2_str = str(hour2)
		if len(hour2_str) == 1:
			hour2_str = '0' + hour2_str
		minute2_str = str(minute2)
		if len(minute2_str) == 1:
			minute2_str = '0' + minute2_str 		
		second2_str = str(second2)
		if len(second2_str) == 1:
			second2_str = '0' + second2_str 	

		time1 = str(year) + "-" + month_str + "-" + day_str + " " + hour1_str + ":" + minute1_str + ":" + second1_str
		time2 = str(year) + "-" + month_str + "-" + day_str + " " + hour2_str + ":" + minute2_str + ":" + second2_str

		sunrise.append(time1)
		sunset.append(time2)
		
	return sunrise,sunset,uploadTime

