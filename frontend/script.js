const API_URL = '/search'; 
const searchForm = document.getElementById('searchForm');
const queryInput = document.getElementById('queryInput');
const searchButton = document.getElementById('searchButton');
const resultsDiv = document.getElementById('results');

searchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    // Set UI State to Loading
    searchButton.disabled = true;
    searchButton.textContent = 'Searching...';
    resultsDiv.innerHTML = '<p class="message">Processing query. Please wait...</p>';

    try {
        // Send request to your FastAPI backend
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
        });

        const data = await response.json();

        if (!response.ok || data.status !== 'success') {
            throw new Error(data.detail || 'The search agent failed to return results.');
        }

        const events = data.events;
        
        // --- VALIDATION CHECK: Check if the graph stopped early (Validator Agent) ---
        // If the graph stops early due to an 'invalid' query, the backend will return 
        // an empty event list and no search_id (since persistence was skipped).
        if (events.length === 0 && data.search_id === undefined) {
             resultsDiv.innerHTML = '<p class="message" style="color: orange;">Please enter a valid query that specifies both an event type and a location (e.g., "Rock concerts in Chicago next month").</p>';
             return;
        }

        // 3. Render Results
        renderEvents(events);

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