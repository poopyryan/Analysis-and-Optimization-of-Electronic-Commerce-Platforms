import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.io as pio

def two_data_comparison_visualisation(first_df, second_df):
    plt.figure(figsize=(12, 6))
    sns.histplot(first_df['Order Item Discount Rate'], color='blue', label='Real Data', kde=True, stat='density', bins=30)
    sns.histplot(second_df['discount_rate'], color='orange', label='Synthetic Data', kde=True, stat='density', bins=30)
    plt.title('Comparison of Real and Synthetic Discount Rates')
    plt.xlabel('Discount Rate')
    plt.ylabel('Density')
    plt.legend()
    plt.show()

def churn_rate_visualisation(df, x_name, x_label):
    return px.bar(
    df.reset_index(),
    x=x_name,
    y='churned',
    labels={'churned': 'Churn Rate (%)', x_name: x_label},
    title='Churn Rate by ' + x_label
    )

def visualisation_show(visualisation):
    visualisation.show()
    
