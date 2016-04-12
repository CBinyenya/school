from AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException
class SMShandler(object):
    def __init__(self,recpts,msg):
        self.username = "CBinyenya";
        self.apikey   = "9496be239c872953f0ff82006c79cdaf081d896fc087ef46954a1256ae5560f3";
        #self.username = "Munai";
        #self.apikey   = "6259cef2f01d6ce6f2ed3e326e98c77877b3235aeea8a08d0db8f9977b941557";
        self.recpts = recpts
        self.msg = msg
    def reciepient(self):
        user2 = ""
        for user in self.recpts:
            user2 =user2+","+ str(user)        
        return user2[1:]
    def sendMessage(self):
        gateway = AfricasTalkingGateway(self.username, self.apikey)
        to=self.reciepient()
        print to
        try:
            pass
            recipients = gateway.sendMessage(to, self.msg)
            for recipient in recipients:
                # Note that only the Status "Success" means the message was sent
                print 'number=%s;status=%s;messageId=%s;cost=%s' % (recipient['number'],
                                                                    recipient['status'],
                                                                    recipient['messageId'],
                                                                    recipient['cost'])
            return recipients
        except AfricasTalkingGatewayException, e:
            print 'Encountered an error while sending: %s' % str(e)
            
class PhoneNumber(object):
    def __init__(self, phn):
        self.phn = phn

    def list_of_numbers(self):
        if isinstance(self.phn, list):
            return self.list_phoneno_formater(self.phn)
        elif isinstance(self.phn, long):
            return self.int_phoneno_formater(self.phn)
        elif isinstance(self.phn, int):
            return self.int_phoneno_formater(self.phn)
        elif isinstance(self.phn, str):
            return self.str_phoneno_formater(self.phn)
        else:
            return "Wrong format"

    def list_phoneno_formater(self, the_list):
        valid_list = []
        for number in the_list:
            if self.phone_no_validator(number) is not False:
                valid_list.append(self.phone_no_validator(number))
        if not valid_list:
            return []
        else:
            return valid_list

    def int_phoneno_formater(self, the_int):
        valid_list = []
        if self.phone_no_validator(the_int) is not False:
            valid_list.append(self.phone_no_validator(the_int))
            return valid_list
        else:
            return []

    def str_phoneno_formater(self, the_str):
        valid_list = []
        the_str.replace(' ', "")
        if self.phone_no_validator(the_str) is not False:
            valid_list.append(self.phone_no_validator(the_str))
            return valid_list

        else:
            return []

    def phone_no_validator(self, phnno):
        try:
            phnno = str(phnno)
            if phnno[0] != "+":
                int(phnno)

        except ValueError:
            return False
        phnno.replace(' ', "")
        length = len(phnno)
        if length < 9:
            return False
        elif length == 9:
            if phnno[:1] == "0":
                print phnno, "has less values"
                return False

            return "%s%s" % ("+254", phnno)
        elif length == 10:
            return "%s%s" % ("+254", phnno[1:])
        elif length == 12:
            if phnno[:3] == "254":
                return "%s%s" % ("+", phnno)
            else:
                return False
        elif length == 13:
            if phnno[:4] == "+254":
                return phnno
            else:
                return False
        else:
            return False
        
        





