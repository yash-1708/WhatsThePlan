const API_URL = '/search';
const searchForm = document.getElementById('searchForm');
const queryInput = document.getElementById('queryInput');
const searchButton = document.getElementById('searchButton');
const resultsDiv = document.getElementById('results');
const searchMeta = document.getElementById('searchMeta');
const themeToggle = document.getElementById('themeToggle');

// Theme management
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    } else if (prefersDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Initialize theme on load
initTheme();
themeToggle.addEventListener('click', toggleTheme);

// Main search function
async function performSearch(query) {
    if (!query || !query.trim()) return;

    // Set UI State to Loading
    setLoadingState(true);
    hideSearchMeta();
    resultsDiv.innerHTML = '<p class="message">Searching for events...</p>';

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query.trim() }),
        });

        const data = await response.json();

        // Handle rate limiting
        if (response.status === 429) {
            throw new Error('Rate limit exceeded. Please wait a moment before searching again.');
        }

        if (!response.ok || data.status !== 'success') {
            throw new Error(data.detail || 'The search agent failed to return results.');
        }

        // Check if the query was invalid
        if (data.query_status === 'invalid') {
            resultsDiv.innerHTML = '<p class="message warning">Please enter a valid query that specifies both an event type and a location (e.g., "Rock concerts in Chicago next month").</p>';
            return;
        }

        const events = data.events;

        // Show search metadata
        showSearchMeta(events.length, data.elapsed_time);

        // Render results
        renderEvents(events);

    } catch (error) {
        console.error('Fetch Error:', error);
        resultsDiv.innerHTML = `<p class="message error">Error: ${error.message}</p>`;
        hideSearchMeta();
    } finally {
        setLoadingState(false);
    }
}

// Example query chips - click to run search
document.querySelectorAll('.query-chip').forEach(chip => {
    chip.addEventListener('click', (e) => {
        e.preventDefault();
        const query = chip.getAttribute('data-query');
        queryInput.value = query;
        performSearch(query);
    });
});

// Search form submission
searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    performSearch(queryInput.value);
});

function setLoadingState(isLoading) {
    searchButton.disabled = isLoading;
    if (isLoading) {
        searchButton.classList.add('loading');
    } else {
        searchButton.classList.remove('loading');
    }
}

function showSearchMeta(count, time) {
    const eventText = count === 1 ? 'event' : 'events';
    searchMeta.innerHTML = `Found <strong>${count}</strong> ${eventText} in <strong>${time}s</strong>`;
    searchMeta.classList.remove('hidden');
}

function hideSearchMeta() {
    searchMeta.classList.add('hidden');
}

function getScoreClass(score) {
    if (score === null || score === undefined) return null;
    if (score >= 0.7) return 'score-high';
    if (score >= 0.4) return 'score-medium';
    return 'score-low';
}

function formatScore(score) {
    if (score === null || score === undefined) return null;
    return Math.round(score * 100);
}

function renderEvents(events) {
    resultsDiv.innerHTML = '';

    if (events.length === 0) {
        resultsDiv.innerHTML = '<p class="message">No events found for that query. Try broadening your terms or checking a different date.</p>';
        return;
    }

    events.forEach(event => {
        const card = document.createElement('div');
        card.className = 'event-card';

        // Score badge (if score exists)
        const scoreValue = formatScore(event.score);
        if (scoreValue !== null) {
            const scoreBadge = document.createElement('span');
            scoreBadge.className = `score-badge ${getScoreClass(event.score)}`;
            scoreBadge.textContent = `${scoreValue}%`;
            scoreBadge.title = 'Relevance score';
            card.appendChild(scoreBadge);
        }

        const title = document.createElement('h3');
        title.textContent = event.title;

        const date = document.createElement('p');
        date.innerHTML = `<strong>Date:</strong> ${event.date || 'TBD'}`;

        const location = document.createElement('p');
        location.innerHTML = `<strong>Location:</strong> ${event.location || 'See details'}`;

        const description = document.createElement('p');
        description.className = 'description';
        description.textContent = event.description || 'No detailed description available.';

        const url = document.createElement('a');
        url.href = event.url || '#';
        url.target = '_blank';
        url.rel = 'noopener noreferrer';
        url.textContent = 'View Details →';

        card.append(title, date, location, description, url);
        resultsDiv.appendChild(card);
    });
}
