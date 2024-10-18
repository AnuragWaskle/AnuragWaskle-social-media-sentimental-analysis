async function analyzeSentiment() {
    const query = document.getElementById("query").value;

    if (!query) {
        alert("Please enter a search query.");
        return;
    }

    // Show a loading message while fetching data
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "<p>Loading, please wait...</p>";

    try {
        const response = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: query })
        });

        const data = await response.json();

        if (response.ok) {
            displayResults(data);
        } else {
            alert(data.error || "An error occurred.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to connect to the server.");
    }
}

function displayResults(data) {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "";

    const summaryHtml = `
        <h2>Sentiment Summary</h2>
        <p>Total Comments: ${data.sentiment_summary.total_comments}</p>
        <p>Positive: ${data.sentiment_summary.positive}</p>
        <p>Negative: ${data.sentiment_summary.negative}</p>
        <p>Neutral: ${data.sentiment_summary.neutral}</p>
        <h3>Impact Summary</h3>
        <p>${data.impact_summary}</p>
    `;

    const commentsHtml = `
        <h2>Comments Analyzed</h2>
        <ul>
            ${data.comments.map(comment => `<li>${comment}</li>`).join("")}
        </ul>
    `;

    resultsDiv.innerHTML = summaryHtml + commentsHtml;
}
