

import pandas as pd
import datetime as dt

pd.set_option ('display.max_columns', None)
pd.set_option ('display.float_format', lambda x: '%.2f' % x)
path = "/Users/ozanguner/PycharmProjects/DSMLBC/Ders_Notlari/3.hafta/egzersizlerim/online_retail.xlsx"
df = pd.read_excel (path, sheet_name="Year 2010-2011")

df.head ()

df.info ()


# Eksik değerler
df.isnull ().sum ()

# Verisetine bakış
df.describe ([0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])

# Miktarı veya fiyatı "O" dan küçük olan değerleri verisetinden çıkarttım
df = df[~((df["Quantity"] < 0) | (df["Price"] < 0))]

df.dropna(inplace=True)


df.shape


# essiz urun sayisi nedir?
df["Description"].nunique ()

# hangi urunden kacar tane var?
df["Description"].value_counts ()

# en cok siparis edilen urun hangisi?(Sıralı)
df.groupby ("Description")[["Quantity"]].sum ().sort_values (by="Quantity", ascending=False).head ()

# toplam kac fatura kesilmiştir?
df["Invoice"].nunique ()

# fatura basina ortalama kac para kazanilmistir? ,
# (iki değişkeni çarparak yeni bir değişken oluşturmak gerekmektedir)
df["TotalPrice"] = df["Quantity"] * df["Price"]
df.groupby ("Invoice")[["TotalPrice"]].mean ().sort_values (by="TotalPrice", ascending=False)

# en pahalı ürünler hangileri?
df.sort_values ("Price", ascending=False).head ()

# hangi ulkeden kac siparis geldi?
df["Country"].value_counts ().sort_values (ascending=False)

# hangi ulke ne kadar kazandırdı?
df.groupby ("Country")[["TotalPrice"]].sum ().sort_values (by="TotalPrice", ascending=False).head ()


df.head ()

df["InvoiceDate"].max ()

# Hesaplamalarla ilgili bir problem olmaması için maksimum tarihin 2 gün sonrası, bugünün tarihi olarak alındı.
today_date = dt.datetime (2011, 12, 11)

rfm = df.groupby ("Customer ID").agg ({"InvoiceDate": lambda day: (today_date - day.max ()).days,
                                       "Invoice": "nunique",
                                       "TotalPrice": "sum"})

rfm.columns = ["Recency", "Frequency", "Monetary"]

rfm["Recency_Score"] = pd.qcut (rfm["Recency"], q=5, labels=[5, 4, 3, 2, 1])
rfm["Frequency_Score"] = pd.qcut (rfm["Frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])
rfm["Monetary_Score"] = pd.qcut (rfm["Monetary"], q=5, labels=[1, 2, 3, 4, 5])

rfm["RFM_Score"] = rfm["Recency_Score"].astype ("str") + rfm["Frequency_Score"].astype ("str") + rfm[
    "Monetary_Score"].astype ("str")

seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[1-2][3-4]': 'At_Risk',
    r'[1-2]5': 'Cant_Loose',
    r'3[1-2]': 'About_to_Sleep',
    r'33': 'Need_Attention',
    r'[3-4][4-5]': 'Loyal_Customers',
    r'41': 'Promising',
    r'51': 'New_Customers',
    r'[4-5][2-3]': 'Potential_Loyalists',
    r'5[4-5]': 'Champions'
}
# Recency ve Frequency değerlerini aldım.
rfm["Segment"] = [row[0] + row[1] for row in rfm["RFM_Score"].values]

# Segmente ettim
rfm["Segment"] = rfm["Segment"].replace (seg_map, regex=True)

seg = rfm.groupby ("Segment").agg (["mean", "count"])

# Multiindex Sorununun Giderilmesi
seg.columns = [row[0] + "_" + row[1] if row[1] != "" else row[0] for row in seg.columns]

######################
# "Loyal Customers" sınıfına ait customer ID'leri seçerek excel çıktısını alınız.
######################

pd.DataFrame (rfm[rfm["Segment"] == "Loyal_Customers"].index).to_excel ("loyal_customers.xlsx")


seg.to_excel("segmentation_metrics.xlsx")

