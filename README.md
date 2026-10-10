# Boni Dash

Boni Dash is a small Streamlit data app built to explore student meal voucher usage across a group of friends during a study exchange in Ljubljana. It brings together transaction data, restaurant patterns, and member comparisons in a simple interactive dashboard that makes the data easy to explore and understand.

## Features

- Welcome page with member selection and profile visualisation
- Personal dashboard with summary stats and monthly spending trends
- Journey view showing daily restaurant activity and voucher usage over time
- Comparison page for benchmarking across members with high-level insights and charts
- Horse Race animation tracking cumulative voucher usage and restaurant visits across participants
- Interactive Plotly and Altair visualisations for exploring patterns in the dataset

## Developer Instructions

### Run locally

1. Clone the repository and open it in VS Code or GitHub Codespaces.
2. Create and activate a Python environment if needed.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the app:

```bash
streamlit run Hello.py
```

5. Open the local Streamlit URL shown in the terminal.

### Streamlit App Owner Quickstart

For the owner of the App, it can be opened directly in GitHub Codespaces from their Streamlit account. For the quickest start find the app in your Streamlit account then click the three dots and select "Edit in Codespaces" to launch the environment. The dev container is configured to install the required Python packages automatically, so the app environment is set up for you without extra manual setup.


### Deploy to Streamlit Community Cloud

Simply reboot the app in your streamlit account to redeploy with latest main. For further instructions on how to first deploy the app check the streamlit docs.

The public demo is available here:

https://boni-dash-4gqq906wpps.streamlit.app/
