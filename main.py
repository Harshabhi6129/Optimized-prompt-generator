st.markdown(
    """
    <style>
    /* Ensure the entire page fits within the viewport and prevent scrolling */
    html, body {
        height: 100vh;
        margin: 0;
        padding: 0;
        overflow: hidden; /* Disable page scrolling */
    }
    [data-testid="stAppViewContainer"] {
        padding: 0;
        margin: 0;
        width: 100%;
        height: 100vh; /* Full height of the viewport */
        display: flex;
        flex-direction: column; /* Stack components vertically */
    }
    /* Layout for the horizontal block (two columns) */
    div[data-testid="stHorizontalBlock"] {
        margin: 0;
        padding: 0;
        width: 100%;
        height: calc(100vh - 80px); /* Subtract height for header, if any */
        display: flex; /* Arrange columns horizontally */
        flex-direction: row; /* Side-by-side layout */
    }
    /* Styling for individual columns */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1),
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
        flex: 1; /* Ensure equal width for both columns */
        height: 100%; /* Full height of the parent container */
        overflow-y: auto; /* Enable independent vertical scrolling */
        padding: 10px;
        box-sizing: border-box;
        border: 1px solid #ccc;
        border-radius: 10px;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)
