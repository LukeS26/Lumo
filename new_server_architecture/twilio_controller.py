import twilio.rest as twilio
from twilio.twiml.messaging_response import MessagingResponse

from config.config_variables import api_credentials, name, contacts, phone_number

class Contacts:
    def __init__(self, contact_list=[]):
        self.contacts_by_name = {}
        self.contacts_by_number = {}

        for number in contact_list:
            names = contact_list[number]
            for name in names:
                name = name.lower()
                if not name in self.contacts_by_name.keys():
                    self.contacts_by_name[name] = number
                if not number in self.contacts_by_number.keys():
                    self.contacts_by_number[number] = name

    def get_number_from_name(self, name:str):
        return self.contacts_by_name[name.lower()]
    
    def get_name_from_number(self, number:str):
        return self.contacts_by_number[number].title()

    # Check if the number is in the contact numbers, or the lowercase name is in the contact names
    def __contains__(self, key):
        return key in self.contacts_by_number.keys() or key.lower() in self.contacts_by_name.keys()

class TwilioController:
    def __init__(self, brain):
        self.client = twilio.Client(api_credentials["twilio"]["sid"], api_credentials["twilio"]["auth_token"])

        self.contact_list = Contacts(contact_list=contacts)

        self.brain = brain

    def send_text(self, contact_name, message):
        print(message)
        self.client.messages.create(
            from_=phone_number,
            body="\n".join(message.splitlines()),
            to=self.contact_list.get_number_from_name(contact_name)
        )

        self.brain.append_message(message, "assistant", contact_name)
    
    def respond_to_text(self, request):
        contact_number = request.values["From"]
        if not contact_number in self.contact_list:
            return

        contact_name = self.contact_list.get_name_from_number(contact_number)

        response_body = self.brain.make_request(messageBody=request.values["Body"], room_name="dorm", user=contact_name)

        response = MessagingResponse()

        response_message = ""

        for line in response_body:
            if line["role"] == "image":
                #TODO: IMAGES CURRENTLY SLIGHTLY BROKEN, NEED TO FINISH FIXING
                print(f"/image?image={line['content']}")

                # self.client.messages.create(
                #     from_=phone_number,
                #     media_url=line["content"][1],
                #     to=contact_number
                # )
            else:
                response_message += line["content"]
                response_message += "\n"

        response.message(response_message)

        return str(response)
        
    def update_url(self, url):
        self.client.incoming_phone_numbers.list(phone_number=phone_number)[0].update(sms_url=url + '/sms')




if __name__ == "__main__":
    controller = TwilioController()

    print(controller.contact_list.contacts_by_name)
    print(controller.contact_list.contacts_by_number)