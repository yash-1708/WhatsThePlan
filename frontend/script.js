// --- JavaScript Logic ---
const API_URL = 'http://127.0.0.1:8000/search'; // Change this to your AWS URL when deployed!
const searchForm = document.getElementById('searchForm');
const queryInput = document.getElementById('queryInput');
const searchButton = document.getElementById('searchButton');
const resultsDiv = document.getElementById('results');

searchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    // 1. Set UI State to Loading
    searchButton.disabled = true;
    searchButton.textContent = 'Searching...';
    resultsDiv.innerHTML = '<p class="message">Processing query. Please wait...</p>';

    try {
        // 2. Send request to your FastAPI backend
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
        });

        const data = await response.json();

        if (!response.ok || data.status !== 'success') {
            // Handle API errors (e.g., 500 server error)
            throw new Error(data.detail || 'The search agent failed to return results.');
        }

        // 3. Render Results
        renderEvents(data.events);

    } catch (error) {
        console.error("Fetch Error:", error);
        resultsDiv.innerHTML = `<p class="message" style="color: red;">Error: ${error.message}. Check your console and ensure the backend is running.</p>`;
    } finally {
        // 4. Reset UI State
        searchButton.disabled = false;
        searchButton.textContent = 'Find Events';
    }
});

function renderEvents(events) {
    resultsDiv.innerHTML = '';
    
    if (events.length === 0) {
        resultsDiv.innerHTML = '<p class="message">No events found for that query. Try broadening your terms or checking a different date.</p>';
        return;
    }

    events.forEach(event => {
        const card = document.createElement('div');
        card.className = 'event-card';

        const title = document.createElement('h3');
        title.textContent = event.title;

        const date = document.createElement('p');
        date.innerHTML = `<strong>Date:</strong> ${event.date}`;
        
        const location = document.createElement('p');
        location.innerHTML = `<strong>Location:</strong> ${event.location}`;

        const description = document.createElement('p');
        description.textContent = event.description || 'No detailed description available.';

        const url = document.createElement('a');
        url.href = event.url || '#';
        url.target = '_blank';
        url.textContent = 'View Source/Details →';
        
        card.append(title, date, location, description, url);
        resultsDiv.appendChild(card);
    });
}