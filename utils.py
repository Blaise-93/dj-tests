import string
import random
from datetime import datetime, timedelta
import uuid

def password_setter():
    """ generate a random password for each user in our database until the client/
    patients/agent changes the password when the person request to change it. While,
    we allow django auth admin to hash the user's password."""
    
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=100))


def slug_modifier():
    """
    Generate a random string code as an adjunct to the patients' slug to
    mask it from the user or any other person viewing the URI. 
    So, we don't want the set slug to be easily identified.
    """
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))


def files(file):
    """ A helper function to upload and read individual file when sending emails to
    the user. """
    with open(file, "r") as f:
        data = f.read()
        return data


def generate_patient_unique_code():
    """
    Generate a random, unique order number using UUID for our patients
    """
    code = uuid.uuid4().hex.upper()
    return code[0:10]


class BMI:
    def __init__(self, height: None, weight: None):
        self.height = height
        self.weight = weight

    def patients_bmi(self) -> int:

        # check whether the user input the correct units
        # of weight and height.
        if self.height is None or self.weight is None:
            return f'Not provided'
        elif self.height and self.weight is not None:
            # check if the said height of a patient is greater than 1 foot
            if self.height > 0:
                square_foot = 0.3048  # in m2 based on metric conversion
                in_meter_square = (self.height * square_foot)
                bmi = round((self.weight) /
                            (in_meter_square * in_meter_square), 2)

                return f'{bmi}kg/m2'

        return f"Not provided"


def bmi(height, weight):
    """ weight/height function playground. :D """
    if height > 0:
        ft_in_square = 0.3048
        pt_height = (ft_in_square) * height
        height_per_meter_squared = pt_height * pt_height
        bmi = round((weight / height_per_meter_squared), 2)
        return bmi


def greetings_in_time_utc(name) -> str:
    """ A helper function that greet a user after a specific task is done (in utc+0). """
    hours = datetime.now().hour
    
    if hours >=4 and hours < 12:
        return f'Good morning {name}'
    
    elif hours >= 12 and hours < 17:
        return f'Good afternoon {name}'
    elif hours >= 17 and hours < 20 :
        return f'Good evening {name}'
    else:
        return f'Good night {name}'


#print(_greetings_in_time_utc("Blaise"))

def utc_standard_time():
    """ strictly convert wat to utc - my playground
    for date related migration pick-up in our db. :D """
    return datetime.now() - timedelta(hours=1)





def time_in_hr_min():
    " Helper function that dynamically output time in UTC+1 to the db as a Charfield \
    when a staff wants to update his/her record."
    hr = datetime.now().hour   
    timezone = datetime.now() 
    
    if hr >=0 and hr < 12:
        time_in_hr_and_min = str(timezone.time())[0:5]
        return f'{time_in_hr_and_min } AM'
    
    time_in_hr_and_min = str(timezone.time())[0:5]
    
    return f"{time_in_hr_and_min} PM"


def reminder_time():
     hr = datetime.now().hour   
     timezone = datetime.now() 
     if hr >=10 and hr < 12:
         return str(timezone.time())[0:5]
        
        #return f'{time_in_hr_and_min } AM'
        
        
    

# print(utc_standard_time())


# print(time_in_hr_min())
#print(datetime.now()  - timedelta(hours=1))
