async function copyURL(url) {
    try {
        await navigator.clipboard.writeText(url);
        console.log("URL copied");
    } catch (error) {
        console.error("Copy failed:", error);
    }
}

async function insert() {
    const input2 = document.getElementById("givenURL").value.trim();
    const result = document.getElementById("result");

    const response = await fetch("http://127.0.0.1:8000/shorten", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            original_url: input2
        })
    });

    const data = await response.json();

    if (!response.ok) {
        result.textContent = data.detail || "Something went wrong";
        return;
    }

    result.innerHTML = `
        <a href="${data.short_url}" target="_blank">
            ${data.short_url}
        </a>
        <button onclick="copyURL('${data.short_url}')">Copy</button>`;
}