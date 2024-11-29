const apiUrl = 'http://localhost:5001/api';

const loadOptions = async (category, elementId) => {
    try {
        const response = await fetch(`${apiUrl}/options/${category}`);
        if (!response.ok) {
            throw new Error(`Error al cargar las opciones de ${category}: ${response.status}`);
        }
        const data = await response.json();
        const selectElement = document.getElementById(elementId);

        selectElement.innerHTML = '<option value="">Select an option</option>';
        data[category].forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            selectElement.appendChild(optionElement);
        });
    } catch (error) {
        console.error(`Error loading ${category} options:`, error);
    }
};

const getRecommendation = async () => {
    const genre = document.getElementById('genre').value;
    const year = document.getElementById('year').value;

    if (!genre || !year) {
        alert('Please select an option for all categories.');
        return;
    }

    try {
        const response = await fetch(`${apiUrl}/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ genres: genre, year })
        });

        if (!response.ok) {
            const errorMessage = `Error al obtener recomendaciones: ${response.status}`;
            console.error(errorMessage);
            document.getElementById('recommendation').textContent = errorMessage;
            return;
        }

        const data = await response.json();

        if (data.error) {
            document.getElementById('recommendation').textContent = `Error: ${data.error}`;
        } else {
            const recommendations = data.recommendations.join(', ');
            document.getElementById('recommendation').textContent = `Recommended Movies: ${recommendations}`;
        }
    } catch (error) {
        console.error('Error getting recommendation:', error);
        document.getElementById('recommendation').textContent = 'An error occurred while fetching the recommendation.';
    }
};

document.addEventListener('DOMContentLoaded', () => {
    loadOptions('genres', 'genre');
    loadOptions('year', 'year');

    document.getElementById('submit').addEventListener('click', getRecommendation);
});
