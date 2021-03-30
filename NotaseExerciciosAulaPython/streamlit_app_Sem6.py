import pandas    as pd
import streamlit as st

st.set_page_config( layout='wide' ) # para que nossos elementos tenham a maxima largura possivel
@st.cache( allow_output_mutation=True ) #o '@' a gente chama de decorador e esse st.cache serve para nos lermos o arquivo direto da memoria e nao do disco,, no caso o dataset abaixo, o allow_.... é para que esse dataset possa mudar ao longo do codigo, isso agiliza a manipulaçao desse dataset

def get_data( path ):
    data = pd.read_csv( path )
    return data

# get data
path = '../datasets/kc_house_data.csv'
data = get_data( path )

# add new features
data['price_m2'] = data['price'] / (data['sqft_lot']/10.764)

#===============
# Data overview
#===============
f_attributes = st.sidebar.multiselect( 'Enter columns', data.columns )
f_zipcode = st.sidebar.multiselect( 'Enter zipcode',
                                    data['zipcode'].unique() )
st.title( 'Data Overview' )

if( ( f_zipcode!= [] ) & ( f_attributes != [] )):
    data = data.loc[ data['zipcode'].isin( f_zipcode ), f_attributes ] # apareer o que foi selecionado, so se ele selecionou

elif(  ( f_zipcode!= [] ) & ( f_attributes == [] ) ):
    data = data.loc[data['zipcode'].isin(f_zipcode), :]

elif(  ( f_zipcode== [] ) & ( f_attributes != [] ) ):
    data = data.loc[:, f_attributes]
else:
    data = data.copy()

# st.write( f_attributes )
# st.write( f_zipcode )


st.write( data.head(7) )


