function showFetchPopup() {
    const popup = document.getElementById("fetch-popup");
    popup.classList.add("show");
    setTimeout(() => {
        popup.classList.remove("show");
    }, 1000);
    console.log("Prices fetched and updated.");
}

async function fetchPrices() {
    await _fetchPrices();
    updateLastUpdated();
    showFetchPopup();
}

function calculateManualProfit() {
    const buyG = parseInt(document.getElementById("manual-buy-g").value) || 0;
    const buyS = parseInt(document.getElementById("manual-buy-s").value) || 0;
    const buyC = parseInt(document.getElementById("manual-buy-c").value) || 0;
    const sellG = parseInt(document.getElementById("manual-sell-g").value) || 0;
    const sellS = parseInt(document.getElementById("manual-sell-s").value) || 0;
    const sellC = parseInt(document.getElementById("manual-sell-c").value) || 0;

    console.log(
        `Calculating profit: Buy - ${buyG}g ${buyS}s ${buyC}c, Sell - ${sellG}g ${sellS}s ${sellC}c`
    );

    // Convert to copper
    const buyTotal = buyG * 10000 + buyS * 100 + buyC;
    const sellTotal = sellG * 10000 + sellS * 100 + sellC;

    // GW2 TP takes 15% fee from sell price
    const sellAfterTax = Math.floor(sellTotal * 0.85);

    const profit = sellAfterTax - buyTotal;
    console.log(`Profit calculated: ${profit} copper`);

    let profitG, profitS, profitC;
    if (profit < 0) {
        profitG = Math.floor((-1 * profit) / 10000);
        profitS = Math.floor(((-1 * profit) % 10000) / 100);
        profitC = (-1 * profit) % 100;
    } else {
        profitG = Math.floor(profit / 10000);
        profitS = Math.floor((profit % 10000) / 100);
        profitC = profit % 100;
    }

    let resultText;
    let color;
    if (profit >= 0) {
        resultText = `Profit: ${profitG}g ${profitS}s ${profitC}c`;
        color = "#FFD700"; // gold-ish
    } else {
        resultText = `Loss: ${Math.abs(profitG)}g ${Math.abs(
            profitS
        )}s ${Math.abs(profitC)}c`;
        color = "#f44336"; // red
    }
    const resultElem = document.getElementById("manual-profit-result");
    resultElem.innerText = resultText;
    resultElem.style.color = color;
}

function updateLastUpdated() {
    const span = document.getElementById("last-updated");
    const now = new Date();
    span.dataset.timestamp = now.getTime();
    span.innerText = "Just now";
    if (window.lastUpdatedInterval) clearInterval(window.lastUpdatedInterval);
    window.lastUpdatedInterval = setInterval(() => {
        const ts = parseInt(span.dataset.timestamp, 10);
        const diff = Math.floor((Date.now() - ts) / 1000);
        let text = "";
        if (diff < 60) text = `${diff} seconds ago`;
        else if (diff < 3600) text = `${Math.floor(diff / 60)} minutes ago`;
        else text = `${Math.floor(diff / 3600)} hours ago`;
        span.innerText = text;
    }, 1000);
}
