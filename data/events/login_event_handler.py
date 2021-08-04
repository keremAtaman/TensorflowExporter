class LoginEventHandler:
    def __init__(self):
        self.data_dict = {}
        self.data_dict['LOGIN'] = 0
        self.data_dict['LOGOUT'] = 0
        self.data_dict['number_of_users'] = 0
    def handle_event(self, is_login:bool):
        if is_login:
            self.data_dict['number_of_users'] +=1
            self.data_dict['LOGIN'] = 1
            self.data_dict['LOGOUT'] = 0
        else:
            self.data_dict['number_of_users'] -=1
            self.data_dict['LOGIN'] = 0
            self.data_dict['LOGOUT'] = 1
    def send_data(self)->dict:
        return self.data_dict