# Setup Folders, Tokens, and Dependencies
from dash import  html, register_page
import dash_bootstrap_components as dbc

# Initialize Page
register_page(__name__, path='/', name='Start', title='Klima Insights')

layout = dbc.Container(className='d-flex justify-content-center align-items-center full-height full-width py-5 z-3', fluid=True, children=[
  html.Div(className='card', children=[
    html.Strong(className="text-primary", children=["Are You Ready to Uncover the Truth about Climate Change in the Philippines?"]),
    html.Div(className='card__body', children=[
          html.P(
                "Delve into the heart of environmental change with Klima Insights. Our dynamic dashboard presents "
                "a comprehensive overview of the climate's impact on the Philippines, revealing temperature increase over the decades, "
                "biodiversity shifts, and the frequency of disasters."
          ),
          html.P(
              "Do you know how climate change is reshaping the Philippines? Join us as we uncover the hidden patterns, "
              "discover the amount of endangered species struggling to survive, and witness the escalating disasters "
              "threatening our communities. The time to act is now. Together, let's shape a sustainable future for generations to come."
          ),
          html.Div(className="container-fluid d-flex justify-content-center scale-button",children=[
                dbc.Button("Explore Climate History", color="info", href="/temperature", className="mt-3")
          ])
    ]),
    html.Span(children=[
      html.Div(className="container-fluid d-flex justify-content-center",children=[
                dbc.Button("Explore Climate History", color="info", href="/temperature", className="mt-3")
          ])
    ])
  ])
])