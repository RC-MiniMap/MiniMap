document.addEventListener("DOMContentLoaded", () => {
    if(typeof directionSteps === "undefined" || !directionSteps.length) return;

    const container = document.getElementById("directions-card-container");
    let currentIndex = 0;

    function renderSteps(index) {
        container.innerHTML = "";

        if(index >= directionSteps.length) {
            container.innerHTML = `
            <div class="direction-card arrived">
                <h3>You have arrived!</h3>
                </div>
                 `;
                 return;
        }
        
        const stepText = directionSteps[index];

        const card = document.createElement("div");
        card.className = "direction-card active";

        card.innerHTML = `
        <h3>Step ${index + 1}</h3>
        <p>${stepText}</p>
        <button id="next-step-btn">Next</button>
         `;

         container.appendChild(card);

         document.getElementById("next-step-btn").addEventListener("click", () => {
            currentIndex++;
            renderSteps(currentIndex);
         });
    }

    renderSteps(currentIndex);
});