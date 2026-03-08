const apiUrl = 'https://f3hmrjp4v5.execute-api.us-east-1.amazonaws.com/prod/api/generate';

document.getElementById('generateBtn').addEventListener('click', async () => {
    const topic = document.getElementById('topic').value.trim();
    const platform = document.getElementById('platform').value;

    if (!topic) {
        alert("Please enter a topic or niche.");
        return;
    }

    const btn = document.getElementById('generateBtn');
    const loading = document.getElementById('loading');
    const responseArea = document.getElementById('responseArea');
    const ideasContent = document.getElementById('ideasContent');
    const textContent = document.getElementById('textContent');

    // UI Reset
    btn.disabled = true;
    btn.textContent = "Generating...";
    loading.classList.remove('hidden');
    responseArea.classList.add('hidden');
    ideasContent.innerHTML = '';
    textContent.innerHTML = '';

    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                platform: platform
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Render ideas
        if (data.ideas && Array.isArray(data.ideas)) {
            data.ideas.forEach((idea, index) => {
                const ideaDiv = document.createElement('div');
                ideaDiv.className = 'idea-card';
                
                const title = document.createElement('div');
                title.className = 'idea-title';
                title.textContent = `${index + 1}. ${idea.title || idea.idea || "Generated Idea"}`;
                
                const reason = document.createElement('div');
                reason.className = 'idea-reason';
                reason.textContent = idea.reason || idea.content || "";
                
                ideaDiv.appendChild(title);
                ideaDiv.appendChild(reason);
                ideasContent.appendChild(ideaDiv);
            });
        }
        
        // Render general content/summary if present
        if (data.content && typeof data.content === 'string') {
            textContent.textContent = data.content;
        } else if (data.response) {
            textContent.textContent = data.response;
        }

        responseArea.classList.remove('hidden');

    } catch (error) {
        console.error("API Call Error:", error);
        alert("Failed to connect to the Creator Engine API. Check the console for CORS or network errors.");
    } finally {
        btn.disabled = false;
        btn.textContent = "Generate AI Ideas";
        loading.classList.add('hidden');
    }
});
