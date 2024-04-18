import json
import requests
import datetime
import os


class WSCaller:
    def __init__(self, gunler) -> None:
        self.url = "https://api2.yolcu360.com/api/v1/search-api/search/point/"
        self.token = "Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJvcmdhbml6YXRpb25zIjpbNjgzNl0sImFub24iOnRydWUsImlzcyI6InlvbGN1MzYwLmNvbSIsInN1YiI6ImFuLWE0MTZiYWUyLWJmN2MtNDM5Ni05N2JhLTIzOTlkMGY3MGMxYyIsImV4cCI6MTcxMzA5NDE3NCwiaWF0IjoxNzEyNDg5Mzc0LCJqdGkiOiI4MzFkNWVhNi1iZjA4LTQ3ZDEtOWMwZS05OWU0YjliNGJiNTEifQ.UFkIR6SKsh4kk7y70uUUEQAyQjwMN-7mIH1N5BAZu30Krly1Vupzn4VkM4HK4_OLdJk79s6qEn24l9oM1iL-7A"
        self.gunler = gunler
        self.brand_model_TO_sippcode = {}
    
    def get_data(self, interval, start_date, end_date, loc, loc_name):
        data = {
            "age": "30-65",
            "checkInDateTime": start_date,
            "checkInLocation": {
                "lat": loc[0],
                "lon": loc[1]
            },
            "lat": loc[0],
            "lon": loc[1],
            "checkOutDateTime": end_date,
            "checkOutLocation": {
                "lat": loc[0],
                "lon": loc[1]
            },
            "country": "TR",
            "currency": "TRY",
            "language": "tr",
            "organizationId": 6836,
            "paymentType": "creditCard",
            "period": "daily"
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token,
            "Connection": "keep-alive"
        }

        re = requests.post(self.url, data=json.dumps(data), headers=headers)
        json_data = re.json()
        if not os.path.exists(loc_name):
            os.makedirs(loc_name)
        with open(f"app/{loc_name}/yolcu360_{interval}.json", "w") as f:
            json.dump(json_data, f, indent=4)
    
    def sippCodes(self, loc_name):
        for gun in self.gunler:
            with open(f"app/{loc_name}/yolcu360_{gun[1]}.json", "r") as f:
                json_data = json.load(f)
            results = json_data["results"] if json_data["results"] is not None else []
            for idx, car in enumerate(results): 
                car_detail = car["details"]["car"]
                brand_id = car_detail["brand"]["id"]
                model_id = car_detail["model"]["id"]

                if f"{brand_id}+{model_id}" not in self.brand_model_TO_sippcode.keys() and "sippCode" in car_detail.keys():
                    self.brand_model_TO_sippcode[f"{brand_id}+{model_id}"] = car_detail["sippCode"]
            
        with open(f"app/{loc_name}/SippCode.json", "w") as f:
            json_data = json.dump(self.brand_model_TO_sippcode, f, indent=4)
        return self.brand_model_TO_sippcode




