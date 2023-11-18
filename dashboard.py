import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="MentaWell", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Patient EDA")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    os.chdir(r"C:\Users\lelethu\Desktop\dashboard")
    df = pd.read_csv("patient_data.csv", encoding = "ISO-8859-1")

    col1, col2 = st.columns((2))
df["symptom_onset_date"] = pd.to_datetime(df["symptom_onset_date"])

# Getting the min and max date 
startDate = pd.to_datetime(df["symptom_onset_date"]).min()
endDate = pd.to_datetime(df["symptom_onset_date"]).max()


with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["symptom_onset_date"] >= date1) & (df["symptom_onset_date"] <= date2)].copy()

st.sidebar.header("Choose your filter: ")
# Create for Region
region = st.sidebar.multiselect("Pick your Region", df["geographic_region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["geographic_region"].isin(region)]


    # Create for State
state = st.sidebar.multiselect("Pick the Province", df2["province"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["province"].isin(state)]


    # Create for City
city = st.sidebar.multiselect("Pick the Ethinicity",df3["ethnicity"].unique())

# Filter the data based on Region, State and City

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["geographic_region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["province"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["ethnicity"].isin(city)]
elif region and city:
    filtered_df = df3[df["geographic_region"].isin(region) & df3["ethnicity"].isin(city)]
elif region and state:
    filtered_df = df3[df["geographic_region"].isin(region) & df3["province"].isin(state)]
elif city:
    filtered_df = df3[df3["ethnicity"].isin(city)]
else:
    filtered_df = df3[df3["geographic_region"].isin(region) & df3["province"].isin(state) & df3["ethnicity"].isin(city)]

employment_status_df = filtered_df.groupby(by = ["employment_status"], as_index = False)["hospitalizations"].sum()

with col1:
    st.subheader("employment_status wise Hospitalizations")
    fig = px.bar(employment_status_df, x = "employment_status", y = "hospitalizations", text = ['{:,.2f}'.format(x) for x in employment_status_df["hospitalizations"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("Age wise Hospitalizations")
    fig = px.pie(filtered_df, values = "hospitalizations", names = "age", hole = 0.5)
    fig.update_traces(text = filtered_df["age"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(employment_status_df.style.background_gradient(cmap="Blues"))
        csv = employment_status_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "employment_status.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')
        
with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "geographic_region", as_index = False)["hospitalizations"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')

filtered_df["month_year"] = filtered_df["symptom_onset_date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["hospitalizations"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="hospitalizations", labels = {"Hospitalizations": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)


with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')


# Create a treem based on Region, category, sub-Category
st.subheader("Hierarchical view of Hospitalizations using TreeMap")
fig3 = px.treemap(filtered_df, path = ["province","gender","ethnicity"], values = "hospitalizations",hover_data = ["hospitalizations"],
                  color = "ethnicity")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Age wise Hospitalizations')
    fig = px.pie(filtered_df, values = "hospitalizations", names = "age", template = "plotly_dark")
    fig.update_traces(text = filtered_df["age"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Gender wise Hospitalizations')
    fig = px.pie(filtered_df, values = "hospitalizations", names = "gender", template = "gridon")
    fig.update_traces(text = filtered_df["gender"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)



import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Ethnicity Hospitalizations Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["geographic_region","province","education_level","gender","hospitalizations","distance_to_care_facilities","population_density"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise Ethnicity Table")
    filtered_df["month"] = filtered_df["symptom_onset_date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = filtered_df, values = "hospitalizations", index = ["ethnicity"],columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot
data1 = px.scatter(filtered_df, x = "hospitalizations", y = "distance_to_care_facilities", size = "age")
data1['layout'].update(title="Relationship between Hospitalizations and distance_to_care_facilities using Scatter Plot.",
                       titlefont = dict(size=20),xaxis = dict(title="hospitalizations",titlefont=dict(size=19)),
                       yaxis = dict(title = "distance_to_care_facilities", titlefont = dict(size=19)))
st.plotly_chart(data1,use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")