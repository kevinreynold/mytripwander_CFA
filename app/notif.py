import json
import requests

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'key=AAAAWN_fPMk:APA91bGnOj0MsFIWy5W4XbGAeeAghOLaLG1NICp0LAdvdpWcjERANcSqpv9kMPJp2p-AyxKhZXkIQLn7g19Etve8CxEgl-zIUAAtNkgDNfpTVxhajRqOqpKm0z9bRGY-LZaAzYfY1AHQ'
}

device_token = "eay5Vd5HTtQ:APA91bGeQan6URkfE6EOVrQQY9pGfKCXTzgn5Du_4WEqvsBOyttZpwwQlbnRgfDgOKHTfoaabMoZxfzFWJLNfsBZgP96Beza9Jgx9ZswdQlkhkic4oJFNWD_7NEBNkuNU-yTEQqcktHY"
notif_data = {
 "to" : device_token,
 "notification" : {
     "title" : "Your itinerary is ready",
     "body": "6 Days Trip"
 },
}

url = "https://fcm.googleapis.com/fcm/send"
data = requests.post(url, json=notif_data, headers=headers)
