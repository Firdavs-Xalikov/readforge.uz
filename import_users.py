import os
import sys
import secrets
import subprocess

# 1. Handle auto-installation of missing dependencies
def check_dependencies(use_postgres):
    dependencies = ["bcrypt"]
    if use_postgres:
        dependencies.append("psycopg2-binary")
        
    for dep in dependencies:
        import_name = "bcrypt" if dep == "bcrypt" else "psycopg2"
        try:
            __import__(import_name)
        except ImportError:
            print(f"Required Python package '{dep}' not found. Installing via pip...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"Successfully installed '{dep}'.")
            except Exception as e:
                print(f"Failed to install '{dep}' automatically: {e}")
                print(f"Please install it manually using: pip install {dep}")
                sys.exit(1)

# 2. Simple manual .env parser
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    os.environ[key] = val

# Load environmental variables from .env
load_env()
database_url = os.environ.get("DATABASE_URL")
use_postgres = bool(database_url)

# Check and install dependencies
check_dependencies(use_postgres)

import bcrypt

# 3. List of users from the original file
users_data = [
    {"first_name": "Rustam", "last_name": "Xolmatov", "language": "uz", "email": "rustam.xolmatov93@mail.ru", "password": "9aW37k5wCnHD"},
    {"first_name": "Dildora", "last_name": "Xolmatva", "language": "uz", "email": "dildora.xolmatva83@gmail.com", "password": "epQHgI3%HLBk"},
    {"first_name": "Gulbahor", "last_name": "Nazarva", "language": "uz", "email": "gulbahor.nazarva65@mail.ru", "password": "bvHEzuPyXQEW"},
    {"first_name": "Кристина", "last_name": "Петроа", "language": "ru", "email": "kristina.petroa81@gmail.com", "password": "88*ad3DNBYjv"},
    {"first_name": "Иван", "last_name": "Кузнецов", "language": "ru", "email": "ivan.kuznetsov19@mail.ru", "password": "edonuSsddfrf"},
    {"first_name": "Aziz", "last_name": "Karimov", "language": "uz", "email": "aziz.karimov90@gmail.com", "password": "ifiUziXnFAAo"},
    {"first_name": "Alisher", "last_name": "Xolmatov", "language": "uz", "email": "alisher.xolmatov5@mail.ru", "password": "elK9mqmALOR2"},
    {"first_name": "Nilufar", "last_name": "Mirzayeva", "language": "uz", "email": "nilufar.mirzayeva34@gmail.com", "password": "cSGKgVP#8Kd0"},
    {"first_name": "Javlon", "last_name": "Saidov", "language": "uz", "email": "javlon.saidov4@mail.ru", "password": "3%mS8gBlKv3a"},
    {"first_name": "Александр", "last_name": "Соловьёв", "language": "ru", "email": "aleksandr.solovev68@gmail.com", "password": "zKgaS!m!x@S$"},
    {"first_name": "Алексей", "last_name": "Лебедев", "language": "ru", "email": "aleksey.lebedev34@mail.ru", "password": "uKBD@vok!nPT"},
    {"first_name": "Роман", "last_name": "Воробьёв", "language": "ru", "email": "roman.vorobev13@gmail.com", "password": "ZYl2dVAMH2#v"},
    {"first_name": "Sherzod", "last_name": "Nazarov", "language": "uz", "email": "sherzod.nazarov49@mail.ru", "password": "D6qeSP%t5Pv7"},
    {"first_name": "Gulnora", "last_name": "Boboyeva", "language": "uz", "email": "gulnora.boboyeva57@gmail.com", "password": "GDqQ7E#yIMtt"},
    {"first_name": "Gulnora", "last_name": "Qodirva", "language": "uz", "email": "gulnora.qodirva32@mail.ru", "password": "P%SuEPyHnvnz"},
    {"first_name": "Iroda", "last_name": "G'ulomva", "language": "uz", "email": "iroda.g'ulomva50@gmail.com", "password": "tsMM3JznnJAX"},
    {"first_name": "Павел", "last_name": "Богданов", "language": "ru", "email": "pavel.bogdanov60@mail.ru", "password": "ebZ3C#L7csGZ"},
    {"first_name": "Muxlisa", "last_name": "Rashidva", "language": "uz", "email": "muxlisa.rashidva1@gmail.com", "password": "F31DDxp63OHm"},
    {"first_name": "Алина", "last_name": "Зайцеа", "language": "ru", "email": "alina.zaytsea54@mail.ru", "password": "FZuG296c0%xP"},
    {"first_name": "Марина", "last_name": "Воробьёа", "language": "ru", "email": "marina.vorobea2@gmail.com", "password": "X!neGBuz%Sm6"},
    {"first_name": "Davron", "last_name": "Abdullayev", "language": "uz", "email": "davron.abdullayev70@mail.ru", "password": "A8$cV%R06AxY"},
    {"first_name": "Bobur", "last_name": "Saidov", "language": "uz", "email": "bobur.saidov66@gmail.com", "password": "pThGJWZhbj11"},
    {"first_name": "Umidjon", "last_name": "Ismoilov", "language": "uz", "email": "umidjon.ismoilov81@mail.ru", "password": "THnCMZ*CY7Bv"},
    {"first_name": "Никита", "last_name": "Соколов", "language": "ru", "email": "nikita.sokolov17@gmail.com", "password": "iy8CsT07Lq8T"},
    {"first_name": "Екатерина", "last_name": "Волкоа", "language": "ru", "email": "ekaterina.volkoa30@mail.ru", "password": "IWG2x9aJTFMP"},
    {"first_name": "Nodirbek", "last_name": "Yusupov", "language": "uz", "email": "nodirbek.yusupov62@gmail.com", "password": "!2kUtMXhkPr*"},
    {"first_name": "Наталья", "last_name": "Семёноа", "language": "ru", "email": "natalya.semenoa45@mail.ru", "password": "bbAjLGmsDx5S"},
    {"first_name": "Kamola", "last_name": "Ismoilva", "language": "uz", "email": "kamola.ismoilva20@gmail.com", "password": "AZvlMz@B*k4o"},
    {"first_name": "Shahnoza", "last_name": "Ismoilva", "language": "uz", "email": "shahnoza.ismoilva72@mail.ru", "password": "pH1Dr8@h97s!"},
    {"first_name": "Егор", "last_name": "Волков", "language": "ru", "email": "egor.volkov32@gmail.com", "password": "@vauP7@L7V21"},
    {"first_name": "Jasur", "last_name": "Qodirov", "language": "uz", "email": "jasur.qodirov87@mail.ru", "password": "jxUdcfQm$9!s"},
    {"first_name": "Егор", "last_name": "Павлов", "language": "ru", "email": "egor.pavlov5@gmail.com", "password": "B1qRmUR8*AK3"},
    {"first_name": "Мария", "last_name": "Морозоа", "language": "ru", "email": "mariya.morozoa44@mail.ru", "password": "2GgLLT@ZQ#I#"},
    {"first_name": "Юлия", "last_name": "Лебедеа", "language": "ru", "email": "yuliya.lebedea45@gmail.com", "password": "A@pQyOMqlfZZ"},
    {"first_name": "Марина", "last_name": "Семёноа", "language": "ru", "email": "marina.semenoa70@mail.ru", "password": "gZMnafy8h#Ws"},
    {"first_name": "Gulnora", "last_name": "Tursunva", "language": "uz", "email": "gulnora.tursunva81@gmail.com", "password": "kBf6wmxe1mbV"},
    {"first_name": "Madina", "last_name": "Rahimva", "language": "uz", "email": "madina.rahimva18@mail.ru", "password": "NHMx1eOc3g@%"},
    {"first_name": "Malika", "last_name": "Karimva", "language": "uz", "email": "malika.karimva6@gmail.com", "password": "p1Z5ibXt80nk"},
    {"first_name": "Aziz", "last_name": "Ismoilov", "language": "uz", "email": "aziz.ismoilov83@mail.ru", "password": "8Btb2abplBpq"},
    {"first_name": "Иван", "last_name": "Голубев", "language": "ru", "email": "ivan.golubev61@gmail.com", "password": "cJF5xgUskL@6"},
    {"first_name": "Umidjon", "last_name": "Yoldashev", "language": "uz", "email": "umidjon.yoldashev86@mail.ru", "password": "GgebhbkXNNv!"},
    {"first_name": "Sanjar", "last_name": "Rahimov", "language": "uz", "email": "sanjar.rahimov78@gmail.com", "password": "hOV48vsoUu19"},
    {"first_name": "Илья", "last_name": "Козлов", "language": "ru", "email": "ilya.kozlov50@mail.ru", "password": "5IQLJhQbtN2F"},
    {"first_name": "Davron", "last_name": "Sattorov", "language": "uz", "email": "davron.sattorov49@gmail.com", "password": "XWD5KaPHI2uf"},
    {"first_name": "Jasur", "last_name": "Rashidov", "language": "uz", "email": "jasur.rashidov37@mail.ru", "password": "ssJ@Sk!WzDNh"},
    {"first_name": "Александр", "last_name": "Семёнов", "language": "ru", "email": "aleksandr.semenov87@gmail.com", "password": "Y7AGbX6lTiDY"},
    {"first_name": "Алина", "last_name": "Воробьёа", "language": "ru", "email": "alina.vorobea75@mail.ru", "password": "%H%P9#zyBylx"},
    {"first_name": "Bobur", "last_name": "Ergashev", "language": "uz", "email": "bobur.ergashev90@gmail.com", "password": "LUTZ%tFf@VnV"},
    {"first_name": "Shohruh", "last_name": "Yoldashev", "language": "uz", "email": "shohruh.yoldashev81@mail.ru", "password": "7ktOdSJ%cmeA"},
    {"first_name": "Rustam", "last_name": "Xoshimov", "language": "uz", "email": "rustam.xoshimov73@gmail.com", "password": "!BHJ2m5qGeRz"},
    {"first_name": "Андрей", "last_name": "Лебедев", "language": "ru", "email": "andrey.lebedev24@mail.ru", "password": "WkdgeV6!iYpl"},
    {"first_name": "Shohruh", "last_name": "Xoshimov", "language": "uz", "email": "shohruh.xoshimov33@gmail.com", "password": "ODl#Yx5uVECw"},
    {"first_name": "Виктор", "last_name": "Попов", "language": "ru", "email": "viktor.popov5@mail.ru", "password": "GThdgH$9hmsO"},
    {"first_name": "Zarina", "last_name": "Xoshimva", "language": "uz", "email": "zarina.xoshimva97@gmail.com", "password": "azM4n8PVGXpV"},
    {"first_name": "Malika", "last_name": "G'ulomva", "language": "uz", "email": "malika.g'ulomva62@mail.ru", "password": "Wv4Esb7yeuCj"},
    {"first_name": "Андрей", "last_name": "Волков", "language": "ru", "email": "andrey.volkov80@gmail.com", "password": "Vr5mXcj5RPD9"},
    {"first_name": "Анастасия", "last_name": "Павлоа", "language": "ru", "email": "anastasiya.pavloa15@mail.ru", "password": "UsQChx5s4tI1"},
    {"first_name": "Diyorbek", "last_name": "Boboyev", "language": "uz", "email": "diyorbek.boboyev53@gmail.com", "password": "FtdILQvH!nO6"},
    {"first_name": "Islom", "last_name": "Karimov", "language": "uz", "email": "islom.karimov62@mail.ru", "password": "ot$hB9KpGzU3"},
    {"first_name": "Javlon", "last_name": "Ergashev", "language": "uz", "email": "javlon.ergashev34@gmail.com", "password": "EEmXL1uhLsc4"},
    {"first_name": "Nodirbek", "last_name": "Yoldashev", "language": "uz", "email": "nodirbek.yoldashev65@mail.ru", "password": "R$r4a*KxU3f0"},
    {"first_name": "Gulnora", "last_name": "Ne'matva", "language": "uz", "email": "gulnora.ne'matva28@gmail.com", "password": "Jxrx%Dwzkl@J"},
    {"first_name": "Shahnoza", "last_name": "Rashidva", "language": "uz", "email": "shahnoza.rashidva23@mail.ru", "password": "AryNzbi%0h%S"},
    {"first_name": "Дарья", "last_name": "Новикоа", "language": "ru", "email": "darya.novikoa43@gmail.com", "password": "K@lb09rIFxUe"},
    {"first_name": "Никита", "last_name": "Новиков", "language": "ru", "email": "nikita.novikov21@mail.ru", "password": "VaT%5%jpTFPW"},
    {"first_name": "Андрей", "last_name": "Соколов", "language": "ru", "email": "andrey.sokolov74@gmail.com", "password": "hLn@5$d*rcFl"},
    {"first_name": "Sanjar", "last_name": "Abdullayev", "language": "uz", "email": "sanjar.abdullayev29@mail.ru", "password": "xvnNGdcmyHc7"},
    {"first_name": "Jasur", "last_name": "Sattorov", "language": "uz", "email": "jasur.sattorov67@gmail.com", "password": "E4nSmwfIp7@#"},
    {"first_name": "Muxlisa", "last_name": "Rahimva", "language": "uz", "email": "muxlisa.rahimva98@mail.ru", "password": "JoppZrDDs7Yv"},
    {"first_name": "Muxlisa", "last_name": "Nazarva", "language": "uz", "email": "muxlisa.nazarva3@gmail.com", "password": "X1*eYgURZEQ3"},
    {"first_name": "Yulduz", "last_name": "Rahimva", "language": "uz", "email": "yulduz.rahimva73@mail.ru", "password": "PZgP%sTF2bUn"},
    {"first_name": "Илья", "last_name": "Соловьёв", "language": "ru", "email": "ilya.solovev68@gmail.com", "password": "xiP3z#cCr1Y6"},
    {"first_name": "Олег", "last_name": "Новиков", "language": "ru", "email": "oleg.novikov82@mail.ru", "password": "ffeIIemGp%b3"},
    {"first_name": "Ozoda", "last_name": "Yusupva", "language": "uz", "email": "ozoda.yusupva31@gmail.com", "password": "fKoNSvph$Ik7"},
    {"first_name": "Nigora", "last_name": "Qodirva", "language": "uz", "email": "nigora.qodirva76@mail.ru", "password": "s4p$qL0KJFlK"},
    {"first_name": "Malika", "last_name": "Saidva", "language": "uz", "email": "malika.saidva59@gmail.com", "password": "CXzU6M98NdFQ"},
    {"first_name": "Nargiza", "last_name": "Rahimva", "language": "uz", "email": "nargiza.rahimva29@mail.ru", "password": "y$XYbTuEPP!I"},
    {"first_name": "Никита", "last_name": "Иванов", "language": "ru", "email": "nikita.ivanov37@gmail.com", "password": "BLhcuiS4h%X4"},
    {"first_name": "Светлана", "safe": "Воробьёа", "language": "ru", "email": "svetlana.vorobea46@mail.ru", "password": "n%Ct1RTrzJ%m"},
    {"first_name": "Кристина", "last_name": "Семёноа", "language": "ru", "email": "kristina.semenoa95@gmail.com", "password": "8Iq0na0p@Yt1"},
    {"first_name": "Ольга", "last_name": "Павлоа", "language": "ru", "email": "olga.pavloa36@mail.ru", "password": "oW56KTLTY*XP"},
    {"first_name": "Светлана", "last_name": "Богданоа", "language": "ru", "email": "svetlana.bogdanoa1@gmail.com", "password": "@W4MxMs3WDlQ"},
    {"first_name": "Ozoda", "last_name": "Ergasheva", "language": "uz", "email": "ozoda.ergasheva42@mail.ru", "password": "FPA2bdgG@MN3"},
    {"first_name": "Malika", "last_name": "Rahimva", "language": "uz", "email": "malika.rahimva67@gmail.com", "password": "%3X7TfS5bi*D"},
    {"first_name": "Umidjon", "last_name": "Xolmatov", "language": "uz", "email": "umidjon.xolmatov13@mail.ru", "password": "0V#Zty1!Z4R*"},
    {"first_name": "Виктор", "last_name": "Петров", "language": "ru", "email": "viktor.petrov96@gmail.com", "password": "lvUOUjN$woLR"},
    {"first_name": "Bekzod", "last_name": "Yoldashev", "language": "uz", "email": "bekzod.yoldashev66@mail.ru", "password": "1u*L$A#y0xhn"},
    {"first_name": "Ксения", "last_name": "Новикоа", "language": "ru", "email": "kseniya.novikoa46@gmail.com", "password": "f0baNaMYmbdz"},
    {"first_name": "Bobur", "last_name": "Nazarov", "language": "uz", "email": "bobur.nazarov23@mail.ru", "password": "@I$sz0psu%$n"},
    {"first_name": "Nargiza", "last_name": "Karimva", "language": "uz", "email": "nargiza.karimva4@gmail.com", "password": "mjv%!73hbPsE"},
    {"first_name": "Sirojiddin", "last_name": "Nazarov", "language": "uz", "email": "sirojiddin.nazarov46@mail.ru", "password": "JveImiSy5Xcg"},
    {"first_name": "Javlon", "last_name": "Xolmatov", "language": "uz", "email": "javlon.xolmatov29@gmail.com", "password": "Yf4gEFCfuwOa"},
    {"first_name": "Jasur", "last_name": "Mirzayev", "language": "uz", "email": "jasur.mirzayev59@mail.ru", "password": "M1G@iFXC0NZ!"},
    {"first_name": "Юлия", "last_name": "Богданоа", "language": "ru", "email": "yuliya.bogdanoa3@gmail.com", "password": "FlwvTWxaLYUo"},
    {"first_name": "Javlon", "last_name": "Qodirov", "language": "uz", "email": "javlon.qodirov43@mail.ru", "password": "XQZip2SFXy7K"},
    {"first_name": "Nigora", "last_name": "Yoldasheva", "language": "uz", "email": "nigora.yoldasheva45@gmail.com", "password": "E3eJdRtEqlzI"},
    {"first_name": "Валентина", "last_name": "Виноградоа", "language": "ru", "email": "valentina.vinogradoa70@mail.ru", "password": "q47EuVTBZWAM"},
    {"first_name": "Aziz", "last_name": "Tursunov", "language": "uz", "email": "aziz.tursunov61@gmail.com", "password": "#AD5qH4VFZ$B"},
    {"first_name": "Татьяна", "last_name": "Павлоа", "language": "ru", "email": "tatyana.pavloa17@mail.ru", "password": "p$lIXdsNbXlw"},
    {"first_name": "Валентина", "last_name": "Петроа", "language": "ru", "email": "valentina.petroa30@gmail.com", "password": "PyniU#MyiNlC"},
    {"first_name": "Максим", "last_name": "Морозов", "language": "ru", "email": "maksim.morozov37@mail.ru", "password": "qZKTZ7qJwdUS"},
    {"first_name": "Gulbahor", "last_name": "Saidva", "language": "uz", "email": "gulbahor.saidva53@gmail.com", "password": "d7FZTmxLoICf"},
    {"first_name": "Shohruh", "last_name": "Jo'rayev", "language": "uz", "email": "shohruh.jo'rayev52@mail.ru", "password": "fu3zMtWfNwD@"},
    {"first_name": "Davron", "last_name": "Xoshimov", "language": "uz", "email": "davron.xoshimov92@gmail.com", "password": "%G3SaoKfgFoe"},
    {"first_name": "Bobur", "last_name": "Xoshimov", "language": "uz", "email": "bobur.xoshimov41@mail.ru", "password": "ASl1YCJ*lS24"},
    {"first_name": "Javlon", "last_name": "Boboyev", "language": "uz", "email": "javlon.boboyev44@gmail.com", "password": "#5$gA2$q!yfH"},
    {"first_name": "Malika", "last_name": "Nazarva", "language": "uz", "email": "malika.nazarva23@mail.ru", "password": "uEHFhvTS0lzN"},
    {"first_name": "Анна", "last_name": "Воробьёа", "language": "ru", "email": "anna.vorobea18@gmail.com", "password": "r!9EEa$4rSMr"},
    {"first_name": "Анастасия", "last_name": "Петроа", "language": "ru", "email": "anastasiya.petroa91@mail.ru", "password": "sEQp2vt7ZAoL"},
    {"first_name": "Sardor", "last_name": "Rashidov", "language": "uz", "email": "sardor.rashidov2@gmail.com", "password": "U!AfhJMzoN5o"},
    {"first_name": "Кристина", "last_name": "Попоа", "language": "ru", "email": "kristina.popoa21@mail.ru", "password": "P47ULvjfb7!k"},
    {"first_name": "Роман", "last_name": "Павлов", "language": "ru", "email": "roman.pavlov96@gmail.com", "password": "QHn!3!yPbTlK"},
    {"first_name": "Владимир", "last_name": "Попов", "language": "ru", "email": "vladimir.popov81@mail.ru", "password": "GFkrddYsLVx*"},
    {"first_name": "Полина", "last_name": "Соколоа", "language": "ru", "email": "polina.sokoloa88@gmail.com", "password": "vnNPWxTODVrV"},
    {"first_name": "Юлия", "last_name": "Голубеа", "language": "ru", "email": "yuliya.golubea33@mail.ru", "password": "EhfnZgB@2@uM"},
    {"first_name": "Diyorbek", "last_name": "Sattorov", "language": "uz", "email": "diyorbek.sattorov78@gmail.com", "password": "ksDur4Zlf49y"},
    {"first_name": "Dilnoza", "last_name": "Qodirva", "language": "uz", "email": "dilnoza.qodirva28@mail.ru", "password": "Vae$2sKjh$1R"},
    {"first_name": "Алексей", "last_name": "Петров", "language": "ru", "email": "aleksey.petrov9@gmail.com", "password": "4bwvWLa4Sz8k"},
    {"first_name": "Kamola", "last_name": "Qodirva", "language": "uz", "email": "kamola.qodirva70@mail.ru", "password": "P%62tZkhQM1V"},
    {"first_name": "Aziz", "last_name": "Ne'matov", "language": "uz", "email": "aziz.ne'matov62@gmail.com", "password": "rMR*dyC5ksV1"},
    {"first_name": "Кристина", "last_name": "Козлоа", "language": "ru", "email": "kristina.kozloa47@mail.ru", "password": "*E4YHoDxzoCG"},
    {"first_name": "Екатерина", "last_name": "Новикоа", "language": "ru", "email": "ekaterina.novikoa84@gmail.com", "password": "my*G!D6Co$k0"},
    {"first_name": "Александр", "last_name": "Павлов", "language": "ru", "email": "aleksandr.pavlov87@mail.ru", "password": "j4r##o$n6Yvy"},
    {"first_name": "Илья", "last_name": "Голубев", "language": "ru", "email": "ilya.golubev73@gmail.com", "password": "8lrVhZEgVfbB"},
    {"first_name": "Gulbahor", "last_name": "Boboyeva", "language": "uz", "email": "gulbahor.boboyeva59@mail.ru", "password": "Mpr2lzoTvURb"},
    {"first_name": "Алина", "last_name": "Новикоа", "language": "ru", "email": "alina.novikoa33@mail.ru", "password": "pEV$*T!fTmTP"},
    {"first_name": "Дарья", "last_name": "Воробьёа", "language": "ru", "email": "darya.vorobea78@mail.ru", "password": "oeFGTy5c4oc!"},
    {"first_name": "Наталья", "last_name": "Соловьёа", "language": "ru", "email": "natalya.solovea15@gmail.com", "password": "jHxtLWsGI4bd"},
    {"first_name": "Ксения", "last_name": "Зайцеа", "language": "ru", "email": "kseniya.zaytsea44@mail.ru", "password": "t!#9eejxY8u5"},
    {"first_name": "Islom", "last_name": "Qodirov", "language": "uz", "email": "islom.qodirov51@gmail.com", "password": "D%jUQ*BNqfBv"},
    {"first_name": "Jasur", "last_name": "Saidov", "language": "uz", "email": "jasur.saidov47@mail.ru", "password": "7Q7XTOaQ9QDc"},
    {"first_name": "Алина", "last_name": "Голубеа", "language": "ru", "email": "alina.golubea32@gmail.com", "password": "6fssIXIi#HT*"},
    {"first_name": "Ирина", "last_name": "Козлоа", "language": "ru", "email": "irina.kozloa75@mail.ru", "password": "remz2mUKEsjM"},
    {"first_name": "Валентина", "last_name": "Соловьёа", "language": "ru", "email": "valentina.solovea98@gmail.com", "password": "RU$FSZQhRP9#"},
    {"first_name": "Javlon", "last_name": "Ne'matov", "language": "uz", "email": "javlon.ne'matov48@mail.ru", "password": "FEStrAa6Z5YM"},
    {"first_name": "Игорь", "last_name": "Павлов", "language": "ru", "email": "igor.pavlov22@gmail.com", "password": "isMNGRjykwMT"},
    {"first_name": "Елена", "last_name": "Соколоа", "language": "ru", "email": "elena.sokoloa60@mail.ru", "password": "T2i!OwJGcvIE"},
    {"first_name": "Yulduz", "last_name": "Saidva", "language": "uz", "email": "yulduz.saidva91@gmail.com", "password": "cBgZ5zK#mzEh"},
    {"first_name": "Gulnora", "last_name": "G'ulomva", "language": "uz", "email": "gulnora.g'ulomva17@mail.ru", "password": "gkjRrayIbPdB"},
    {"first_name": "Rustam", "last_name": "Sattorov", "language": "uz", "email": "rustam.sattorov42@gmail.com", "password": "Pd!ZRwh1flQ@"},
    {"first_name": "Ozoda", "last_name": "Jo'rayeva", "language": "uz", "email": "ozoda.jo'rayeva77@mail.ru", "password": "ZG7bdOOh1Qul"},
    {"first_name": "Umidjon", "last_name": "Karimov", "language": "uz", "email": "umidjon.karimov3@gmail.com", "password": "tAs*lTU2StQD"},
    {"first_name": "Sitora", "last_name": "Ne'matva", "language": "uz", "email": "sitora.ne'matva95@mail.ru", "password": "H9eN6JU%*JqG"},
    {"first_name": "Сергей", "last_name": "Лебедев", "language": "ru", "email": "sergey.lebedev2@gmail.com", "password": "8mUtDZldrph#"},
    {"first_name": "Мария", "last_name": "Соловьёа", "language": "ru", "email": "mariya.solovea27@mail.ru", "password": "xHUtwu*dSF4@"},
    {"first_name": "Виктория", "last_name": "Козлоа", "language": "ru", "email": "viktoriya.kozloa28@gmail.com", "password": "SX6BPdnbiZSh"},
    {"first_name": "Nigora", "last_name": "Rashidva", "language": "uz", "email": "nigora.rashidva30@mail.ru", "password": "W0WCdGcH3EDT"},
    {"first_name": "Мария", "last_name": "Зайцеа", "language": "ru", "email": "mariya.zaytsea27@gmail.com", "password": "P2JM@Bu9IrMK"},
    {"first_name": "Олег", "last_name": "Голубев", "language": "ru", "email": "oleg.golubev12@mail.ru", "password": "Qa!FuO5BgAUf"},
    {"first_name": "Виктор", "last_name": "Виноградов", "language": "ru", "email": "viktor.vinogradov57@gmail.com", "password": "x3rMdotbrMt#"},
    {"first_name": "Кристина", "last_name": "Соловьёа", "language": "ru", "email": "kristina.solovea95@mail.ru", "password": "Tmv7Yl1RYQeE"},
    {"first_name": "Nilufar", "last_name": "Boboyeva", "language": "uz", "email": "nilufar.boboyeva26@gmail.com", "password": "ber#D3ncgOio"},
    {"first_name": "Rustam", "last_name": "Yusupov", "language": "uz", "email": "rustam.yusupov16@mail.ru", "password": "!r*2awCs#o*T"},
    {"first_name": "Sherzod", "last_name": "Ne'matov", "language": "uz", "email": "sherzod.ne'matov64@gmail.com", "password": "jSBCjIwbHIif"},
    {"first_name": "Сергей", "last_name": "Зайцев", "language": "ru", "email": "sergey.zaytsev26@mail.ru", "password": "$g0UIbPf6KQ0"},
    {"first_name": "Егор", "last_name": "Попов", "language": "ru", "email": "egor.popov96@gmail.com", "password": "IZ2O1XtXX0sa"},
    {"first_name": "Наталья", "last_name": "Богданоа", "language": "ru", "email": "natalya.bogdanoa31@mail.ru", "password": "#GWEzolegZP4"},
    {"first_name": "Diyorbek", "last_name": "Rahimov", "language": "uz", "email": "diyorbek.rahimov71@gmail.com", "password": "O6a88$RWEWTi"},
    {"first_name": "Дмитрий", "last_name": "Морозов", "language": "ru", "email": "dmitriy.morozov51@mail.ru", "password": "*IPjCHH8S%9C"},
    {"first_name": "Виктория", "last_name": "Попоа", "language": "ru", "email": "viktoriya.popoa19@gmail.com", "password": "i*U*A*vUEwt6"},
    {"first_name": "Наталья", "last_name": "Петроа", "language": "ru", "email": "natalya.petroa23@mail.ru", "password": "fPWU2p0tGWnU"},
    {"first_name": "Sirojiddin", "last_name": "Ismoilov", "language": "uz", "email": "sirojiddin.ismoilov46@gmail.com", "password": "%%M5lJYL5o59"},
    {"first_name": "Jasur", "last_name": "Boboyev", "language": "uz", "email": "jasur.boboyev94@mail.ru", "password": "w%taqU!%EV%R"},
    {"first_name": "Ксения", "last_name": "Смирноа", "language": "ru", "email": "kseniya.smirnoa49@gmail.com", "password": "GczaHhwNJPGE"},
    {"first_name": "Rayhona", "last_name": "Ergasheva", "language": "uz", "email": "rayhona.ergasheva34@mail.ru", "password": "4l*@lzq2LVf4"},
    {"first_name": "Александр", "last_name": "Зайцев", "language": "ru", "email": "aleksandr.zaytsev49@gmail.com", "password": "UfL03GTEXqyV"},
    {"first_name": "Feruza", "last_name": "G'ulomva", "language": "uz", "email": "feruza.g'ulomva9@mail.ru", "password": "AQjk5WY*1@dn"},
    {"first_name": "Nilufar", "last_name": "Ergasheva", "language": "uz", "email": "nilufar.ergasheva76@gmail.com", "password": "77318wi4Y!r$"},
    {"first_name": "Владимир", "last_name": "Соловьёв", "language": "ru", "email": "vladimir.solovev97@mail.ru", "password": "bDzZfLQX6plC"},
    {"first_name": "Дмитрий", "last_name": "Смирнов", "language": "ru", "email": "dmitriy.smirnov10@gmail.com", "password": "bn@lB6hzQ9h1"},
    {"first_name": "Otabek", "last_name": "Yoldashev", "language": "uz", "email": "otabek.yoldashev75@mail.ru", "password": "r0gsPQy%axJ%"},
    {"first_name": "Iroda", "last_name": "Tursunva", "language": "uz", "email": "iroda.tursunva34@gmail.com", "password": "lOXGMY$1gNMF"},
    {"first_name": "Dilnoza", "last_name": "Tursunva", "language": "uz", "email": "dilnoza.tursunva49@mail.ru", "password": "3GNzqgAV7!sU"},
    {"first_name": "Егор", "last_name": "Новиков", "language": "ru", "email": "egor.novikov44@gmail.com", "password": "z6gObi0PeJC4"},
    {"first_name": "Денис", "last_name": "Морозов", "language": "ru", "email": "denis.morozov38@gmail.com", "password": "zA6Z4AAhx3pg"},
    {"first_name": "Денис", "last_name": "Богданов", "language": "ru", "email": "denis.bogdanov18@mail.ru", "password": "j@xbv@CLBusA"},
    {"first_name": "Dilnoza", "last_name": "Ne'matva", "language": "uz", "email": "dilnoza.ne'matva67@mail.ru", "password": "m7mzlg1CG42t"},
    {"first_name": "Sanjar", "last_name": "Xoshimov", "language": "uz", "email": "sanjar.xoshimov8@gmail.com", "password": "rfu5LDOtNHPB"},
    {"first_name": "Umidjon", "last_name": "G'ulomov", "language": "uz", "email": "umidjon.g'ulomov20@mail.ru", "password": "DYePWtLClz7t"},
    {"first_name": "Анастасия", "last_name": "Голубеа", "language": "ru", "email": "anastasiya.golubea94@gmail.com", "password": "x3QZoeTpA**j"}
]

# We slice the users to import exactly 180 users as requested.
LIMIT_USERS = 180
users_to_import = users_data[:LIMIT_USERS]

def generate_recovery_key():
    random_hex = secrets.token_hex(4).upper()  # 8 characters
    parts = [random_hex[i:i+4] for i in range(0, len(random_hex), 4)]
    return 'RF-' + '-'.join(parts)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10)).decode('utf-8')

def import_to_sqlite(users):
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'readforge.db')
    print(f"Connecting to SQLite database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Initialize Schema if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            surname     TEXT NOT NULL,
            email       TEXT NOT NULL UNIQUE,
            password    TEXT NOT NULL,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN recovery_key TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    
    success_count = 0
    skipped_count = 0
    
    for index, u in enumerate(users):
        first_name = u.get("first_name", u.get("name", "")).strip()
        last_name = u.get("last_name", u.get("safe", u.get("surname", ""))).strip()
        email = u.get("email", "").strip().lower()
        password = u.get("password", "")
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            print(f"[{index+1}/{len(users)}] Skipped (already exists): {email}")
            skipped_count += 1
            continue
            
        try:
            hashed_pwd = hash_password(password)
            recovery_key = generate_recovery_key()
            cursor.execute("""
                INSERT INTO users (name, surname, email, password, recovery_key)
                VALUES (?, ?, ?, ?, ?)
            """, (first_name, last_name, email, hashed_pwd, recovery_key))
            success_count += 1
            print(f"[{index+1}/{len(users)}] Imported successfully: {email}")
        except Exception as e:
            print(f"[{index+1}/{len(users)}] Error importing {email}: {e}")
            
        if success_count % 10 == 0 and success_count > 0:
            conn.commit()
            
    conn.commit()
    conn.close()
    return success_count, skipped_count

def import_to_postgres(users, url):
    import psycopg2
    print("Connecting to PostgreSQL database...")
    conn = psycopg2.connect(url)
    cursor = conn.cursor()
    
    # Initialize Schema if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          SERIAL PRIMARY KEY,
            name        VARCHAR(255) NOT NULL,
            surname     VARCHAR(255) NOT NULL,
            email       VARCHAR(255) NOT NULL UNIQUE,
            password    VARCHAR(255) NOT NULL,
            created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS recovery_key VARCHAR(255)")
    except Exception:
        pass  # Column already exists
    
    conn.commit()
    
    success_count = 0
    skipped_count = 0
    
    for index, u in enumerate(users):
        first_name = u.get("first_name", u.get("name", "")).strip()
        last_name = u.get("last_name", u.get("safe", u.get("surname", ""))).strip()
        email = u.get("email", "").strip().lower()
        password = u.get("password", "")
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            print(f"[{index+1}/{len(users)}] Skipped (already exists): {email}")
            skipped_count += 1
            continue
            
        try:
            hashed_pwd = hash_password(password)
            recovery_key = generate_recovery_key()
            cursor.execute("""
                INSERT INTO users (name, surname, email, password, recovery_key)
                VALUES (%s, %s, %s, %s, %s)
            """, (first_name, last_name, email, hashed_pwd, recovery_key))
            success_count += 1
            print(f"[{index+1}/{len(users)}] Imported successfully: {email}")
        except Exception as e:
            print(f"[{index+1}/{len(users)}] Error importing {email}: {e}")
            
        if success_count % 10 == 0 and success_count > 0:
            conn.commit()
            
    conn.commit()
    conn.close()
    return success_count, skipped_count

def main():
    print(f"Starting import of up to {LIMIT_USERS} users...")
    if use_postgres:
        success, skipped = import_to_postgres(users_to_import, database_url)
    else:
        success, skipped = import_to_sqlite(users_to_import)
        
    print("\n--- Import Summary ---")
    print(f"Total target users: {len(users_to_import)}")
    print(f"Successfully imported: {success}")
    print(f"Skipped (already exist): {skipped}")
    print(f"Failed: {len(users_to_import) - success - skipped}")
    print("----------------------")

if __name__ == "__main__":
    main()