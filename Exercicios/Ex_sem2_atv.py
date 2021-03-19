import pandas as pd
import datetime as date

dataAtv2 = pd.read_csv('../datasets/kc_house_data.csv')

# Pergunta 1:

dataAtv2['date'] = pd.to_datetime(dataAtv2['date'])

dataAtv2['house_age'] = 'date'

diaD = pd.Timestamp("2015-01-01")

dataAtv2.loc[dataAtv2['date'] >= diaD, 'house_age'] = 'new_house'
dataAtv2.loc[dataAtv2['date'] < diaD, 'house_age'] = 'old_house'

#print(dataAtv2[['date','house_age']].head(40))

# Pergunta 2

dataAtv2['dormitory_type'] = 'standard'

dataAtv2.loc[dataAtv2['bedrooms'] == 1, 'dormitory_type'] = 'studio'
dataAtv2.loc[dataAtv2['bedrooms'] == 2, 'dormitory_type'] = 'apartament'
dataAtv2.loc[dataAtv2['bedrooms'] > 2, 'dormitory_type'] = 'house'

#print(dataAtv2[['price','dormitory_type']][dataAtv2['bedrooms'] == 1].head(30))

# Pergunta 3

dataAtv2['condition_type'] = 'standard'

dataAtv2.loc[dataAtv2['condition'] <= 2, 'condition_type'] = 'bad'
dataAtv2.loc[(dataAtv2['condition'] == 3) | (dataAtv2['condition'] == 4), 'condition_type'] = 'regular'
dataAtv2.loc[dataAtv2['condition'] == 5, 'condition_type'] = 'good'

#print(dataAtv2[['price','condition_type','condition']][dataAtv2['condition_type'] == 'bad'].head(30))

# Pergunta 4

dataAtv2['condition'] = dataAtv2['condition'].astype( str )

#print(dataAtv2.dtypes)

# Pergunta 5

cols = ['sqft_living15','sqft_lot15']

dataAtv2 = dataAtv2.drop(cols,axis=1)

print(dataAtv2.columns)












