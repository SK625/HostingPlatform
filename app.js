document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('contestantName').value;
    const language = document.getElementById('languageSelect').value;
    const fileInput = document.getElementById('codeFile');
    const terminal = document.getElementById('errorTerminal');

    if (fileInput.files.length === 0) return;

    const formData = new FormData();
    formData.append('name', name);
    formData.append('language', language);
    formData.append('file', fileInput.files[0]);

    terminal.style.color = '#e3b341';
    terminal.innerText = `Compiling and launching sandbox for ${name}... Please wait.`;

    try {
        const response = await fetch('/api/submit', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (result.status === "error") {
            terminal.style.color = '#f85149';
            terminal.style.borderColor = '#f85149';
            terminal.innerText = `[COMPILATION/RUNTIME ERROR]:\n${result.message}`;
        } else {
            terminal.style.color = '#56d364';
            terminal.style.borderColor = '#56d364';
            terminal.innerText = `Success! ${name}'s algorithm passed compilation and is executing under live load.`;
            await fetchLeaderboard();
        }
    } catch (err) {
        terminal.style.color = '#f85149';
        terminal.innerText = `Network Error: Could not connect to the evaluation hub server.`;
    }
});


async function fetchLeaderboard() {
    try {
        const response = await fetch('/api/leaderboard');
        const data = await response.json();
        
        const tbody = document.getElementById('leaderboardBody');
        
        if (data && data.length > 0) {
            tbody.innerHTML = '';

            data.forEach((player, index) => {
                const rank = index + 1;
                const row = document.createElement('tr');
                if (rank === 1) row.classList.add('rank-1');

                row.innerHTML = `
                    <td>${rank === 1 ? '1' : rank}</td>
                    <td><strong>${player.name}</strong></td>
                    <td>${player.accuracy.toFixed(2)}%</td>
                    <td>${player.stability.toFixed(2)}%</td>
                    <td>${player.speed.toLocaleString()} ops/s</td>
                `;
                tbody.appendChild(row);
            });
        }
    } catch (e) {
        console.error("Failed to fetch live standings", e);
    }
}

setInterval(fetchLeaderboard, 1000);

fetchLeaderboard();