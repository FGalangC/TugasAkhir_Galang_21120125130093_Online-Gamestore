# Class user_service, sebagai class untuk membuat objek user
class user_service:
    # Constructor (__init__) untuk inisialisasi atribut username, password, dan data user
    def __init__(self, username, password):
        self.username = username
        self.password = password

        # Data user disimpan dalam dictionary
        self.data = {
            "kelompok1": {
                "username": "kelompok1",
                "password": "12345",
                "role": "mahasiswa"
            },
            "kelompok2": {
                "username": "kelompok2",
                "password": "12345",
                "role": "dosen"
            }
        }

    # Method untuk mengecek kesesuaian username dan password
    def check_password(self):
        user_data = self.data.get(self.username)
        if user_data and self.password == user_data['password']:
            return user_data
        return False

    # Method untuk proses login
    def login(self):
        data = self.check_password()
        if data:
            print("\nWelcome", data['username'])
            print("Logged in as:", data['role'])
        else:
            print("\nInvalid Login!\n")