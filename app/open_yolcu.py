import json
import pandas as pd
import openpyxl
import sys





class DataExtract:
    def __init__(self, filename, gunler) -> None:
        self.filepath = filename
        try:
            self.wb = openpyxl.Workbook()
            self.wb.save(self.filepath)
        except PermissionError:
            print("Please close the excel file")
            sys.exit()
        self.columns = ["checkInDate","checkInOffice", "checkOutOffice", "brand", "brand_id", "model", "model_id", "sippCode", "vendor", "vendor_id", "period", "price_currency", "price_amount"]
        self.gunler = gunler #[(1, "1gunluk"), (7, "7gunluk"), (30, "30gunluk")]

    def convert_excel(self, sippcodes_dict, loc_name):
        dfs = [None, None, None]
        for idx, gun in enumerate(self.gunler):
            with open(f"app/{loc_name}/yolcu360_{gun[1]}.json", "r") as f:
                json_data = json.load(f)
            try:
                count = json_data["count"]
                car_data = json_data["results"]

                price_dict, period = self.get_car_prices(car_data, sippcodes_dict)
                
                df = pd.DataFrame.from_dict(price_dict, orient="index", columns=self.columns)
                df.sort_values(by=["vendor_id"], inplace=True)
                #print(df.head())
                # add dataframes to list
                dfs[idx] = df
                try:
                    with pd.ExcelWriter(self.filepath, engine="openpyxl", mode="a") as writer:
                        df.to_excel(writer, sheet_name=f"{period} Gunluk",index=True, header=True)
                except PermissionError:
                    print("Please close the excel file")
                    break
            except KeyError:
                continue
        print(len(dfs))
        return dfs

    def get_car_prices(self, car_data, sippCodes):
        price_dict = {car: [] for car in range(0, len(car_data))}
        for idx, car in enumerate(car_data): 
            car_detail = car["details"]["car"]
            appointment = car_detail["appointment"]
            checkInDateTime = appointment["checkInDateTime"].split('.')[0]
            checkInOffice, checkOutOffice = appointment["checkInOffice"]["address"]["adm2"], appointment["checkOutOffice"]["address"]["adm2"]
            brand, brand_id = car_detail["brand"]["name"], car_detail["brand"]["id"] 
            model, model_id = car_detail["model"]["name"],  car_detail["model"]["id"]

            try:
                if len(car_detail["sippCode"]) == 4:
                    sippCode = car_detail["sippCode"]
                else:
                    sippCode = sippCodes[f"{brand_id}+{model_id}"]
            except KeyError:
                if f"{brand_id}+{model_id}" in sippCodes.keys():
                    sippCode = sippCodes[f"{brand_id}+{model_id}"]
                else:
                    sippCode = "N/A"

            vendor = car_detail["vendor"]["displayName"]
            vendor_id = car_detail["vendor"]["id"]
            period = car["period"]["amount"]
            price = car["pricing"]["payment"]
            price_currency = price["currency"]
            price_amount = price["total"]["amount"]["amount"]
            price_amount = price_amount/100.0
            print(price_amount)

            price_dict[idx] = [checkInDateTime, checkInOffice, checkOutOffice, brand, brand_id, model, model_id, sippCode, vendor, vendor_id, period, price_currency, price_amount]
            print(checkInDateTime, checkInOffice, checkOutOffice, brand, brand_id, model, model_id, sippCode, vendor, vendor_id, period, price_currency, price_amount)
        return price_dict, period