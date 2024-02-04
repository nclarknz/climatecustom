#
# Nathan Clark
#
import sys
import logging
#from . import constants
#import importlib_resources
import tinytuya
import json
import sys

logging.basicConfig(level=logging.INFO)


class IRAirCon(object):
    """Initialises a IR Air Con, by taking a device ID and ip addr and other setup Info."""

    def __init__(self, deviceID, ipaddr,apiregion,apikey,apisecret,remoteID):

        self.deviceID = deviceID
        self._ipaddr = ipaddr
        self._apiRegion = apiregion
        self._apiKey = apikey
        self._apiSecret = apisecret
        self.remoteID = remoteID

    def connect(self):

         self.c = c = tinytuya.Cloud(self._apiRegion,self._apiKey, self._apiSecret,self.remoteID)
        

    def _send_msg(self, message):
        """This is the only interface to the send the command to the connection."""
        try:
           #commands2 = {"commands": [{"code": "switch", "value": "True"}]}
           sendmsg = self.c.cloudrequest( '/v1.0/devices/' + self.remoteID + '/commands','POST',message )
        except Exception:
            serror = "Error: "
            sys.stderr.write(serror)
        # Now wait for reply
        return sendmsg


    def getstatusall(self):
        remote_list = self.c.cloudrequest( '/v2.0/infrareds/' + self.deviceID + '/remotes/' + self.remoteID + '/ac/status' )
        result = remote_list["result"]
        return result
    
    def getstatuspower(self):
        remote_list = self.c.cloudrequest( '/v2.0/infrareds/' + self.deviceID + '/remotes/' + self.remoteID + '/ac/status' )
        result2 = remote_list['result']['power']
        return result2
    
    def getstatustemp(self):
        remote_list = self.c.cloudrequest( '/v2.0/infrareds/' + self.deviceID + '/remotes/' + self.remoteID + '/ac/status' )
        result2 = remote_list['result']['temp']
        return result2
    
    def getstatusfan(self):
        remote_list = self.c.cloudrequest( '/v2.0/infrareds/' + self.deviceID + '/remotes/' + self.remoteID + '/ac/status' )
        result2 = remote_list['result']['wind']
        if result2 == 0:
            msg = "low"
        elif result2 == 1:
            msg = "mid"
        elif result2 == 2:
            msg = "high"
        elif result2 == 3:
            msg = "auto"
        else:
            msg = "Error Converting value "
        return msg
    
    def getstatusmode(self):
        remote_list = self.c.cloudrequest( '/v2.0/infrareds/' + self.deviceID + '/remotes/' + self.remoteID + '/ac/status' )
        result2 = remote_list['result']['mode']
        if result2 == 0:
            msg = "dehumidification"
        elif result2 == 1:
            msg = "cold"
        elif result2 == 2:
            msg = "auto"
        elif result2 == 3:
            msg = "fan"
        elif result2 == 4:
            msg = "heat"
        else:
            msg = "Error Converting value "
        return msg


    def set_target_temp(self, temperature):
        """
        Sets the target temperature, to the requested int
        """
        if 35 < temperature < 18:
            logging.info("Refusing to set temp outside of allowed range")
            return False
        else:
            data = {}
            data['code'] = 'temp'
            data['value'] = temperature
            cmds = {}
            cmds['commands'] = [data]
            self._send_msg(cmds)
            return True
        
    def turnOn(self):
        """
        Turns the unit on
        """
        msgsend = {"commands": [{"code": "switch", "value": "True"}]}
        self._send_msg(msgsend)
        return True
    
    def turnOff(self):
        """
        Turns the unit on
        """
        msgsend = {"commands": [{"code": "switch", "value": "False"}]}
        self._send_msg(msgsend)
        return True
    
    def switchToCool(self):
        """
        Turns the unit to cool mode
        """
        msgsend = {"commands": [{"code": "mode", "value": "cold"}]}
        self._send_msg(msgsend)
        return True
    
    def switchToHeat(self):
        """
        Turns the unit to cool mode
        """
        msgsend = {"commands": [{"code": "mode", "value": "heat"}]}
        self._send_msg(msgsend)
        return True
    
    def switchToFan(self):
        """
        Turns the unit to cool mode
        """
        msgsend = {"commands": [{"code": "mode", "value": "wind_dry"}]}
        self._send_msg(msgsend)
        return True
    
    def switchToDeHumid(self):
        """
        Turns the unit to cool mode
        """
        msgsend = {"commands": [{"code": "mode", "value": "dehumidification"}]}
        self._send_msg(msgsend)
        return True
    
    def changeFanSpeed(self, fanmode):
        if fanmode == "low":
            msgsend = {"commands": [{"code": "fan", "value": "low"}]}
        elif fanmode == "mid":
            msgsend = {"commands": [{"code": "fan", "value": "mid"}]}
        elif fanmode == "high":
            msgsend = {"commands": [{"code": "fan", "value": "high"}]}
        elif fanmode == "auto":
            msgsend = {"commands": [{"code": "fan", "value": "auto"}]}
        else:
            sys.stderr.write("Please use low, mid, high or auto as options")
            return False
        
        self._send_msg(msgsend)
        return True

    