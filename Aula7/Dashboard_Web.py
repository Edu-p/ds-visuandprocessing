
import pandas    as pd
import streamlit as st
import numpy     as np
import folium
import geopandas
import plotly.express as px

from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

from datetime import datetime

st.set_page_config( layout='wide' )

@st.cache( allow_output_mutation=True ) #o '@' a gente chama de decorador e esse st.cache serve para nos lermos o arquivo direto da memoria e nao do disco, no caso o dataset abaixo, o allow_.... é para que esse dataset possa mudar ao longo do codigo, isso agiliza a manipulaçao desse dataset
def get_data( path ):
    data = pd.read_csv( path )
    return data

@st.cache( allow_output_mutation=True )
def get_geofile( url ):
    geofile = geopandas.read_file( url ) # lib que a glr do pandas desenvolveu pra trabalhar com localizaçao
    return geofile

def set_feature( data ):

    # add new features
    data['price_m2'] = data['price'] / (data['sqft_lot'] / 10.764)

    return data

def overview_data( data ): #nao retorna nada, so vai plotar as tabelas
    st.sidebar.title('Table Options')
    f_attributes = st.sidebar.multiselect('Enter columns', data.columns)
    f_zipcode = st.sidebar.multiselect('Enter zipcode',
                                       data['zipcode'].unique())
    st.title('Data Overview')

    # data filter
    if ((f_zipcode != []) & (f_attributes != [])):
        data = data.loc[
            data['zipcode'].isin(f_zipcode), f_attributes]  # apareer o que foi selecionado, so se ele selecionou

    elif ((f_zipcode != []) & (f_attributes == [])):
        data = data.loc[data['zipcode'].isin(f_zipcode), :]

    elif ((f_zipcode == []) & (f_attributes != [])):
        data = data.loc[:, f_attributes]
    else:
        data = data.copy()

    st.dataframe(data)

    # st.write( data.head(7) )

    c1, c2 = st.beta_columns((1, 1))  # isso é para deixar os graficos dispostos um do lado do outro
    # Avarage metrics

    df1 = data[['id', 'zipcode']].groupby('zipcode').count().reset_index()
    df2 = data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    df3 = data[['sqft_living', 'zipcode']].groupby('zipcode').mean().reset_index()
    df4 = data[['price_m2', 'zipcode']].groupby('zipcode').mean().reset_index()

    # merge metrics

    m1 = pd.merge(df1, df2, on='zipcode', how='inner')  # abstrair inner por agora
    m2 = pd.merge(m1, df3, on='zipcode', how='inner')
    df = pd.merge(m2, df4, on='zipcode', how='inner')

    df.columns = ['zipcode', 'total houses', 'price', 'sqft living', 'price/m2']  # rename coluns

    c1.header('Avarage values')
    c1.dataframe(df, height=600)

    # st.write( df.head(7) )

    # Descriptive Statistic
    num_attributes = data.select_dtypes(
        include=['int64', 'float64'])  # selecionando todos as colunas que forem desses tipos
    media = pd.DataFrame(num_attributes.apply(np.nanmean))
    mediana = pd.DataFrame(num_attributes.apply(np.median))
    std = pd.DataFrame(num_attributes.apply(np.nanstd))

    max_ = pd.DataFrame(num_attributes.apply(np.max))
    min_ = pd.DataFrame(num_attributes.apply(np.min))

    df8 = pd.concat([max_, min_, media, mediana, std], axis=1).reset_index()

    df8.columns = ['attributes', 'max', 'min', 'mean', 'median', 'std']

    # st.write( num_attributes['price'].max() )

    c2.header('Descriptive analysis')
    c2.dataframe(df8, height=600)

    return None

def portifolio_density( data ):
    st.title('Region Overview')
    c1, c2 = st.beta_columns((1, 1))

    c1.header('Portfolio Density')

    df = data.sample(100)  # pegar uma amostra

    # Base Map - Folium( map lib )
    density_map = folium.Map(location=[data['lat'].mean(), data['long'].mean()])

    maker_cluster = MarkerCluster().add_to(density_map)
    for name, row in df.iterrows():  # deixar meu dataframe interativo, row cada linha do dataset
        folium.Marker([row['lat'], row['long']],
                      popup='Sold R$ on: {0}., {1} bedrooms'.format(row['price'],
                                                                    row['bedrooms'],
                                                                    )
                      ).add_to(maker_cluster)

    with c1:
        folium_static(density_map)


    return None

def commercial_distribution( data ):
    # Avarage Price per year

    st.sidebar.title('Commercial Options')
    st.title('Commercial atributes')

    data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')

    # Filters
    min_year_built = int(data['yr_built'].min())
    max_year_built = int(data['yr_built'].max())

    st.sidebar.subheader('Select Max Year Built')
    f_year_built = st.sidebar.slider('Year Built', min_year_built,
                                     max_year_built,
                                     min_year_built)

    st.header('Avarage Price per Year Built')

    df1 = data.loc[data['yr_built'] < f_year_built]

    df1 = df1[['yr_built', 'price']].groupby('yr_built').mean().reset_index()

    fig = px.line(df1, x='yr_built', y='price')

    st.plotly_chart(fig, use_container_width=True)

    # Avarage Price per Day

    st.header('Avarage Price per day')
    st.sidebar.subheader('Select max Date')

    # Filters
    min_date = datetime.strptime(data['date'].min(), '%Y-%m-%d')
    max_date = datetime.strptime(data['date'].max(), '%Y-%m-%d')

    f_date = st.sidebar.slider('Date', min_date, max_date, min_date)

    # data filtering
    # st.write( type(f_date) )
    data['date'] = pd.to_datetime(data['date'])

    df = data.loc[data['date'] < f_date]
    df = data[['date', 'price']].groupby('date').mean().reset_index()
    # plot
    fig = px.line(df, x='date', y='price')

    st.plotly_chart(fig, use_container_width=True)

    # ==================
    # Histogram
    # ==================

    st.header('Price Distribution')
    st.sidebar.subheader('Select Max Price')

    # data filtering
    min_price = int(data['price'].min())
    max_price = int(data['price'].max())
    avg_price = int(data['price'].mean())

    f_price = st.sidebar.slider('Price', min_price, max_price, avg_price)

    df3 = data.loc[data['price'] < f_price]

    # data plot

    fig = px.histogram(df3, x='price', nbins=50)  # quantas barras eu qeuro no meu histograma

    st.plotly_chart(fig, use_container_width=True)

    return None

def attributes_distribution( data ):
    # ==================
    # Real state distribution by physic categories
    # ==================

    st.sidebar.title('Attributes Options')
    st.title('House Attributes')

    # filters
    f_bedrooms = st.sidebar.selectbox('Max number of bedrooms',
                                      sorted(set(data['bedrooms'].unique())))
    f_bathrooms = st.sidebar.selectbox('Max number of bathrooms',
                                       sorted(set(data['bathrooms'].unique())))

    c1, c2 = st.beta_columns(2)

    # House per bedrooms
    c1.header('houses per bedrooms')
    df = data[data['bedrooms'] < f_bedrooms]
    fig = px.histogram(df, x='bedrooms', nbins=15)
    c1.plotly_chart(fig, use_container_width=True)

    # House per bathrooms
    c2.header('houses per bathrooms')
    df = data[data['bathrooms'] < f_bathrooms]
    fig = px.histogram(df, x='bathrooms', nbins=15)
    c2.plotly_chart(fig, use_container_width=True)

    # Filters
    f_floors = st.sidebar.selectbox('Max number of floors',
                                    sorted(set(data['floors'].unique())))

    f_waterview = st.sidebar.checkbox('Only Houses with Water View')

    c1, c2 = st.beta_columns(2)

    # House per floors
    c1.header('Houses per floor')
    df = data[data['floors'] < f_floors]
    # plot
    fig = px.histogram(df, x='floors', nbins=15)
    c1.plotly_chart(fig, use_container_width=True)

    # House per waterview
    c2.header('Houses with water view')
    if f_waterview:
        df = data[data['waterfront'] == 1]
    else:
        df = data.copy()

    fig = px.histogram(df, x='waterfront', nbins=10)
    c2.plotly_chart(fig, use_container_width=True)

    return None

if __name__ == '__main__':
    #ETL
    # DAta extraction

    path = '../datasets/kc_house_data.csv'
    data = get_data(path)

    # TRansformation

    data = set_feature( data )

    overview_data( data )

    portifolio_density( data )

    commercial_distribution( data )

    attributes_distribution( data )

    # LOading









