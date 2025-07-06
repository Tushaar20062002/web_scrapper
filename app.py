from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup
import requests
from io import BytesIO
import base64

app = Flask(__name__)
sns.set(style="whitegrid")

chart_types = [
    'Bar Chart', 'Pie Chart', 'Histogram', 'Line Chart',
    'Bubble Chart', 'Scatter Plot', 'Heatmap', 'Box Plot'
]

def scrape_data():
    url = 'https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'wikitable'})
    df = pd.read_html(str(table))[0]
    df = df[['Location', 'Population', '% of world', 'Date']]
    df.columns = ['Country', 'Population', 'World_Percent', 'Date']
    df = df.head(10)
    df['Population'] = df['Population'].astype(str).str.replace(r'[^0-9]', '', regex=True).astype(float)
    df['World_Percent'] = df['World_Percent'].astype(str).str.replace('%', '', regex=False).astype(float)
    df['Population_Millions'] = df['Population'] / 1_000_000
    return df

def generate_chart(df, chart_type):
    plt.figure(figsize=(10, 6))
    if chart_type == 'Bar Chart':
        sns.barplot(x='Population_Millions', y='Country', data=df, palette='viridis')
        plt.title('Population by Country (Millions)')
    elif chart_type == 'Pie Chart':
        plt.pie(df['World_Percent'], labels=df['Country'], autopct='%1.1f%%')
        plt.title('World Population Share')
    elif chart_type == 'Histogram':
        plt.hist(df['Population_Millions'], bins=5, color='orange')
        plt.title('Population Histogram')
        plt.xlabel('Population (Millions)')
    elif chart_type == 'Line Chart':
        plt.plot(df['Country'], df['Population_Millions'], marker='o')
        plt.title('Line Chart - Population')
    elif chart_type == 'Bubble Chart':
        plt.scatter(df['Country'], df['World_Percent'], s=df['Population_Millions']*10, alpha=0.6)
        plt.title('Bubble Chart: Country vs World %')
    elif chart_type == 'Scatter Plot':
        sns.scatterplot(x='Population_Millions', y='World_Percent', hue='Country', data=df, s=100)
        plt.title('Scatter Plot: Pop vs % of World')
    elif chart_type == 'Heatmap':
        sns.heatmap(df[['Population', 'World_Percent']].corr(), annot=True, cmap='coolwarm')
        plt.title('Correlation Heatmap')
    elif chart_type == 'Box Plot':
        sns.boxplot(y=df['Population_Millions'])
        plt.title('Box Plot: Population')
    else:
        return None

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return chart_base64

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    selected_chart = request.form.get('chart') or 'Bar Chart'
    df = scrape_data()
    chart_image = generate_chart(df, selected_chart)
    table_html = df.to_html(classes='data', index=False)
    return render_template('interactive_dashboard.html',
                           table=table_html,
                           chart=chart_image,
                           chart_types=chart_types,
                           selected_chart=selected_chart)

if __name__ == '__main__':
    app.run(debug=True)
