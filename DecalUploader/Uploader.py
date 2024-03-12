from rblxopencloud import User, AssetType
import requests, random, string
from time import sleep as sleepy
import xmltodict
from json import dumps

class DecalClass:
    def __init__(self, cookie:str, type:AssetType = AssetType.Decal) -> None:
        self.cookie = cookie
        self.creator = None
        self.keyId = None
        self.api_key = None
        self.asset_type = None
        self.__get_api_key__()

    def __get_api_key__(self):
        """Creates a API key and sets the self vers required"""
        if self.api_key: return self.api_key

        payload = {"cloudAuthUserConfiguredProperties": {"name": ''.join(random.choices(string.digits, k=2)),"description": "","isEnabled": True,"allowedCidrs": ["0.0.0.0/0"],"scopes": [{"scopeType": "asset","targetParts": ["U"],"operations": ["read", "write"]}]}}

        headers = {
            "content-type": "application/json",
            "X-Csrf-Token": requests.post('https://auth.roblox.com/v1/login', cookies={'.ROBLOSECURITY': self.cookie}).headers['x-csrf-token']
        }

        response = requests.post("https://apis.roblox.com/cloud-authentication/v1/apiKey", json=payload, headers=headers, cookies={'.ROBLOSECURITY': self.cookie}).json()
        #print(response)
        self.api_key = response['apikeySecret']
        self.keyId = response['cloudAuthInfo']['id']
        self.creator = User(requests.get('https://www.roblox.com/mobileapi/userinfo',cookies={'.ROBLOSECURITY':self.cookie}).json()['UserID'],
                                self.api_key)

    def delete_key(self):
        """Deletes the API key"""
        headers = {
            "content-type": "application/json",
            "X-Csrf-Token": requests.post('https://auth.roblox.com/v1/login', cookies={'.ROBLOSECURITY': self.cookie}).headers['x-csrf-token']
        }
        
        requests.delete(f'https://apis.roblox.com/cloud-authentication/v1/apiKey/{self.keyId}', headers=headers, cookies={'.ROBLOSECURITY': self.cookie}).json()

    def upload(self, file:bytes, title:str, description:str):
        """Attempts to upload decal

        Args:
            file (bytes): file data
            title (str): title of decal
            description (str): description of decal

        Returns:
            Asset: the asset of the decal
        """
        asset = self.creator.upload_asset(file, self.asset_type, title, description)

        sleepy(5)

        while True:
            try:
                if status:= asset.fetch_operation():
                    return status
            except Exception:
                sleepy(0.5)
            sleepy(0.2)

class Functions:
    def send_discord_message(webhook:str, name_value:str, decal_value, img_value):
        # sourcery skip: instance-method-first-arg-name
        decal_value = int(decal_value)
        img_value = int(img_value)
        library_url = f"https://www.roblox.com/library/{img_value}/"

        embed_data = {
            "title": "Uploaded",
            "url": library_url,
            "fields": [
                {"name": "File Name", "value": f"{name_value}"},
                {"name": "Decal Id", "value": f"{decal_value}"},
                {"name": "Image ID", "value": f"{img_value}"}
            ],
            "color": "16777215"
        }

        payload = {"embeds": [embed_data]}

        return requests.post(webhook, data=dumps(payload), headers={"Content-Type": "application/json"}).text

    def get_image_id(decal_id):
        # sourcery skip: instance-method-first-arg-name
        if not decal_id:
            return "no decal id passed???"
        url = f"https://assetdelivery.roblox.com/v1/asset/?id={decal_id}"
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return "failed to get Imgid"
            xml_data = xmltodict.parse(response.text)
            result_url = xml_data['roblox']['Item']['Properties']['Content']['url']
            return result_url.split("=")[1]
        except Exception as e:
            print(e)
            return "failed to get Imgid"

if __name__ == '__main__':
    input('you don\' run this file')
