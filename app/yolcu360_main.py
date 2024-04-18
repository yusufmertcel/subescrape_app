import datetime
import json
import os
from yolcu360 import WSCaller
from open_yolcu import DataExtract

class Main:
    def __init__(self, input_type, hour_db=2, day_db=0) -> None:
        self.input_type = input_type
        if input_type == "console":
            self.hour, self.day = self.getConsoleInput()
        elif input_type == "dashboard":
            self.hour, self.day = hour_db, day_db
        else:
            self.hour, self.day = hour_db, day_db

        self.gunler = [(1, "1gunluk"), (7, "7gunluk"), (30, "30gunluk")]
        self.start_date = datetime.datetime.now() + datetime.timedelta(days=self.day)


        with open("app/garenta_sube.json", "r") as f:
            self.loc_dict = json.load(f)

       
    
    def getConsoleInput(self):
        while True:
            hour = int(input("Kac saat sonrasindan baslamak istiyorsun? En az 2 saat sonrasını seçmelisiniz."))
            if hour >= 2:
                break
        while True:
            day = int(input("Kac gun sonrasından baslamak istiyorsun? Aynı gün için 0 yazmalısınız."))
            if day >= 0:
                break
        return hour, day
        

    def apiCall_fileRead(self, loc_name):
        is_API_called = True
        for gun in self.gunler:
            print(f"{loc_name}/yolcu360_{gun[1]}.json")
            if os.path.exists(f"{loc_name}/yolcu360_{gun[1]}.json"):
                with open(f"app/{loc_name}/yolcu360_{gun[1]}.json", "r") as f:
                    json_data = json.load(f)
                    try:
                        last_updated = json_data["results"][0]["searchRequest"]["checkInDateTime"].split(".")[0]
                        last_updated = datetime.datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S")
                        below_limit = last_updated + datetime.timedelta(days=-5)
                        upper_limit = last_updated + datetime.timedelta(days=5)
                        print(last_updated)
                    except KeyError and TypeError:
                        last_updated = None
                    if last_updated is None or upper_limit <= self.start_date or  below_limit >= self.start_date: # 8 Nisan bugün 15 Nisana request atılmış daha önceden biz 10 ve 20 Nisan arasına request atamıyoruz
                        print("API cagrisi yapilacak.")
                    else:
                        is_API_called = False
                        print("API cagrisi yapılmadı. {last_updated} tarihindeki veriler kullanılacak. Cunku {last_updated} tarihine yapilan cagri {start_date} tarihinden daha güncel".format(last_updated=last_updated, start_date=self.start_date))
        return is_API_called

    def apiCall(self, loc_name, apiCallBool, fname):
        web_service_caller = WSCaller(self.gunler)
        web_scraper = DataExtract(fname, self.gunler)
        for gun in self.gunler:
            print(gun[1])
            end_date = self.start_date + datetime.timedelta(days=gun[0])
            pickup_date = (self.start_date + datetime.timedelta(hours=self.hour)).strftime("%Y-%m-%dT%H:00:00")
            dropoff_date = (end_date + datetime.timedelta(hours=self.hour)).strftime("%Y-%m-%dT%H:00:00")
            print(pickup_date, dropoff_date)
            print(self.loc_dict[loc_name])
            
            
            if apiCallBool:
                print("API cagrisi yapıldı.")
                web_service_caller.get_data(gun[1], pickup_date, dropoff_date, self.loc_dict[loc_name], loc_name)

        brand_model_TO_sippcode = web_service_caller.sippCodes(loc_name)

        return web_scraper.convert_excel(brand_model_TO_sippcode, loc_name)
    
    def main(self, office_id, filename):
        if self.input_type == "console":
            key = list(self.loc_dict.keys())[office_id] # hangi şehirdeki ofislerin verilerini almak istiyorsun?
            print(key)
        elif self.input_type == "dashboard":
            key = office_id

        apiCallBool = self.apiCall_fileRead(key) # API cagrisi yapilacak mi?

        return self.apiCall(key, apiCallBool, filename)



if __name__ == "__main__":
    print("yolcu360_main.py is running.")
    # arayüzden saat, gün, lokasyon, seçimi yapılacak
    # Kaç saat sonrasından başlamak istiyorsun?
    main_obj = Main("console")
    while True:
            g_filename = input("Rapor dosyasının ismini giriniz(.xls veya .xlsx): ")
            if g_filename.split('.')[1] in ("xlsx", "xls"):
                break


    main_obj.main(1, g_filename)


       
        

    



