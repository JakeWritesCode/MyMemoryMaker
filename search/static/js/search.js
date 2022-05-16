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

function searchFilterButtonOperate(filterName, callback) {
    // Operates the custom toggle buttons for search filters.
    // Will find the accompanying select field and toggle value
    // Then apply style to visible button.
    const valueToggle = ["none", "true", "false", "none"]

    // First, get the accompanying select and the value
    const filterToggle = document.getElementById("filter_" + filterName)
    let currentValue = ""
    let newValue = ""
    for (let i = 0; i < valueToggle.length; i++) {
        if (filterToggle.value === valueToggle[i]) {
            currentValue = valueToggle[i]
            newValue = valueToggle[i + 1]
            break
        }
    }

    // Set the new value in the select
    filterToggle.value = newValue

    // Set the new class in the visible button
    const visibleButton = document.getElementById("search-filter-button-" + filterName)
    visibleButton.classList.remove("search-filter-button-" + currentValue)
    visibleButton.classList.add("search-filter-button-" + newValue)

    // Run the callback if there is one
    if (callback) {
        callback()
    }
}

function parseSearch() {
    // Parses the data from the form into get params for the runSearch function.
    // Returns a dict of get params as k/v pairs.
    let getParams = {}
    const checkboxFields = ["id_event_select", "id_activity_select", "id_place_select"]
    for (let i = 0; i < checkboxFields.length; i++) {
        const field = document.getElementById(checkboxFields[i])
        if (field.checked) {
            getParams[field.name] = true
        }
    }

    const textFields = [
        "id_location_lat",
        "id_location_long",
        "id_distance_lower",
        "id_distance_upper",
        "id_price_lower",
        "id_price_upper",
        "id_people_lower",
        "id_people_upper",
        "id_keywords",
        "id_datetime_from",
        "id_datetime_to",
    ]
    for (let i = 0; i < textFields.length; i++) {
        const field = document.getElementById(textFields[i])
        if (field.value !== "") {
            getParams[field.name] = field.value
        }
    }

    // All the null bool filter buttons with hidden fields attached
    const nullBoolFilters = document.getElementsByClassName("filter-select")
    for (let i = 0; i < nullBoolFilters.length; i++) {
        if (nullBoolFilters[i].value !== "none") {
            getParams[nullBoolFilters[i].name] = nullBoolFilters[i].value
        }
    }

    console.log(getParams)
    return getParams
}

function runSearch() {
    const getParams = parseSearch()
    const resultsTarget = document.getElementById("search-results-target")

    // It's possible the user could have deactivated all filters after activating some.
    // If so, just remove everything from the target div.
    if (Object.keys(getParams).length === 0) {
        resultsTarget.innerHTML = ""
    }

    // Generate the get params
    const searchResultsURLWithGETParams = new URL(searchResultsURL)
    for (let k in getParams) {
        searchResultsURLWithGETParams.searchParams.append(k, getParams[k]);
    }

    // Send a GET request to the search URL and add the returned HTML into the
    // target div, HTMX style.
    fetch(searchResultsURLWithGETParams.href, {
        method: 'GET',
    })
        .then(response => response.text())
        .then(html => {
                // console.log(html);
                resultsTarget.innerHTML = html;
            }
        )
}

class ClassWatcher {

    constructor(targetNode, classToWatch, classAddedCallback, classRemovedCallback) {
        this.targetNode = targetNode
        this.classToWatch = classToWatch
        this.classAddedCallback = classAddedCallback
        this.classRemovedCallback = classRemovedCallback
        this.observer = null
        this.lastClassState = targetNode.classList.contains(this.classToWatch)

        this.init()
    }

    init() {
        this.observer = new MutationObserver(this.mutationCallback)
        this.observe()
    }

    observe() {
        this.observer.observe(this.targetNode, {attributes: true})
    }

    disconnect() {
        this.observer.disconnect()
    }

    mutationCallback = mutationsList => {
        for (let mutation of mutationsList) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                let currentClassState = mutation.target.classList.contains(this.classToWatch)
                if (this.lastClassState !== currentClassState) {
                    this.lastClassState = currentClassState
                    if (currentClassState) {
                        this.classAddedCallback()
                    } else {
                        this.classRemovedCallback()
                    }
                }
            }
        }
    }
}