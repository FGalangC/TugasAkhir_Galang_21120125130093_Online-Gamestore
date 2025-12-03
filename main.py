# mengimpor class service dari file auth_service.py
from service import user_service
print("login bang dari kelompok XX!")
# Mengambil masukan username & password melalui console
username = input("username:kelompok1")
password = input("password:12345")
# Membuat objek logininfo dengan blueprint atribut dan method

auth = user_service(username,password)
auth.login()