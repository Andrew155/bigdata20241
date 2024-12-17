from fastapi import FastAPI, Query, Response
from datetime import datetime, timedelta
import json
import random
from typing import List, Dict 
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

COUNTRIES = [
            ("Afghanistan", "AF"), ("Albania", "AL"), ("Algeria", "DZ"),
            ("Andorra", "AD"), ("Angola", "AO"), ("Antigua and Barbuda", "AG"),
            ("Argentina", "AR"), ("Armenia", "AM"), ("Australia", "AU"),
            ("Austria", "AT"), ("Azerbaijan", "AZ"), ("Bahamas", "BS"),
            ("Bahrain", "BH"), ("Bangladesh", "BD"), ("Barbados", "BB"),
            ("Belarus", "BY"), ("Belgium", "BE"), ("Belize", "BZ"),
            ("Benin", "BJ"), ("Bhutan", "BT"), ("Bolivia", "BO"),
            ("Bosnia and Herzegovina", "BA"), ("Botswana", "BW"), ("Brazil", "BR"),
            ("Brunei Darussalam", "BN"), ("Bulgaria", "BG"), ("Burkina Faso", "BF"),
            ("Burundi", "BI"), ("Cambodia", "KH"), ("Cameroon", "CM"),
            ("Canada", "CA"), ("Cape Verde", "CV"), ("Central African Republic", "CF"),
            ("Chad", "TD"), ("Chile", "CL"), ("China", "CN"),
            ("Colombia", "CO"), ("Comoros", "KM"), ("Congo (Brazzaville)", "CG"),
            ("Congo (Kinshasa)", "CD"), ("Costa Rica", "CR"), ("Croatia", "HR"),
            ("Cuba", "CU"), ("Cyprus", "CY"), ("Czech Republic", "CZ"),
            ("Côte d'Ivoire", "CI"), ("Denmark", "DK"), ("Djibouti", "DJ"),
            ("Dominica", "DM"), ("Dominican Republic", "DO"), ("Ecuador", "EC"),
            ("Egypt", "EG"), ("El Salvador", "SV"), ("Equatorial Guinea", "GQ"),
            ("Eritrea", "ER"), ("Estonia", "EE"), ("Ethiopia", "ET"),
            ("Fiji", "FJ"), ("Finland", "FI"), ("France", "FR"),
            ("Gabon", "GA"), ("Gambia", "GM"), ("Georgia", "GE"),
            ("Germany", "DE"), ("Ghana", "GH"), ("Greece", "GR"),
            ("Grenada", "GD"), ("Guatemala", "GT"), ("Guinea", "GN"),
            ("Guinea-Bissau", "GW"), ("Guyana", "GY"), ("Haiti", "HT"),
            ("Honduras", "HN"), ("Hungary", "HU"), ("Iceland", "IS"),
            ("India", "IN"), ("Indonesia", "ID"), ("Iran", "IR"),
            ("Iraq", "IQ"), ("Ireland", "IE"), ("Israel", "IL"),
            ("Italy", "IT"), ("Jamaica", "JM"), ("Japan", "JP"),
            ("Jordan", "JO"), ("Kazakhstan", "KZ"), ("Kenya", "KE"),
            ("Korea (South)", "KR"), ("Kuwait", "KW"), ("Kyrgyzstan", "KG"),
            ("Lao PDR", "LA"), ("Latvia", "LV"), ("Lebanon", "LB"),
            ("Lesotho", "LS"), ("Liberia", "LR"), ("Libya", "LY"),
            ("Liechtenstein", "LI"), ("Lithuania", "LT"), ("Luxembourg", "LU"),
            ("Macedonia", "MK"), ("Madagascar", "MG"), ("Malawi", "MW"),
            ("Malaysia", "MY"), ("Maldives", "MV"), ("Mali", "ML"),
            ("Malta", "MT"), ("Mauritania", "MR"), ("Mauritius", "MU"),
            ("Mexico", "MX"), ("Moldova", "MD"), ("Monaco", "MC"),
            ("Mongolia", "MN"), ("Montenegro", "ME"), ("Morocco", "MA"),
            ("Mozambique", "MZ"), ("Myanmar", "MM"), ("Namibia", "NA"),
            ("Nepal", "NP"), ("Netherlands", "NL"), ("New Zealand", "NZ"),
            ("Nicaragua", "NI"), ("Niger", "NE"), ("Nigeria", "NG"),
            ("Norway", "NO"), ("Oman", "OM"), ("Pakistan", "PK"),
            ("Palestinian Territory", "PS"), ("Panama", "PA"), ("Papua New Guinea", "PG"),
            ("Paraguay", "PY"), ("Peru", "PE"), ("Philippines", "PH"),
            ("Poland", "PL"), ("Portugal", "PT"), ("Qatar", "QA"),
            ("Republic of Kosovo", "XK"), ("Romania", "RO"), ("Russian Federation", "RU"),
            ("Rwanda", "RW"), ("Saint Kitts and Nevis", "KN"), ("Saint Lucia", "LC"),
            ("Saint Vincent and Grenadines", "VC"), ("San Marino", "SM"),
            ("Sao Tome and Principe", "ST"), ("Saudi Arabia", "SA"), ("Senegal", "SN"),
            ("Serbia", "RS"), ("Seychelles", "SC"), ("Sierra Leone", "SL"),
            ("Singapore", "SG"), ("Slovakia", "SK"), ("Slovenia", "SI"),
            ("Somalia", "SO"), ("South Africa", "ZA"), ("South Sudan", "SS"),
            ("Spain", "ES"), ("Sri Lanka", "LK"), ("Sudan", "SD"),
            ("Suriname", "SR"), ("Swaziland", "SZ"), ("Sweden", "SE"),
            ("Switzerland", "CH"), ("Syrian Arab Republic", "SY"),
            ("Taiwan", "TW"), ("Tajikistan", "TJ"), ("Tanzania", "TZ"),
            ("Thailand", "TH"), ("Timor-Leste", "TL"), ("Togo", "TG"),
            ("Trinidad and Tobago", "TT"), ("Tunisia", "TN"), ("Turkey", "TR"),
            ("Uganda", "UG"), ("Ukraine", "UA"), ("United Arab Emirates", "AE"),
            ("United Kingdom", "GB"), ("United States of America", "US"),
            ("Uruguay", "UY"), ("Uzbekistan", "UZ"), ("Venezuela", "VE"),
            ("Vietnam", "VN"), ("Western Sahara", "EH"), ("Yemen", "YE"),
            ("Zambia", "ZM"), ("Zimbabwe", "ZW")
]
# Class CovidData
class CovidData:
    def __init__(self):
        self.base_data = {}  # Lưu dữ liệu quốc gia tích lũy
        self.last_updated = None  # Lưu thời gian cập nhật lần cuối
        self.simulated_time = datetime(2020, 1, 1)  # Bắt đầu từ 1/1/2020

    def generate_slug(self, country: str) -> str:
        return country.lower().replace(" ", "-")

    def advance_time(self):
        """Tăng thời gian giả lập lên 1 ngày"""
        self.simulated_time += timedelta(days=1)


    def generate_country_data(self, date: datetime, country_name: str,
                              country_code: str, previous_data: Dict = None) -> Dict:
        if previous_data is None:
            total_confirmed = random.randint(1000, 100000)
            total_deaths = int(total_confirmed * random.uniform(0.01, 0.05))
            total_recovered = int(total_confirmed * random.uniform(0.4, 0.8))
        else:
            total_confirmed = previous_data["TotalConfirmed"]
            total_deaths = previous_data["TotalDeaths"]
            total_recovered = previous_data["TotalRecovered"]

        new_confirmed = random.randint(0, 5000)
        new_deaths = int(new_confirmed * random.uniform(0.01, 0.03))
        new_recovered = int(new_confirmed * random.uniform(0.3, 0.7))

        total_confirmed += new_confirmed
        total_deaths += new_deaths
        total_recovered += new_recovered

        return {
            "Country": country_name,
            "CountryCode": country_code,
            "Slug": self.generate_slug(country_name),
            "NewConfirmed": new_confirmed,
            "TotalConfirmed": total_confirmed,
            "NewDeaths": new_deaths,
            "TotalDeaths": total_deaths,
            "NewRecovered": new_recovered,
            "TotalRecovered": total_recovered,
            "Date": self.simulated_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

    def generate_global_data(self, countries_data: List[Dict]) -> Dict:
        return {
            "NewConfirmed": sum(c["NewConfirmed"] for c in countries_data),
            "TotalConfirmed": sum(c["TotalConfirmed"] for c in countries_data),
            "NewDeaths": sum(c["NewDeaths"] for c in countries_data),
            "TotalDeaths": sum(c["TotalDeaths"] for c in countries_data),
            "NewRecovered": sum(c["NewRecovered"] for c in countries_data),
            "TotalRecovered": sum(c["TotalRecovered"] for c in countries_data),
            "Date": self.simulated_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

    def update_data(self) -> None:
        """Tự động cập nhật dữ liệu"""
        current_time = datetime.now()
        countries_data = []
        for country_name, country_code in COUNTRIES:
            previous_data = self.base_data.get(country_code)
            country_data = self.generate_country_data(current_time, country_name, country_code, previous_data)
            countries_data.append(country_data)
            self.base_data[country_code] = country_data

        global_data = self.generate_global_data(countries_data)
        self.last_updated = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.base_data["Global"] = global_data

        #Tăng thời gian giả lập
        self.advance_time()

# Khởi tạo CovidData và APScheduler
covid_data = CovidData()
scheduler = BackgroundScheduler()

def update_covid_data_job():
    """Job tự động cập nhật dữ liệu"""
    covid_data.update_data()
    print(f"Dữ liệu cập nhật lúc: {datetime.now()}")

# Định nghĩa job chạy mỗi 5 phút
scheduler.add_job(update_covid_data_job, "interval", seconds=5)
scheduler.start()

# Khởi tạo dữ liệu ban đầu ngay khi ứng dụng bắt đầu
covid_data.update_data()
print(f"Dữ liệu được khởi tạo lúc: {datetime.now()}")

# @app.get("/summary")
# async def get_covid_summary():
#     if not covid_data.last_updated:
#         return {"message": "Dữ liệu chưa sẵn sàng. Vui lòng chờ."}
#     return {
#         "Global": covid_data.base_data.get("Global"),
#         "Countries": list(covid_data.base_data.values()),
#         "LastUpdated": covid_data.last_updated
#     }

@app.get("/summary")
async def get_covid_summary():
    if not covid_data.last_updated:
        return {"message": "Data not ready. Please wait."}
    
    # Tạo response data
    response_data = {
        "Global": covid_data.base_data["Global"],
        "Countries": [
            data for code, data in covid_data.base_data.items()
            if code != "Global"
        ]
    }
    
    # Trả về JSON được format
    return Response(
        content=json.dumps(response_data, indent=2),
        media_type="application/json"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
