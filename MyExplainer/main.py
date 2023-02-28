import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from Explainer import ClassifierExplainer

def fig(fig, include_plotlyjs="cdn", full_html: bool = False) -> str:
    """Returns html for a plotly figure. By default the plotly javascript is not
    included but imported from the plotly cdn, and the full html wrapper is not included.

    Args:
        include_plotlyjs (bool, str): how to import the necessary javascript for the plotly
            fig. Defaults to 'cdn', which means the figure just links to javascript file
            hosted by plotly. If set to True then a 3MB javascript snippet is included.
            For other options check https://plotly.com/python-api-reference/generated/plotly.io.to_html.html
        full_html (bool): include <html>, <head> and <body> tags. Defaults to False.
    """
    return fig.to_html(include_plotlyjs=include_plotlyjs, full_html=full_html)

df=pd.read_csv('cbdata.csv',index_col=0)

df=df.reset_index(drop='index')

#splitting the data
X=df.drop(columns=['Prob_of_Success'])
y=df['Prob_of_Success' ]

#using traintest split to generate training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=50)

# Generating the XAI Dashboard
model = RandomForestClassifier(n_estimators=2, max_depth=2).fit(X_train, y_train)

explainer = ClassifierExplainer(model, X_test, y_test, 
                            #    descriptions=feature_descriptions,
                               )
# Get Random Index
index = explainer.random_index()

# Contribution Plot
x = explainer.plot_contributions(index=index)
result = fig(x)
print (result)