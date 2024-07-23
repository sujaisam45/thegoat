document.addEventListener('DOMContentLoaded', function() {
    let radioButtons = document.querySelectorAll('input[name="goat-type"]');
    radioButtons.forEach(button => {
        button.addEventListener('change', function() {
            displayTable(this.value);
        });
    });

    let periodButtons = document.querySelectorAll('input[name="feed-period"]');
    periodButtons.forEach(button => {
        button.addEventListener('change', function() {
            document.querySelectorAll('.table-container').forEach(container => {
                container.style.display = 'none';
            });
            let selectedPeriod = document.querySelector('input[name="feed-period"]:checked').value;
            document.querySelector(`.table-container[data-period="${selectedPeriod}"]`).style.display = 'block';
            updateFeedCalculations();
        });
    });

    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('no-of-goats')) {
            updateFeedCalculations();
        }
    });
});

function getDryMatterIntake(weight, type) {
    const types = {
        'Grower': 0.04,
        'Maintain': 0.03,
        'Breeding': 0.036,
        'Lactating': 0.043
    };
    return weight * types[type];
}

function calculateFeed(weight, noOfGoats, period, type) {
    let factor;
    switch (period) {
        case 'per_day':
            factor = 1;
            break;
        case 'per_week':
            factor = 7;
            break;
        case 'per_month':
            factor = 30;
            break;
        default:
            factor = 1;
    }

    let dmi = getDryMatterIntake(weight, type) * noOfGoats * factor;
    let forage = dmi * 0.7 * 5.3;
    let hay = dmi * 0.1;
    let pellet = dmi * 0.2;

    return { forage, hay, pellet };
}

function displayTable(type) {
    let periods = ['per_day', 'per_week', 'per_month'];
    periods.forEach(period => {
        let tableContainer = document.querySelector(`.table-container[data-period="${period}"]`);
        let table = tableContainer.querySelector('tbody');
        table.innerHTML = '';
        let weights = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60'];

        weights.forEach(weight => {
            table.innerHTML += `
                <tr>
                    <td>${weight}</td>
                    <td><input type="number" class="no-of-goats" min="0" value="0" data-weight="${weight}" data-period="${period}" oninput="syncInputs('${weight}')"></td>
                    <td class="forage"></td>
                    <td class="hay"></td>
                    <td class="pellet"></td>
                </tr>
            `;
        });
    });

    updateFeedCalculations();
}

function updateFeedCalculations() {
    let rows = document.querySelectorAll('.table-container tbody tr');
    let type = document.querySelector('input[name="goat-type"]:checked').value;
    let forageTotal = { per_day: 0, per_week: 0, per_month: 0 };
    let hayTotal = { per_day: 0, per_week: 0, per_month: 0 };
    let pelletTotal
