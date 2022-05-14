function generateRangeSelector(
    targetElementId,
    targetLowerInputId,
    targetUpperInputId,
    targetDisplayLowerId,
    targetDisplayUpperId,
    min,
    max,
    startLower,
    startUpper,
    callbackLower,
    callbackUpper,
) {
    // Generate a single range selector slider to feed an upper and lower input element.
    // Callbacks accept a function with the new value as a single arg.
    const rangeSelector = document.querySelector('#' + targetElementId);
    const inputLower = document.querySelector("#" + targetLowerInputId)
    const inputUpper = document.querySelector("#" + targetUpperInputId)
    const displayLower = document.querySelector("#" + targetDisplayLowerId)
    const displayUpper = document.querySelector("#" + targetDisplayUpperId)
    let [lower, upper] = [startLower, startUpper]
    displayLower.innerHTML = lower
    displayUpper.innerHTML = upper

    new mdb.MultiRangeSlider(rangeSelector, {
        startValues: [lower, upper],
        min: min,
        max: max,
    });

    rangeSelector.addEventListener('value.mdb.multiRangeSlider', (e) => {
        [lower, upper] = e.values.rounded
        if (lower < min) {
            lower = 0
        }
        if (upper > max) {
            upper = max
        }
        if (upper < lower) {
            upper = lower
        }
        if (lower > upper) {
            lower = upper
        }

        displayLower.innerHTML = lower
        displayUpper.innerHTML = upper
        inputLower.value = lower
        inputUpper.value = upper

        if (callbackLower) {
            callbackLower(lower)
        }
        if (callbackUpper) {
            callbackUpper(upper)
        }
    });
}

function clearChildren(element) {
    for (var i = 0; i < element.childNodes.length; i++) {
        var e = element.childNodes[i];
        if (e.tagName) switch (e.tagName.toLowerCase()) {
            case 'input':
                switch (e.type) {
                    case "radio":
                    case "checkbox":
                        e.checked = false;
                        break;
                    case "button":
                    case "submit":
                    case "image":
                        break;
                    default:
                        e.value = '';
                        break;
                }
                break;
            case 'select':
                e.selectedIndex = 0;
                break;
            case 'textarea':
                e.innerHTML = '';
                break;
            default:
                clearChildren(e);
        }
    }
}


function updatePreviewCard(updateFieldId, value) {
    // Updates an included preview card with the new information provided.
    const standardFields = [
        "search-entity-headline",
        "search-entity-description",
        "search-entity-price-lower",
        "search-entity-price-upper",
        "search-entity-duration-lower",
        "search-entity-duration-upper",
        "search-entity-people-lower",
        "search-entity-people-upper",
    ]

    if (standardFields.includes(updateFieldId)) {
        const target = document.getElementById(updateFieldId)
        target.innerHTML = value
    }

    if (updateFieldId === "filters") {
        // Get all the filter id's
        const all_filters = document.querySelectorAll('[form-field-type="filter"]')
        let filtersHTML = ""
        for (let i = 0; i < all_filters.length; i++) {
            if (all_filters[i].checked) {
                const humanReadable = all_filters[i].getAttribute("human-readable")
                filtersHTML = filtersHTML + `</div><span class=\"badge badge-light mx-1\">${humanReadable}</span>`
            }
        }
        document.getElementById("search-entity-filters").innerHTML = filtersHTML
    }
}